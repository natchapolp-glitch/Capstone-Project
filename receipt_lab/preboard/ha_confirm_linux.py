"""Called inside WSL; bearer token arrives on stdin and is never printed."""
import asyncio
import json
import sys
import aiohttp


async def main():
    config = json.load(sys.stdin)
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect("ws://127.0.0.1:8123/api/websocket") as ws:
            await ws.receive_json()
            await ws.send_json({"type": "auth", "access_token": config["access_token"]})
            authenticated = await ws.receive_json()
            if authenticated["type"] != "auth_ok":
                raise RuntimeError("Local HA websocket authentication failed")
            await ws.send_json({"id": 1, "type": "http/config/promote"})
            result = await ws.receive_json()
            print(json.dumps({"http_configuration_confirmed": result.get("success"), "error": result.get("error")}))


asyncio.run(main())
