import shlex
import json

def rebalance_command_args(command: str, args: list[str] | None):
    """Split *command* into command and arguments, rebalancing with *args*.

    ``shlex.split`` handles quoting and escaping rules adequately for the test
    cases used in this project and avoids requiring the ``lark`` dependency.
    """

    parts = shlex.split(command)
    cmd = parts[0] if parts else ""
    cmd_args = parts[1:]
    cmd_args.extend(args or [])
    return cmd, cmd_args

def upload_whitelist_entry(name: str, hash: str, base_url: str):
    url = base_url + "/api/v1/public/mcp-whitelist"
    headers = {"Content-Type": "application/json"}
    data = {
        "name": name,
        "hash": hash,
    }
    # Import requests lazily to avoid an import-time dependency during tests
    import requests

    response = requests.post(url, headers=headers, data=json.dumps(data))
