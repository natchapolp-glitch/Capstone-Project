"""Relocation preserves identity; changed model bytes never keep the old identity."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from receipt_lab.preboard import assets
from receipt_lab.preboard.common import write_json


class AssetTests(unittest.TestCase):
    def test_path_changes_are_portable_but_weight_changes_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'registry.json'
            saved={'version':'fixture-only','weights':[{'filename':'fixture','path':'old-location','sha256':'one'}]}
            write_json(path,{'assets':{'easyocr':saved}})
            relocated={'version':'fixture-only','weights':[{'filename':'fixture','path':'new-location','sha256':'one'}]}
            with patch.object(assets,'REGISTRY',path):
                self.assertTrue(assets.check_registered('easyocr',relocated))
                relocated['weights'][0]['sha256']='different'
                with self.assertRaises(ValueError):assets.check_registered('easyocr',relocated)


if __name__=='__main__':unittest.main()
