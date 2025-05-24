import json

import aiohttp
try:  # pragma: no cover - optional dependency
    from lark import Lark
except Exception:  # pragma: no cover - fall back to shlex if lark unavailable
    Lark = None
    import shlex


def rebalance_command_args(command, args):
    if Lark is None:
        parts = shlex.split(command)
        return parts[0], parts[1:] + (args or [])

    # create a parser that splits on whitespace,
    # unless it is inside quotes
    parser = Lark(
        r"""
        command: WORD+
        WORD: (PART|SQUOTEDPART|DQUOTEDPART)
        PART: /[^\s'".]+/
        SQUOTEDPART: /'[^']*'/
        DQUOTEDPART: /"[^"]*"/
        %import common.WS
        %ignore WS
        """,
        parser="lalr",
        start="command",
        regex=True,
    )
    tree = parser.parse(command)
    parts = [node.value for node in tree.children]
    return parts[0], parts[1:] + (args or [])


async def upload_whitelist_entry(name: str, hash: str, base_url: str):
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
