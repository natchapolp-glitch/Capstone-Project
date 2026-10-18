"""WSL sidecar: sample only the verified local experimental service processes."""
import json
import re
import select
import sys
import time
from pathlib import Path

ROOT=Path.home()/'SeminarLab/preboard-services'


def tree_rss(pid,seen=None):
    seen=set() if seen is None else seen
    if pid in seen:return 0
    seen.add(pid)
    try:
        status=Path(f'/proc/{pid}/status').read_text()
        match=re.search(r'^VmRSS:\s+(\d+)\s+kB',status,re.M)
        total=int(match[1])*1024 if match else 0
        children=Path(f'/proc/{pid}/task/{pid}/children').read_text().split()
        return total+sum(tree_rss(int(child),seen) for child in children)
    except (FileNotFoundError,ProcessLookupError):return 0


def main():
    processes={};missing=[]
    for name in ['ha','broker']:
        try:
            pid=int((ROOT/(name+'.pid')).read_text())
            command=Path(f'/proc/{pid}/cmdline').read_bytes()
            if str(ROOT).encode() not in command:raise ValueError('PID does not belong to this experiment')
            processes[name]={'pid':pid,'sampled_peak_rss_bytes':0,'samples':0}
        except (FileNotFoundError,ValueError):missing.append(name)
    print(json.dumps({'ready':not missing,'missing':missing}),flush=True)
    start=time.perf_counter()
    while True:
        for entry in processes.values():
            entry['sampled_peak_rss_bytes']=max(entry['sampled_peak_rss_bytes'],tree_rss(entry['pid']))
            entry['samples']+=1
        ready,_,_=select.select([sys.stdin],[],[],0.05)
        if ready:
            sys.stdin.readline();break
    print(json.dumps({'wall_seconds':time.perf_counter()-start,'interval_seconds':0.05,'services':processes,
                      'memory_metric':'Linux sampled service process-tree RSS; shared pages may be counted twice; short peaks may be missed'}),flush=True)


if __name__=='__main__':main()
