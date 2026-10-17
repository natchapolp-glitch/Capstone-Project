"""Set draft image scope BEFORE human entry; never relabel existing reviewed text."""
import argparse
import json

from .common import WORK, read_json, write_json, utc
from .dataset import MANIFEST, annotations, validate


def configure(doc_id, boxes, rotation, capture_conditions=None):
    if annotations(doc_id) or (WORK/'annotations/adjudicated'/f'{doc_id}.json').exists():
        raise ValueError('Preserve existing human entries: image scope must be set before both review rounds')
    data=read_json(MANIFEST)
    row=next(r for r in data['records'] if r['doc_id']==doc_id)
    if len(boxes)!=1 or rotation not in {'none','cw','ccw'}:
        raise ValueError('Single-region protocol requires one document box and a valid rotation; exclude complex photos')
    row.update(original_pixel_boxes=boxes,rotation_to_read=rotation,box_status='draft_ai',
               rotation_source='draft setup before human entry; confirmed only at adjudication',bbox_exclusion_reason=None)
    if capture_conditions:
        if not isinstance(capture_conditions,dict) or not all(isinstance(capture_conditions.get(k),str) and capture_conditions[k].strip() for k in ['device','lighting','background','capture_source']):
            raise ValueError('Record device, lighting, background and capture_source as non-empty strings')
        row['capture_conditions']=capture_conditions
        row['capture_conditions_status']='operator_supplied_pending_adjudication'
    errors=validate(data)
    if errors:raise ValueError('; '.join(errors))
    row['scope_configured_at']=utc()
    data['version']+=1
    write_json(MANIFEST,data)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--doc-id',required=True)
    ap.add_argument('--box',required=True,help='x0,y0,x1,y1 in normalized original-image pixels')
    ap.add_argument('--rotation',choices=['none','cw','ccw'],default='none')
    ap.add_argument('--capture-conditions',help='JSON containing device, lighting, background and capture_source')
    args=ap.parse_args()
    configure(args.doc_id,[list(map(float,args.box.split(',')))],args.rotation,
              json.loads(args.capture_conditions) if args.capture_conditions else None)
    print('Draft region saved. Open /review and inspect the displayed crop before both entry rounds.')


if __name__=='__main__':main()
