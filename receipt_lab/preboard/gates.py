"""Fail-closed completion gates: engineering runs never pass accuracy gates."""
import json
from collections import Counter

from .common import REPO, WORK, digest, read_json, utc, write_json
from .dataset import MANIFEST, validate, fingerprints


def has_aggregate(folder,manifest):
    path=folder/'aggregate.json'
    if not path.exists():return False
    report=read_json(path)
    if report.get('manifest_sha256')!=digest(folder/'manifest.json') or report.get('completion_sha256')!=digest(folder/'completion.json') or report.get('aggregator_sha256')!=digest(REPO/'receipt_lab/preboard/aggregate.py'):
        return False
    paths=list((folder/'attempts').glob('*.json'))
    return len(paths)==manifest['expected_attempts'] and Counter(digest(p) for p in paths)==Counter(r['raw_evidence_sha256'] for r in report.get('documents',[]))


def build_report():
    data=read_json(MANIFEST)
    approved=[r for r in data['records'] if r['annotation_status']=='adjudicated']
    errors=validate(data)
    groups={r['transaction_group_id'] for r in approved if r['transaction_group_id']}
    stores={r['store'] for r in approved}
    part1=not errors and len(groups)>=6 and len(stores)>=2
    scored_ocr=[];scored_fields=[];scored_llm=[];scored_challenge=[]
    for manifest in (WORK/'runs').glob('*/manifest.json'):
        m=read_json(manifest)
        complete=manifest.parent/'completion.json'
        if not complete.exists():continue
        c=read_json(complete)
        snapshot=m.get('dataset_snapshot')
        if not snapshot:continue
        current=[r for r in data['records'] if r['doc_id'] in snapshot]
        if fingerprints(current)!=snapshot:continue
        if m.get('purpose') in {'scored_ocr_evaluation','scored_ocr_fields_with_fixed_extractor','scored_final_pipeline_challenge','scored_evaluation'} and not has_aggregate(manifest.parent,m):continue
        if m.get('purpose')=='scored_ocr_evaluation' and m.get('split')=='evaluation' and set(m.get('engines',[]))=={'easyocr','tesseract'} and set(m.get('modes',[]))=={'reference','predicted'} and m.get('repetitions',0)>=3 and c.get('complete') and c.get('accuracy_scored'):
            scored_ocr.append(str(manifest.parent))
        if m.get('purpose')=='scored_ocr_fields_with_fixed_extractor' and m.get('split')=='evaluation' and set(m.get('modes',[]))=={'reference','predicted'} and m.get('repetitions',0)>=3 and c.get('complete') and c.get('accuracy_scored') and (WORK/'selection.json').exists() and m.get('selection_sha256')==digest(WORK/'selection.json'):
            scored_fields.append(str(manifest.parent))
        if m.get('purpose')=='scored_final_pipeline_challenge' and c.get('complete') and (WORK/'selection.json').exists() and m.get('selection_sha256')==digest(WORK/'selection.json'):
            expected=m.get('expected_attempts',0)
            attempts=[read_json(p) for p in (manifest.parent/'attempts').glob('*.json')]
            keys=[(a.get('doc_id'),a.get('repetition')) for a in attempts]
            expected_keys={(doc,rep) for doc in snapshot for rep in range(3)}
            if expected>=18 and len(attempts)==expected==len(expected_keys) and set(keys)==expected_keys and all(a.get('runtime_reused') is True and a.get('measurement',{}).get('sampled_peak_rss_bytes',0)>0 and a.get('fields') is not None for a in attempts):
                scored_challenge.append(str(manifest.parent))
        if m.get('purpose')=='scored_evaluation' and c.get('complete') and c.get('accuracy_scored',0)==m.get('expected_attempts'):
            matrix=m['matrix']
            if len(matrix['models'])==4 and len(matrix['sources'])==2 and set(matrix['grammar'])=={True,False} and matrix['repetitions']>=3:
                if m.get('split')=='evaluation' and (WORK/'selection.json').exists() and m.get('selection_sha256')==digest(WORK/'selection.json'):
                    chosen=read_json(WORK/'selection.json')
                    if set(matrix['sources'])=={'reference',chosen['engine']}:
                        scored_llm.append(str(manifest.parent))
    delivery=WORK/'runs/delivery-integration/evidence.json'
    demo_ok=False
    if delivery.exists():
        d=read_json(delivery)
        flags=['broker_stopped_delivery_failed','repeat_confirmation_same_event','restart_no_pending_event','invalid_schema_blocked']
        traces=d.get('real_photo_traces',[])
        demo_ok=all(d.get(f) is True for f in flags) and len({t['doc_id'] for t in traces})>=3 and all(len(t['ha_entities'])==2 for t in traces)
    challenges=[r for r in approved if r.get('challenge_candidate') and r['split']=='challenge' and r.get('capture_conditions_status')=='owner_confirmed']
    challenge_groups={r['transaction_group_id'] for r in challenges}
    benchmark_ok=part1 and len(challenges)>=6 and len(challenge_groups)>=3 and bool(scored_llm) and bool(scored_challenge)
    results={'timestamp':utc(),'overall_complete':False,'gates':[
        {'part':1,'status':'PASS_IMPLEMENTATION' if part1 else 'WAITING_HUMAN','reviewed_photos':len(approved),'reviewed_transactions':len(groups),
         'remaining':'Owner full transcription, blind second entry, adjudication, grouping and splits' if not part1 else None,'structural_errors':errors},
        {'part':2,'status':'PASS_IMPLEMENTATION' if part1 and scored_ocr and scored_fields else 'IN_PROGRESS','evidence':scored_ocr,'field_evidence':scored_fields,
         'remaining':'Run paired scored OCR benchmark after checked truth; engineering OCR exists but has no accuracy denominator'},
        {'part':3,'status':'PASS_IMPLEMENTATION' if part1 and scored_llm else 'IN_PROGRESS','evidence':scored_llm,
         'remaining':'Run 16 conditions per document from reference and OCR; current 24 attempts are engineering only'},
        {'part':4,'status':'PASS_IMPLEMENTATION' if demo_ok else 'IN_PROGRESS','evidence':str(delivery) if delivery.exists() else None,
         'note':'Engineering demo confirmations are automated and do not count as human ground truth or user study'},
        {'part':5,'status':'PASS_IMPLEMENTATION' if benchmark_ok else 'WAITING_DATA','reviewed_new_photos':len(challenges),'reviewed_new_transactions':len(challenge_groups),
         'remaining':'Six new real photos / three new transactions, checked truths, frozen config and final benchmark'}]}
    results['overall_complete']=all(r['status']=='PASS_IMPLEMENTATION' for r in results['gates'])
    return results


def main():
    results=build_report()
    write_json(REPO/'reports/preboard/completion_gates.json',results)
    print(json.dumps(results,ensure_ascii=False,indent=2))
    if not results['overall_complete']:
        raise SystemExit(2)


if __name__=='__main__':main()
