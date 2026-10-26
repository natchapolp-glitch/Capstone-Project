"""Read-only runtime availability checks; never restore or download executables."""
import argparse
import json
from pathlib import Path

from .common import WORK, read_json


def find_llama_server(binary_dir):
    matches = sorted(Path(binary_dir).rglob('llama-server.exe'))
    if not matches:
        raise FileNotFoundError(
            f'Local LLM runtime missing: {Path(binary_dir) / "llama-server.exe"}. '
            'Inspect antivirus quarantine and verify the original release before restoring. '
            'Saved-result replay remains available; live inference is not ready.')
    if len(matches) != 1:
        raise RuntimeError('Multiple llama-server.exe files found; select an unambiguous runtime directory')
    return matches[0]


def check_runtime(work=WORK):
    registry = read_json(Path(work) / 'model_registry.json')
    executable = find_llama_server(registry['binary_dir'])
    missing = [m['id'] for m in registry['models'] if not Path(m['path']).is_file()]
    if missing:
        raise FileNotFoundError('Registered model files missing: ' + ', '.join(missing))
    return {'runtime_files_present': True, 'llama_tag': registry['llama_tag'],
            'executable': str(executable), 'note': 'Availability only; a live inference test is still required'}


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    try:
        print(json.dumps(check_runtime(), ensure_ascii=True))
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        print(json.dumps({'runtime_files_present': False, 'error': str(exc)}, ensure_ascii=True))
        raise SystemExit(1)


if __name__ == '__main__':
    main()
