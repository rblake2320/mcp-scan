import json
import os
import shlex
from collections.abc import Sequence

import aiohttp


def _ensure_sequence(args: Sequence[str] | None) -> list[str]:
    if args is None:
        return []
    if isinstance(args, list):
        return args
    return list(args)


def rebalance_command_args(command: str, args: Sequence[str] | None) -> tuple[str, list[str]]:
    """Split ``command`` into an executable and argument list.

    Historically this function relied on a custom Lark grammar which struggled
    with quoted segments and produced hard-to-debug parsing errors.  ``shlex``
    already provides a battle-tested implementation for shell-style parsing so
    we delegate the heavy lifting to it here.

    Args:
        command: Raw command string that may contain embedded arguments.
        args: Existing arguments associated with the server configuration.

    Returns:
        A tuple consisting of the executable/command and the merged argument
        list, preserving the original argument order.

    Raises:
        ValueError: If ``command`` is empty after parsing.
    """

    # ``posix`` parsing is appropriate for Unix and still provides consistent
    # behaviour across platforms for MCP server definitions.
    parsed = shlex.split(command, posix=os.name != "nt")
    if not parsed:
        raise ValueError("command must not be empty")

    existing_args = _ensure_sequence(args)
    split_command, split_args = parsed[0], parsed[1:]
    return split_command, [*split_args, *existing_args]


async def upload_whitelist_entry(name: str, hash: str, base_url: str) -> None:
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
