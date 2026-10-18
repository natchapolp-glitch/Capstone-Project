"""Inspect the actual Tesseract executable and trained language files inside WSL."""
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path


def sha(path):
    value=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):value.update(chunk)
    return value.hexdigest()


def inspect():
    languages=subprocess.check_output(['tesseract','--list-langs'],text=True)
    match=re.search(r'in "([^"]+)"',languages)
    if not match:raise RuntimeError('Cannot identify the active Tesseract data directory')
    directory=Path(match[1])
    executable=Path(shutil.which('tesseract')).resolve()
    return {'engine':'tesseract','version':subprocess.check_output(['tesseract','--version'],text=True).splitlines()[0],
            'data_dir':str(directory),'executable_sha256':sha(executable),
            'weights':[{'filename':language+'.traineddata','path':str(directory/(language+'.traineddata')),
                        'sha256':sha(directory/(language+'.traineddata')),'bytes':(directory/(language+'.traineddata')).stat().st_size}
                       for language in ['tha','eng']]}


if __name__=='__main__':print(json.dumps(inspect()))
