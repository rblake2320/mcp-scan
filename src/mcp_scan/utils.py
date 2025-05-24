import json

import shlex


def rebalance_command_args(command, args):
    """Split command string and merge with additional arguments."""
    parts = shlex.split(command)
    cmd = parts[0]
    args = parts[1:] + (args or [])
    return cmd, args


async def upload_whitelist_entry(name: str, hash: str, base_url: str):
    import aiohttp
    url = base_url + "/api/v1/public/mcp-whitelist"
    headers = {"Content-Type": "application/json"}
    data = {
        "name": name,
        "hash": hash,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=json.dumps(data)) as response:
            if response.status != 200:
                raise Exception(f"Failed to upload whitelist entry: {response.status} - {response.text}")
