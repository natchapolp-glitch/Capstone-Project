"""Phone orientation and pre-entry crop edits must preserve annotation scope."""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from receipt_lab.preboard import intake_challenge, regions
from receipt_lab.preboard.common import digest, read_json, write_json


class IntakeTests(unittest.TestCase):
    def test_exif_frame_is_normalized_and_original_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);inbox=root/'inbox';inbox.mkdir()
            original=inbox/'fixture.jpg'
            exif=Image.Exif();exif[274]=6
            Image.new('RGB',(12,8),'red').save(original,exif=exif)
            original_hash=digest(original)
            manifest=root/'manifest.json'
            write_json(manifest,{'version':1,'records':[]})
            with patch.object(intake_challenge,'WORK',root),patch.object(intake_challenge,'MANIFEST',manifest),patch.object(sys,'argv',['intake',str(inbox)]),contextlib.redirect_stdout(io.StringIO()):
                intake_challenge.main()
                intake_challenge.main()
            rows=read_json(manifest)['records']
            self.assertEqual(len(rows),1)
            row=rows[0]
            self.assertEqual((row['width'],row['height']),(8,12))
            self.assertEqual(digest(row['original_source']),original_hash)
            self.assertEqual(digest(original),original_hash)
            with Image.open(row['source']) as canonical:
                self.assertEqual(canonical.size,(8,12))
                self.assertFalse(canonical.getexif())
            with patch.object(regions,'WORK',root),patch.object(regions,'MANIFEST',manifest),patch.object(regions,'annotations',return_value=[]):
                regions.configure(row['doc_id'],[[0,0,8,12]],'none',{'device':'fixture','lighting':'fixture','background':'fixture','capture_source':'synthetic unit test only'})
            self.assertEqual(read_json(manifest)['records'][0]['box_status'],'draft_ai')
            before=digest(manifest)
            with patch.object(regions,'WORK',root),patch.object(regions,'MANIFEST',manifest),patch.object(regions,'annotations',return_value=[{'fixture':'human entry'}]):
                with self.assertRaises(ValueError):regions.configure(row['doc_id'],[[0,0,4,6]],'none')
            self.assertEqual(digest(manifest),before)


if __name__=='__main__':unittest.main()
