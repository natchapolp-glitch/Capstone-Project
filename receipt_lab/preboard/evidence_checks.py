"""Read-only checks that public summaries still refer to intact private evidence."""
from collections import Counter
from .common import WORK, digest, object_hash, read_json
from .dataset import annotations


def matching_run(report, manifest_name='manifest.json', hash_key='manifest_sha256'):
    expected=report.get(hash_key)
    if not expected:
        return None
    return next((p.parent for p in (WORK/'runs').glob('*/'+manifest_name) if digest(p)==expected),None)


def check_llm(report):
    folder=matching_run(report)
    if folder is None:
        return False
    if not (folder/'completion.json').exists() or read_json(folder/'completion.json')!=report:
        return False
    manifest=read_json(folder/'manifest.json')
    evidence=report.get('evidence',[])
    keys=[r['attempt_key'] for r in evidence]
    paths=list((folder/'attempts').glob('*.json'))
    if len(keys)!=len(set(keys)) or len(keys)!=report.get('attempts') or len(paths)!=len(keys):
        return False
    if Counter(digest(p) for p in paths)!=Counter(r['sha256'] for r in evidence):
        return False
    # An added transcript outside the frozen six photos does not invalidate them.
    for s in manifest['samples']:
        first=next((e for e in annotations(s['doc_id']) if e['slot']=='first'),None)
        if first is None or object_hash(first)!=s['reference_entry_sha256']:
            return False
    return True


def check_pc(report):
    folder=matching_run(report)
    if folder is None or not (folder/'summary.json').exists():
        return False
    if digest(folder/'summary.json')!=report.get('private_summary_sha256'):
        return False
    private=read_json(folder/'summary.json')
    public={k:v for k,v in report.items() if k not in {'manifest_sha256','private_summary_sha256'}}
    if private!=public:
        return False
    raw=report.get('raw_evidence_sha256',{})
    if len(raw)!=report.get('attempts') or not raw:
        return False
    return all(_evidence_path(folder,name).exists() and digest(_evidence_path(folder,name))==value for name,value in raw.items())


def _evidence_path(folder,name):
    # Evidence file names are flat and must never escape the matching run.
    if '/' in name or '\\' in name or name in {'.','..'}:
        raise ValueError('Invalid evidence filename')
    return folder/name
