import tempfile
import unittest
from pathlib import Path
from receipt_lab.preboard.demo_preflight import find_llama_server


class RuntimeAvailabilityTests(unittest.TestCase):
    def test_missing_executable_explains_recovery_without_creating_files(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(FileNotFoundError, 'quarantine'):
                find_llama_server(directory)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_nested_executable_and_ambiguity(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / 'bin' / 'llama-server.exe'
            first.parent.mkdir()
            first.write_bytes(b'fixture only, never executed')
            self.assertEqual(find_llama_server(directory), first)
            (Path(directory) / 'llama-server.exe').write_bytes(b'second fixture')
            with self.assertRaisesRegex(RuntimeError, 'Multiple'):
                find_llama_server(directory)
