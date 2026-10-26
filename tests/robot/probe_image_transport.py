"""Compare HTTP transfer and Chrome image decoding without changing demo data."""
import json
import time
import urllib.request
from pathlib import Path
from selenium import webdriver

base='http://127.0.0.1:8090'
rid='ca5ac06a-fd54-45ad-b197-2642da31535c'
results=[]
options=webdriver.ChromeOptions()
options.add_argument('--headless=new')
driver=webdriver.Chrome(options=options)
try:
    for path in ['/api/image?doc_id=R74946CAAC57E','/api/detection-image?id='+rid]:
        row={'path':path}
        try:
            start=time.monotonic()
            with urllib.request.urlopen(base+path,timeout=30) as response:
                row['http_status']=response.status
                row['declared_bytes']=response.headers.get('Content-Length')
                data=response.read()
                row['received_bytes']=len(data)
            row['seconds']=time.monotonic()-start
        except Exception as exc:
            row['http_error']=str(exc)
        driver.get(base+path)
        row['chrome']=driver.execute_script('return [...document.images].map(i=>({complete:i.complete,width:i.naturalWidth,src:i.src}))')
        row['errors']=driver.get_log('browser')
        results.append(row)
finally:
    driver.quit()
print(json.dumps(results,indent=2))
