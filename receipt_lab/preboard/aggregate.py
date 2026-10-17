"""Reproduce tables from completed, checked runs without exposing receipt text."""
import argparse
import csv
import math
import statistics
from collections import defaultdict
from decimal import Decimal, localcontext
from pathlib import Path
from itertools import product

from .common import REPO, WORK, digest, read_json, utc, write_json
from .dataset import MANIFEST, fingerprints, validate
from .metrics import summarize as summarize_cer

PURPOSES={'scored_ocr_evaluation','scored_evaluation','scored_ocr_fields_with_fixed_extractor','scored_final_pipeline_challenge'}


def distribution(values):
    values=[v for v in values if v is not None]
    return {'samples':len(values),'median':statistics.median(values) if values else None,
            'min':min(values) if values else None,'max':max(values) if values else None,
            'p95':statistics.quantiles(values,n=100,method='inclusive')[94] if len(values)>1 else values[0] if values else None}


def fields_summary(rows):
    counts={};errors=defaultdict(list);missing=extra=0
    for row in rows:
        fields=row.get('fields')
        if fields is None:raise ValueError('Missing field-metric evidence; do not omit this document')
        missing+=fields['missing_items'];extra+=fields['extra_unmatched_items']
        for key,value in fields['counts'].items():
            dest=counts.setdefault(key,{'correct':0,'defined_reference':0})
            for name in dest:dest[name]+=value[name]
        for error in fields['numeric_absolute_errors_on_present_matched_fields']:
            value=error.get('absolute_error_decimal',error.get('absolute_error'))
            if value is None:raise ValueError('Monetary error lost its numeric evidence')
            errors[error['field']].append(Decimal(str(value)))
    for value in counts.values():value['accuracy']=value['correct']/value['defined_reference'] if value['defined_reference'] else None
    money={}
    for key in ['grand_total','items.unit_price','items.line_total']:
        values=errors[key]
        with localcontext() as context:
            context.prec=max(28,max((abs(v.adjusted())+len(v.as_tuple().digits)+10 for v in values),default=28))
            mae=sum(values)/len(values) if values else None
        approximate=float(mae) if mae is not None else None
        denominator=counts.get(key,{}).get('defined_reference',0)
        money[key]={'matched_present_samples':len(values),'defined_reference_fields':denominator,
                    'coverage':len(values)/denominator if denominator else None,
                    'mae':approximate if approximate is not None and math.isfinite(approximate) else None,
                    'mae_decimal':str(mae) if mae is not None else None,
                    'mae_outside_float_range':approximate is not None and not math.isfinite(approximate)}
    return {'field_accuracy':counts,'missing_items':missing,'extra_unmatched_items':extra,'money':money,
            'money_denominator':'MAE uses only present matched numeric predictions; missing/invalid values remain field failures, never zero errors'}


def condition(row,purpose):
    if purpose=='scored_ocr_evaluation':return row['engine']+' / '+row['mode']
    if purpose=='scored_ocr_fields_with_fixed_extractor':return row['engine']+' / '+row['mode']+' / fixed extractor / grammar on'
    if purpose=='scored_evaluation':return row['model']['id']+' / '+row['source_kind']+' / '+('grammar' if row['grammar'] else 'free')
    return 'frozen end-to-end PC pipeline'


def failed(row,purpose):
    if purpose=='scored_final_pipeline_challenge':return not row['successful_processing']
    request_failed=row.get('status')!='ok' or row.get('upstream_status','ok')!='ok'
    return request_failed if purpose=='scored_ocr_evaluation' else request_failed or not row['parse_valid'] or not row['schema_valid']


def measurement(row):
    return row.get('measurement',row)


def check_attempts(rows,manifest):
    purpose=manifest['purpose'];docs=manifest['dataset_snapshot']
    if purpose=='scored_ocr_evaluation':
        expected=set(product(docs,manifest['engines'],manifest['modes'],range(manifest['repetitions'])))
        actual=[(r['doc_id'],r['engine'],r['mode'],r['repetition']) for r in rows]
    elif purpose=='scored_evaluation':
        matrix=manifest['matrix']
        expected=set(product(docs,matrix['models'],matrix['sources'],matrix['grammar'],range(matrix['repetitions'])))
        actual=[(r['doc_id'],r['model']['id'],r['source_kind'],r['grammar'],r['repetition']) for r in rows]
    elif purpose=='scored_ocr_fields_with_fixed_extractor':
        expected=set(product(docs,manifest['engines'],manifest['modes'],range(manifest['repetitions'])))
        actual=[(r['doc_id'],r['engine'],r['mode'],r['repetition']) for r in rows]
    else:
        expected=set(product(docs,range(3)))
        actual=[(r['doc_id'],r['repetition']) for r in rows]
        if any(r.get('runtime_reused') is not True or r.get('configuration',{}).get('selection_sha256')!=manifest['selection_sha256'] for r in rows):
            raise ValueError('Final pipeline rows do not match the frozen warm runtime')
    if len(actual)!=len(expected) or set(actual)!=expected:
        raise ValueError('Missing, duplicate or unexpected condition/document/repetition')


