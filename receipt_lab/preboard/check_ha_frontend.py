"""Check authenticated frontend WebSocket dependencies, without exposing credentials."""
import json
import subprocess

from .services import access_token


PROBE = r'''
import asyncio, json, sys
import aiohttp

async def main():
    token = json.load(sys.stdin)['token']
    checks = []
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect('ws://127.0.0.1:8123/api/websocket', timeout=15) as ws:
            await ws.receive_json(timeout=15)
            await ws.send_json({'type': 'auth', 'access_token': token})
            if (await ws.receive_json(timeout=15))['type'] != 'auth_ok':
                raise RuntimeError('Authentication failed')
            for i, command in enumerate(['get_config', 'get_states', 'get_services', 'get_panels', 'auth/current_user', 'frontend/get_themes'], 1):
                await ws.send_json({'id': i, 'type': command})
                reply = await ws.receive_json(timeout=30)
                checks.append({'command': command, 'success': reply.get('success', False), 'error': reply.get('error')})
    print(json.dumps({'checks': checks, 'all_passed': all(c['success'] for c in checks)}))

asyncio.run(main())
'''


def main():
    result = subprocess.run([
        'wsl', '-d', 'Ubuntu', '--exec',
        '/home/natchapol/SeminarLab/preboard-ha/bin/python', '-c', PROBE],
        input=json.dumps({'token': access_token()}), text=True, encoding='utf-8',
        capture_output=True, timeout=210)
    if result.returncode:
        raise RuntimeError('Frontend WebSocket probe failed: ' + result.stderr[-1200:])
    report = json.loads(result.stdout)
    print(json.dumps(report))
    if not report['all_passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
