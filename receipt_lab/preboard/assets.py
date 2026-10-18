"""Pin actual OCR/detector assets independently from LLM checkpoints."""
import hashlib
import importlib.metadata as md
import json
import subprocess
from pathlib import Path

from .common import LAB, REPO, WORK, digest, read_json, write_json, utc

REGISTRY=WORK/'runtime_assets.json'
DETECTOR=LAB/'yolo_expanded/runs/receipt_region_v8n/weights/best.pt'


def portable(value):
    if isinstance(value,dict):return {k:portable(v) for k,v in value.items() if k not in {'path','config_path'}}
    if isinstance(value,list):return [portable(v) for v in value]
    return value


def easy_identity():
    from easyocr import config
    wanted={'craft_mlt_25k.pth','thai.pth'};models=[]
    def walk(value):
        if not isinstance(value,dict):return
        if value.get('filename') in wanted:
            path=LAB/'models/easyocr'/value['filename']
            sha,legacy=hashlib.sha256(),hashlib.md5()
            with path.open('rb') as stream:
                for chunk in iter(lambda:stream.read(1024*1024),b''):sha.update(chunk);legacy.update(chunk)
            if legacy.hexdigest()!=value['md5sum']:raise ValueError('EasyOCR vendor checksum mismatch: '+path.name)
            models.append({'filename':path.name,'path':str(path),'bytes':path.stat().st_size,
                           'sha256':sha.hexdigest(),'vendor_md5':value['md5sum'],'vendor_md5_matched':True,'source_url':value['url']})
        else:
            for child in value.values():walk(child)
    walk(config.detection_models);walk(config.recognition_models)
    if {m['filename'] for m in models}!=wanted:raise ValueError('Missing expected Thai/EasyOCR model definitions')
    return {'engine':'easyocr','version':md.version('easyocr'),'config_sha256':digest(config.__file__),
            'weights':sorted(models,key=lambda m:m['filename'])}


def tesseract_identity():
    path=(REPO/'receipt_lab/preboard/wsl_asset_info.py').resolve()
    linux='/mnt/'+path.drive[0].lower()+path.as_posix()[2:]
    result=subprocess.run(['wsl','-d','Ubuntu','--exec','python3',linux],capture_output=True,text=True,encoding='utf-8',timeout=30,check=True)
    return json.loads(result.stdout)


def detector_identity():
    root=DETECTOR.parent.parent
    return {'engine':'ultralytics_yolo','version':md.version('ultralytics'),'filename':DETECTOR.name,'path':str(DETECTOR),
            'sha256':digest(DETECTOR),'bytes':DETECTOR.stat().st_size,
            'source':'local training artifact; earlier labels and scores remain retrospective',
            'training_artifact_hashes':{name:digest(root/name) for name in ['args.yaml','results.csv'] if (root/name).exists()}}


def check_registered(name,identity):
    if not REGISTRY.exists():return False
    saved=read_json(REGISTRY)['assets'][name]
    if portable(saved)!=portable(identity):raise ValueError('Runtime asset changed after registration: '+name)
    return True


def require_registry():
    if not REGISTRY.exists():raise ValueError('Run python -m receipt_lab.preboard.assets before scored experiments')
    return digest(REGISTRY)


def main():
    assets={'easyocr':easy_identity(),'tesseract':tesseract_identity(),'detector':detector_identity()}
    if REGISTRY.exists():
        for name,value in assets.items():check_registered(name,value)
    else:write_json(REGISTRY,{'timestamp':utc(),'assets':assets})
    write_json(REPO/'reports/preboard/runtime_ocr_detector_assets.json',{'registry_sha256':digest(REGISTRY),
               'assets':portable(assets),'note':'Current asset identity, not retroactive proof of older engineering runs that omitted asset hashes'})
    print('Registered EasyOCR vendor-verified weights, two Tesseract languages, executable and local YOLO weights')


if __name__=='__main__':main()
