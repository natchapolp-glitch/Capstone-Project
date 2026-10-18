"""Freeze decisions using development evidence only, before evaluation/challenge."""
import argparse
import statistics
from pathlib import Path

from .common import WORK, digest, read_json, utc, write_json
from .dataset import MANIFEST, fingerprints
from .assets import require_registry


def checked_run(path, purpose):
    path=Path(path)
    manifest=read_json(path/'manifest.json');completion=read_json(path/'completion.json')
    if manifest.get('purpose')!=purpose or manifest.get('split')!='development' or not completion.get('complete'):
        raise ValueError('Selection requires a completed scored development run')
    if manifest.get('asset_registry_sha256')!=require_registry():raise ValueError('Runtime assets changed since development')
    wanted=manifest['dataset_snapshot']
    rows=[r for r in read_json(MANIFEST)['records'] if r['doc_id'] in wanted]
    if fingerprints(rows)!=wanted:
        raise ValueError('Selected development records/truth have changed')
    return path,manifest,completion


def choose_ocr(path):
    path,manifest,completion=checked_run(path,'scored_ocr_evaluation')
    candidates=[]
    for engine in ['easyocr','tesseract']:
        summary=completion['summaries'][engine+'-reference']
        if summary['micro_cer'] is None:
            raise ValueError('Cannot select OCR without non-empty checked references')
        candidates.append((summary['micro_cer'],summary['failures'],engine))
    chosen=sorted(candidates)[0][2]
    result={'engine':chosen,'frozen_at':utc(),'development_run':str(path),
            'asset_registry_sha256':manifest['asset_registry_sha256'],
            'development_evidence_sha256':digest(path/'completion.json'),
            'criterion':'lowest micro CER on reference crops in development; failures retained',
            'candidate_scores':candidates,'dataset_snapshot':manifest['dataset_snapshot']}
    write_json(WORK/'ocr_selection.json',result)
    print(chosen)


def freeze(path):
    if (WORK/'selection.json').exists():
        raise FileExistsError('Selection already frozen; version it explicitly instead of overwriting after evaluation')
    ocr=read_json(WORK/'ocr_selection.json')
    path,manifest,completion=checked_run(path,'scored_evaluation')
    if ocr.get('asset_registry_sha256')!=manifest['asset_registry_sha256'] or manifest['model_registry_sha256']!=digest(WORK/'model_registry.json'):
        raise ValueError('OCR/LLM asset versions differ from the frozen development evidence')
    if ocr['engine'] not in manifest['matrix']['sources']:
        raise ValueError('LLM development run must use the preselected OCR engine')
    attempts=[read_json(p) for p in (path/'attempts').glob('*.json')]
    groups={}
    for a in attempts:
        if a['source_kind']==ocr['engine'] and a['repetition']==0:
            if not a.get('accuracy_scored') or 'score' not in a:
                raise ValueError('Engineering responses cannot select a final model')
            groups.setdefault((a['model']['id'],a['grammar']),[]).append(a)
    if len(groups)!=8:
        raise ValueError('Need all four weights x two decoding modes')
    candidates=[]
    for (model,grammar),rows in groups.items():
        candidates.append({'model_id':model,'grammar':grammar,
            'mean_document_f1':statistics.mean((r['score']['f1'] or 0) for r in rows),
            'schema_valid_rate':statistics.mean(r['schema_valid'] and r['status']=='ok' for r in rows),
            'median_seconds':statistics.median(r['measurement']['wall_seconds'] for r in rows),
            'documents':len(rows)})
    candidates.sort(key=lambda r:(-r['mean_document_f1'],-r['schema_valid_rate'],r['median_seconds'],r['model_id'],not r['grammar']))
    write_json(WORK/'selection.json',{'frozen_at':utc(),'engine':ocr['engine'],**candidates[0],
               'asset_registry_sha256':manifest['asset_registry_sha256'],
               'model_registry_sha256':manifest['model_registry_sha256'],
               'scorer_sha256':manifest['scorer_sha256'],'schema_sha256':manifest['schema_sha256'],
               'llm_driver_sha256':manifest['driver_sha256']['llm.py'],
               'development_evidence_sha256':digest(path/'completion.json'),
               'ocr_selection_sha256':digest(WORK/'ocr_selection.json'),
               'development_run':str(path),'dataset_snapshot':manifest['dataset_snapshot'],
               'criterion':'macro document field F1 on fixed OCR input, schema rate then median time as tiebreakers; repetition zero only',
               'candidates':candidates})
    print(candidates[0]['model_id'],candidates[0]['grammar'])


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('command',choices=['ocr','freeze'])
    ap.add_argument('--run',type=Path,required=True)
    args=ap.parse_args()
    (choose_ocr if args.command=='ocr' else freeze)(args.run)


if __name__=='__main__':main()
