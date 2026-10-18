"""Verify immutable run evidence and describe termination states without repairing outputs."""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from receipt_lab.preboard.common import read_json,write_json,digest,utc
from receipt_lab.preboard.evidence_checks import check_llm,check_pc,matching_run

def main():
    reports=ROOT/'reports/preboard'
    llm=read_json(reports/'single_pass_llm.json'); pc=read_json(reports/'pc_transport_profile.json')
    assert llm['complete'] and llm['attempts']==288 and check_llm(llm)
    assert pc['run_id']=='pc-delivery-profile-engineering-v3' and pc['attempts']==9 and pc['failures']==0 and check_pc(pc)
    folder=matching_run(llm)
    rows=[read_json(p) for p in (folder/'attempts').glob('*.json')]
    assert all(m['missing']==0 and m['samples']==9 for s in pc['stage_summaries'].values() for m in s.values())
    result={'timestamp':utc(),'status':'pass','llm_attempts':len(rows),
            'llm_status_counts':dict(Counter(r['status'] for r in rows)),
            'finish_reason_counts':dict(Counter(str(r.get('finish_reason')) for r in rows)),
            'grammar_truncated':sum(r['grammar'] and r['status']=='truncated' for r in rows),
            'parse_valid':sum(r['parse_valid'] for r in rows),'schema_valid':sum(r['schema_valid'] for r in rows),
            'output_limits':dict(Counter(str(r['request']['max_tokens']) for r in rows)),
            'pc_attempts':pc['attempts'],'pc_failures':pc['failures'],'stage_measurements_complete':True,
            'raw_evidence_verified':True,'semantic_accuracy':None,
            'note':'Parse/schema counts describe raw returned content; truncated/request-failed attempts remain in every denominator. No output repair.',
            'legacy_field_note':'single_pass_llm.groups.request_failures counts every non-ok status, including truncated. Use the explicit status counts here to distinguish HTTP/request failures from output-limit termination.',
            'group_status_counts':[{**{k:g[k] for k in ['model','source','grammar']},
                                    'statuses':dict(Counter(r['status'] for r in rows if r['model']['id']==g['model'] and r['source_kind']==g['source'] and r['grammar']==g['grammar']))}
                                   for g in llm['groups']],
            'source_report_sha256':{n:digest(reports/n) for n in ['single_pass_llm.json','pc_transport_profile.json']}}
    write_json(reports/'completed_run_audit.json',result)
    print(json.dumps({k:result[k] for k in ['status','llm_attempts','llm_status_counts','pc_attempts','pc_failures']},ensure_ascii=False))

if __name__=='__main__':main()
