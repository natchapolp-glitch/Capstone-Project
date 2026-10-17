"""Run the required regressions and retain logs with the exact source hashes."""
import re
import subprocess
import sys
import tempfile
import uuid

from .common import REPO, WORK, digest, utc, write_json


def main():
    folder=WORK/'verification'/uuid.uuid4().hex[:12]
    folder.mkdir(parents=True)
    commands=[['-m','unittest','discover','-s','tests/preboard','-v'],
              ['-m','unittest','test_json_extraction_scorer','-v'],
              ['-m','receipt_lab.preboard.dataset','validate']]
    runs=[]
    for i,args in enumerate(commands):
        command=[sys.executable,'-X','utf8','-B',*args]
        result=subprocess.run(command,cwd=REPO,capture_output=True,text=True,encoding='utf-8')
        text=result.stdout+result.stderr
        log=folder/f'check-{i}.txt';log.write_text(text,encoding='utf-8')
        count=re.search(r'Ran (\d+) tests?',text)
        runs.append({'command':command,'exit_code':result.returncode,'tests':int(count[1]) if count else None,
                     'log_path':str(log),'log_sha256':digest(log)})
        print(i,result.returncode,'tests='+str(count[1] if count else 'dataset validation'),flush=True)
    with tempfile.TemporaryDirectory() as temp:
        from pathlib import Path
        for html in (REPO/'receipt_lab/demo_pc').glob('*.html'):
            js=Path(temp)/(html.stem+'.js')
            js.write_text('\n'.join(re.findall(r'<script>([\s\S]*?)</script>',html.read_text(encoding='utf-8'))),encoding='utf-8')
            result=subprocess.run(['node','--check',str(js)],capture_output=True,text=True)
            runs.append({'command':['node','--check',str(html)+' scripts'],'exit_code':result.returncode,'script_sha256':digest(js)})
            print(html.name,result.returncode,flush=True)
    files=[*(REPO/'receipt_lab/preboard').glob('*.py'),*(REPO/'receipt_lab/demo_pc').glob('*.py'),
           *(REPO/'receipt_lab/demo_pc').glob('*.html'),REPO/'json_extraction_scorer.py',REPO/'receipt_schema.json']
    write_json(REPO/'reports/preboard/verification.json',{'timestamp':utc(),'runs':runs,
               'implementation_sha256':{p.relative_to(REPO).as_posix():digest(p) for p in files},
               'browser_visual_qa':False,'note':'HTTP regressions and JS syntax checked; CUA browser unavailable. Synthetic test attestations remain only in temporary test fixtures.'})
    if any(r['exit_code'] for r in runs):raise SystemExit(1)


if __name__=='__main__':main()