def summarize_condition(rows,purpose):
    primary=[r for r in rows if r.get('repetition',0)==0]
    if not primary:raise ValueError('Missing repetition zero for accuracy')
    docs=[r['doc_id'] for r in primary]
    if len(docs)!=len(set(docs)):raise ValueError('Repeated documents would inflate the accuracy denominator')
    seconds=[measurement(r).get('wall_seconds') for r in rows]
    memory=defaultdict(list)
    for r in rows:
        m=measurement(r)
        if m.get('sampled_peak_rss_bytes') is not None:memory[m.get('memory_metric','sampled Windows process-tree RSS')].append(m['sampled_peak_rss_bytes'])
        if m.get('child_peak_rss_bytes') is not None:memory[m.get('memory_metric','Linux child peak RSS')].append(m['child_peak_rss_bytes'])
    result={'documents':len(primary),'transaction_groups':len({r['transaction_group_id'] for r in primary}),
            'attempts':len(rows),'failed_attempts':sum(failed(r,purpose) for r in rows),
            'primary_failed_documents':sum(failed(r,purpose) for r in primary),
            'wall_seconds_all_attempts':distribution(seconds),'missing_time_measurements':sum(v is None for v in seconds),
            'missing_memory_measurements':sum(measurement(r).get('sampled_peak_rss_bytes') is None and measurement(r).get('child_peak_rss_bytes') is None for r in rows),
            'memory_bytes_by_metric':{k:distribution(v) for k,v in memory.items()}}
    if purpose=='scored_ocr_evaluation':
        result['cer']=summarize_cer([r['metric'] for r in primary])
    else:
        result['raw_parse_valid_rate']=sum(bool(r['parse_valid']) for r in primary)/len(primary)
        result['raw_schema_valid_rate']=sum(bool(r['schema_valid']) for r in primary)/len(primary)
        for key in ['precision','recall','f1','exact_match']:
            values=[r['score'][key] for r in primary if r['score'][key] is not None]
            result['macro_document_'+key]=statistics.mean(values) if values else None
            result[key+'_scorable_documents']=len(values)
        result.update(fields_summary(primary))
    stages=defaultdict(list)
    for row in rows:
        for name,value in row.get('stage_measurements',{}).items():
            if value is not None:stages[name].append(value)
    if stages:
        result['stages']={name:{'wall_seconds':distribution([v.get('wall_seconds') for v in values]),
                               'sampled_rss_bytes':distribution([v.get('sampled_peak_rss_bytes') for v in values]),
                               'linux_child_rss_bytes':distribution([v.get('child_peak_rss_bytes') for v in values])} for name,values in stages.items()}
    return result


