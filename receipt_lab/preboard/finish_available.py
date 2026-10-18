"""Wait for the existing matrix, then measure the corrected PC pipeline once.

This never substitutes fixture data, truncates the matrix or starts a duplicate
LLM benchmark. Authoring and visual review remain separate delivery steps.
"""
import subprocess
import sys
import time

import psutil

from .common import REPO, WORK, read_json
from .evidence_checks import check_llm, check_pc


def main():
    matrix=WORK/'runs/single-pass-llm-v2'
    while True:
        report=read_json(REPO/'reports/preboard/single_pass_llm.json')
        if report.get('complete'):
            if not check_llm(report):
                raise RuntimeError('Completed matrix evidence did not verify')
            break
        alive=False
        for proc in psutil.process_iter(['cmdline']):
            if 'receipt_lab.preboard.single_pass_llm' in (proc.info['cmdline'] or []):
                alive=True
        count=len(list((matrix/'attempts').glob('*.json')))
        print(f'Matrix saved {count}/288; running={alive}',flush=True)
        if not alive:
            raise RuntimeError('Matrix incomplete and runner stopped; inspect its log before resuming')
        time.sleep(30)
    report=read_json(REPO/'reports/preboard/pc_transport_profile.json')
    if report.get('run_id')=='pc-delivery-profile-engineering-v3' and check_pc(report) and report['failures']==0:
        print('Verified corrected PC profile already exists',flush=True)
        return
    print('Matrix complete and verified; measuring corrected PC pipeline',flush=True)
    subprocess.run([sys.executable,'-X','utf8','-m','receipt_lab.preboard.profile_transport',
                    '--run-id','pc-delivery-profile-engineering-v3'],cwd=REPO,check=True)
    report=read_json(REPO/'reports/preboard/pc_transport_profile.json')
    if not check_pc(report) or report['attempts']!=9 or report['failures']:
        raise RuntimeError('Corrected PC profile did not satisfy delivery check')
    print('Both experiment runs complete and raw evidence verified',flush=True)


if __name__=='__main__':main()
