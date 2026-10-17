import uuid
from decimal import Decimal

from receipt_lab.preboard.common import LAB, REPO, WORK, Measurement, digest, read_json, utc, write_json
from receipt_lab.preboard.dataset import MANIFEST
from receipt_lab.preboard.llm import LocalLLM
from receipt_lab.preboard.ocr import OCREngine, prepare_image


class PipelineRuntime:
    """Keep CPU models resident for the separately measured warm pipeline."""
    def __init__(self, model_id=None, engine=None):
        self.configuration=configuration(model_id,engine)
        from ultralytics import YOLO
        with Measurement() as loaded:
            self.detector=YOLO(str(LAB / "yolo_expanded/runs/receipt_region_v8n/weights/best.pt"))
            self.ocr=OCREngine(self.configuration['engine'])
            self.llm=LocalLLM(self.configuration['model_id'])
        self.load={**loaded.result,'ocr_load':self.ocr.load_measurement,'llm_load':self.llm.load}

    def __enter__(self):return self
    def __exit__(self,*args):self.llm.close()


def configuration(model_id=None,engine=None):
    selected = read_json(WORK/'selection.json') if (WORK/'selection.json').exists() else {}
    model_id = model_id or selected.get('model_id', 'qwen3-0.6B-Q4_K_M')
    engine = engine or selected.get('engine','tesseract')
    grammar = selected.get('grammar', True)
    return {'model_id':model_id,'engine':engine,'grammar':grammar,
            'selection_sha256':digest(WORK/'selection.json') if selected else None,
            'status':'frozen_from_development' if selected and model_id==selected['model_id'] and engine==selected['engine'] else 'engineering_default_or_override'}


def amount_warning(extraction):
    from json_extraction_scorer import schema_errors
    if schema_errors(extraction) or not extraction['items'] or extraction['grand_total'] is None or any(i['line_total'] is None for i in extraction['items']):
        return None
    subtotal=sum(Decimal(str(i['line_total'])) for i in extraction['items'])
    if abs(subtotal-Decimal(str(extraction['grand_total'])))>Decimal('0.01'):
        return 'ยอดสุทธิต่างจากผลรวมสินค้า กรุณาตรวจภาษี ส่วนลด และรายการกับภาพก่อนยืนยัน'


def process(doc_id, store, model_id=None, engine=None, rotation="none", runtime=None):
    config=configuration(model_id,engine)
    if runtime is not None and config!=runtime.configuration:
        raise ValueError('Warm runtime configuration differs from the requested/frozen pipeline')
    model_id,engine,grammar=config['model_id'],config['engine'],config['grammar']
    rows = {r["doc_id"]: r for r in read_json(MANIFEST)["records"]}
    row = rows[doc_id]
    if row.get('challenge_candidate') and config['status']!='frozen_from_development':
        raise ValueError('Freeze the development configuration before opening model results on new challenge photos')
    record = {"run_id": str(uuid.uuid4()), "doc_id": doc_id, "timestamp": utc(),
              "source_sha256": row["sha256"], "schema_sha256": digest(REPO / "receipt_schema.json"),
              "device": "PC CPU", "purpose": "engineering demo; no accuracy claim without adjudicated truth"}
    record['configuration'] = config
    record['runtime_reused']=runtime is not None
    with Measurement() as total:
        try:
            from ultralytics import YOLO
            with Measurement() as detection:
                detector = runtime.detector if runtime else YOLO(str(LAB / "yolo_expanded/runs/receipt_region_v8n/weights/best.pt"))
                image, crop = prepare_image(row, "predicted", detector=detector, rotation=rotation)
            record["detection_and_preprocessing"] = {**detection.result, "transform": crop}
            ocr = runtime.ocr if runtime else OCREngine(engine)
            record['ocr_load']={'measurement':ocr.load_measurement,'included_in_request':runtime is None}
            result = ocr.run(image)
            record["ocr"] = result
            if result["status"] != "ok":
                raise RuntimeError("OCR did not complete")
            if runtime:
                record['runtime_load']=runtime.load
                record['llm_load']=runtime.llm.load
                record['llm']=runtime.llm.extract(result['text'],grammar=grammar)
            else:
                with LocalLLM(model_id) as llm:
                    record["llm_load"] = llm.load
                    record["llm"] = llm.extract(result["text"], grammar=grammar)
            record["extraction"] = record["llm"]["parsed_output"]
            record["status"] = "pending_review"
            record["warnings"] = []
            if not record["llm"]["schema_valid"] or record["llm"]["status"] != "ok":
                record["warnings"].append("Model output invalid or incomplete; complete manual correction is required")
            record["warnings"].append("Image rotation was selected by operator; automatic orientation is not implemented")
            warning=amount_warning(record['extraction'])
            if warning:record['warnings'].append(warning)
        except Exception as exc:
            record.update({"status": "processing_failed", "error": str(exc), "extraction": None})
    record["processing_measurement"] = total.result
    record['processing_measurement']['latency_scope']='warm resident models; startup excluded' if runtime else 'request includes model startup; not warm inference'
    record["processing_measurement"]["note"] = "Windows pipeline process tree; Linux Tesseract child memory is recorded separately in OCR result"
    rid = store.add(doc_id, record)
    write_json(WORK / "runs" / record["run_id"] / "pipeline.json", record)
    return rid, record