def aggregate(folder,publish=False):
    folder=Path(folder)
    manifest=read_json(folder/'manifest.json');completion=read_json(folder/'completion.json')
    purpose=manifest['purpose']
    if purpose not in PURPOSES or not completion.get('complete'):raise ValueError('Only complete scored runs can produce accuracy tables')
    snapshot=manifest.get('dataset_snapshot')
    if not snapshot:raise ValueError('Missing checked dataset snapshot')
    data=read_json(MANIFEST)
    records=[r for r in data['records'] if r['doc_id'] in snapshot]
    errors=validate({**data,'records':records},require_review=True)
    if errors:raise ValueError('Unchecked input records: '+'; '.join(errors))
    if fingerprints(records)!=snapshot:raise ValueError('Dataset/truth changed after this run')
    if purpose!='scored_ocr_evaluation' and manifest.get('scorer_sha256')!=digest(REPO/'json_extraction_scorer.py'):
        raise ValueError('Scorer changed; use a separately versioned analysis instead of mixing protocols')
    if manifest.get('selection_sha256') and (not (WORK/'selection.json').exists() or manifest['selection_sha256']!=digest(WORK/'selection.json')):
        raise ValueError('Frozen selection changed')
    paths=sorted((folder/'attempts').glob('*.json'))
    if len(paths)!=manifest['expected_attempts']:raise ValueError('Attempt count differs from the manifest')
    attempts=[read_json(path) for path in paths]
    check_attempts(attempts,manifest)
    metadata={r['doc_id']:r for r in records};groups=defaultdict(list);documents=[]
    for path,row in zip(paths,attempts):
        row['transaction_group_id']=metadata[row['doc_id']]['transaction_group_id']
        key=condition(row,purpose);groups[key].append(row)
        score=row.get('score',{})
        documents.append({'doc_id':row['doc_id'],'transaction_group_id':row['transaction_group_id'],'condition':key,
                          'repetition':row.get('repetition',0),'accuracy_included':row.get('repetition',0)==0,
                          'status':row['status'],'failed':failed(row,purpose),'cer':row.get('metric',{}).get('cer'),
                          **{k:score.get(k) for k in ['precision','recall','f1','exact_match']},
                          'wall_seconds':measurement(row).get('wall_seconds'),
                          'sampled_peak_rss_bytes':measurement(row).get('sampled_peak_rss_bytes'),
                          'linux_child_peak_rss_bytes':measurement(row).get('child_peak_rss_bytes'),
                          'raw_evidence_sha256':digest(path)})
    report={'timestamp':utc(),'run_id':folder.name,'purpose':purpose,'split':manifest.get('split','challenge'),'device':'PC CPU',
            'timing_scope':manifest.get('timing_scope','Per-attempt tool measurement; full pipeline measured separately'),
            'environment':{k:v for k,v in manifest.get('environment',{}).items() if k not in {'lab_root','executable'}},
            'aggregator_sha256':digest(Path(__file__)),
            'manifest_sha256':digest(folder/'manifest.json'),'completion_sha256':digest(folder/'completion.json'),
            'dataset_snapshot':snapshot,'accuracy_repetition':0,
            'uncertainty':'Descriptive statistics only; repetitions are timing samples, not independent transactions. Interpolated p95 may be unstable in small samples.',
            'conditions':{key:summarize_condition(rows,purpose) for key,rows in sorted(groups.items())},'documents':documents}
    loads=[]
    for path in sorted(set(folder.glob('load-*.json'))|set(folder.glob('runtime-load.json'))|set(folder.glob('sessions/*/load-*.json'))):
        item=read_json(path);m=item.get('measurement',item) or {}
        loads.append({'artifact':str(path.relative_to(folder)),'raw_sha256':digest(path),
                      'measurement':{key:m[key] for key in ['wall_seconds','load_wall_seconds','sampled_peak_rss_bytes','memory_metric'] if key in m}})
    report['cold_loads']=loads
    write_json(folder/'aggregate.json',report)
    csvpath=folder/'aggregate.csv'
    with csvpath.open('w',newline='',encoding='utf-8-sig') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(documents[0]));writer.writeheader();writer.writerows(documents)
    if publish:
        import shutil
        output=REPO/'reports/preboard/scored';output.mkdir(parents=True,exist_ok=True)
        write_json(output/(folder.name+'.json'),report)
        shutil.copy2(csvpath,output/(folder.name+'.csv'))
        lines=['# '+folder.name,'','Scored data only. Accuracy uses repetition 0; timing uses all retained attempts. Repetitions are not independent transactions.','',
               '| Condition | Photos / transactions | Failures / attempts | Micro CER | Macro field F1 | Median / p95 seconds |',
               '|---|---:|---:|---:|---:|---:|']
        def fmt(value):return 'N/A' if value is None else f'{value:.4f}'
        for key,row in report['conditions'].items():
            timing=row['wall_seconds_all_attempts']
            lines.append(f"| {key} | {row['documents']} / {row['transaction_groups']} | {row['failed_attempts']} / {row['attempts']} | {fmt(row.get('cer',{}).get('micro_cer'))} | {fmt(row.get('macro_document_f1'))} | {fmt(timing['median'])} / {fmt(timing['p95'])} |")
        lines+=['','RAM statistics are in the JSON under `memory_bytes_by_metric`; Windows process RSS and Linux child RSS remain separate. Cold model loads are listed separately. Monetary MAE excludes missing predictions, with coverage shown alongside. Raw receipt text is not included.','',report['uncertainty'],'']
        (output/(folder.name+'.md')).write_text('\n'.join(lines),encoding='utf-8')
    return report


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True);ap.add_argument('--publish',action='store_true');args=ap.parse_args()
    report=aggregate(args.run,args.publish)
    print(report['run_id'],len(report['documents']),'attempts,',len(report['conditions']),'conditions')


if __name__=='__main__':main()
