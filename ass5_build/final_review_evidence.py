"""Recalculate delivery metrics from raw evidence without the production scorers."""
import hashlib
import itertools
import json
import math
import re
import statistics
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RUNS=Path.home()/'SeminarLab/preboard/runs'
REPORTS=ROOT/'reports/preboard'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def normalized(value):
    value=re.sub(r'\[cite:\s*\d+\s*\]','',value,flags=re.I)
    return '\n'.join(' '.join(line.split()) for line in unicodedata.normalize('NFC',value).replace('\r\n','\n').splitlines()).strip()
def distance(a,b):
    if len(a)<len(b):a,b=b,a
    row=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        new=[i]
        for j,y in enumerate(b,1):new.append(min(new[-1]+1,row[j]+1,row[j-1]+(x!=y)))
        row=new
    return row[-1]
def unique_object(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('duplicate key')
        result[key]=value
    return result
def reject_constant(value):raise ValueError('nonfinite number')
def shape_valid(value):
    def number(x):return x is None or type(x) in (int,float) and math.isfinite(x)
    def string(x):return x is None or isinstance(x,str)
    if not isinstance(value,dict) or set(value)!={'transaction_date','merchant','items','grand_total','currency'}:return False
    if not all(string(value[k]) for k in ['transaction_date','merchant','currency']) or not number(value['grand_total']) or not isinstance(value['items'],list):return False
    return all(isinstance(x,dict) and set(x)=={'name','quantity','unit','unit_price','line_total'} and all(string(x[k]) for k in ['name','unit']) and all(number(x[k]) for k in ['quantity','unit_price','line_total']) for x in value['items'])

def main():
    ocr=read(REPORTS/'single_pass_ocr.json')
    snapshot_path=RUNS/'single-pass-owner-v4/snapshot.json'
    assert sha(snapshot_path)==ocr['snapshot_sha256']
    snapshot=read(snapshot_path)
    rows={r['doc_id']:r for r in snapshot['records']}
    selected=[r for r in ocr['documents'] if not r['exclusion_reasons']]
    assert len(rows)==59 and len(selected)==24 and ocr['excluded_photos']==35
    totals={engine:{'edits':0,'characters':0} for engine in ['easyocr','tesseract']}
    for item in selected:
        source=rows[item['doc_id']];ref=normalized(source['entry']['transcript'])
        for engine in totals:
            hyp=normalized(source['predictions'][engine]['text'])
            edits=distance(ref,hyp);assert edits==item['metrics'][engine]['edit_distance']
            totals[engine]['edits']+=edits;totals[engine]['characters']+=len(ref)
    for engine,t in totals.items():
        t['micro_cer']=t['edits']/t['characters']
        assert t['characters']==28011 and math.isclose(t['micro_cer'],ocr['summaries']['all_eligible'][engine]['micro_cer'],abs_tol=1e-12)
    print('Independent OCR arithmetic passed',flush=True)
    llm=read(REPORTS/'single_pass_llm.json');folder=RUNS/'single-pass-llm-v2'
    manifest=read(folder/'manifest.json');raw=[read(p) for p in (folder/'attempts').glob('*.json')]
    expected={f"{s['doc_id']}-{s['source_kind']}-{model}-{'grammar' if grammar else 'free'}-r{rep}" for s,model,grammar,rep in itertools.product(manifest['samples'],manifest['models'],[False,True],range(3))}
    assert len(raw)==288 and {r['attempt_key'] for r in raw}==expected
    for r in raw:
        assert r['raw_response']['choices'][0]['message']['content']==r['raw_content']
        try:
            parsed=json.loads(r['raw_content'],object_pairs_hook=unique_object,parse_constant=reject_constant)
            valid=True
        except (ValueError,TypeError):parsed=None;valid=False
        assert valid==r['parse_valid']
        assert (valid and shape_valid(parsed))==r['schema_valid']
    for g in llm['groups']:
        group=[r for r in raw if (r['model']['id'],r['source_kind'],r['grammar'])==(g['model'],g['source'],g['grammar'])]
        assert len(group)==18 and len({r['doc_id'] for r in group})==6
        assert sum(r['schema_valid'] for r in group)==g['schema_valid'] and sum(r['parse_valid'] for r in group)==g['parse_valid']
        assert statistics.median(r['measurement']['wall_seconds'] for r in group)==g['median_seconds']
    print('Independent raw LLM parse/schema and 16 groups passed',flush=True)
    pc=read(REPORTS/'pc_transport_profile.json');folder=RUNS/pc['run_id']
    trials=[read(folder/name) for name in pc['raw_evidence_sha256']]
    assert len(trials)==9 and len({r['doc_id'] for r in trials})==3 and all(r['status']=='ok' and not r['warmup'] for r in trials)
    for name in ['automated_window_to_ha_observed_seconds','publish_to_ha_observed_seconds']:
        values=[r[name] for r in trials];s=pc['summaries'][name]
        assert (min(values),statistics.median(values),max(values))==(s['min'],s['median'],s['max'])
    for r in trials:
        assert len(r['ha_states'])==2 and all(s['attributes']['event_id']==r['event_id'] for s in r['ha_states'])
        assert r['ha_value_checks'] and r['human_confirmation_time'] is None
    result={'status':'pass','reviewed_at':datetime.now(timezone.utc).isoformat(),'method':'Independent edit-distance, strict JSON structure, group arithmetic and PC median calculations from raw evidence; no new model inference',
            'ocr':totals,'llm_attempts':len(raw),'llm_groups':len(llm['groups']),'llm_status_counts':dict(Counter(r['status'] for r in raw)),
            'pc_attempts':len(trials),'pc_failures':0,'semantic_accuracy':None,
            'source_reports':{name:sha(REPORTS/name) for name in ['single_pass_ocr.json','single_pass_llm.json','pc_transport_profile.json']},
            'reviewer_script_sha256':sha(Path(__file__))}
    (REPORTS/'final_review_recalculation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PC arithmetic and event IDs passed; final review evidence saved')

if __name__=='__main__':main()
