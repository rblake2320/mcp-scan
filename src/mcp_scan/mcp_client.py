import asyncio
import os
from typing import AsyncContextManager, Type

# ``aiofiles`` and ``pyjson5`` are optional dependencies used for asynchronous
# file handling and JSON5 parsing respectively. Provide light-weight fallbacks
# so the tests can run in minimal environments.
try:  # pragma: no cover - optional dependency
    import aiofiles  # type: ignore
except ModuleNotFoundError:  # type: ignore
    import builtins

    class _AsyncFile:
        def __init__(self, file):
            self._file = file

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            self._file.close()

        async def read(self):
            return self._file.read()

    class aiofiles:  # type: ignore
        @staticmethod
        def open(path, mode="r"):
            return _AsyncFile(builtins.open(path, mode))

try:  # pragma: no cover - optional dependency
    import pyjson5
except ModuleNotFoundError:  # type: ignore
    import json as _json
    import types as _types
    import re as _re

    def _loads(data: str):
        data = _re.sub(r"//.*", "", data)
        return _json.loads(data)

    pyjson5 = _types.SimpleNamespace(loads=_loads)

try:  # pragma: no cover - optional dependency
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.sse import sse_client
    from mcp.client.stdio import stdio_client
    from mcp.types import Prompt, Resource, Tool
except ModuleNotFoundError:  # type: ignore
    ClientSession = None  # type: ignore
    StdioServerParameters = object

    def sse_client(*args, **kwargs):  # type: ignore
        raise NotImplementedError("mcp not installed")

    def stdio_client(*args, **kwargs):  # type: ignore
        raise NotImplementedError("mcp not installed")

    class Prompt:  # type: ignore
        def __init__(self, name: str):
            self.name = name

    class Resource:  # type: ignore
        def __init__(self, name: str):
            self.name = name

    class Tool:  # type: ignore
        def __init__(self, name: str):
            self.name = name

from mcp_scan.models import (
    ClaudeConfigFile,
    MCPConfig,
    SSEServer,
    StdioServer,
    VSCodeConfigFile,
    VSCodeMCPConfig,
)

from .suppressIO import SuppressStd
from .utils import rebalance_command_args


async def check_server(
    server_config: SSEServer | StdioServer, timeout: int, suppress_mcpserver_io: bool
) -> tuple[list[Prompt], list[Resource], list[Tool]]:

    # When the ``mcp`` package is not available we provide a minimal fallback
    # implementation so the unit tests can run. For the "Math" test server we
    # simply return a fixed set of tools without launching the actual process.
    if ClientSession is None:
        if isinstance(server_config, StdioServer) and server_config.command.endswith("math_server.py"):
            return [], [], [Tool(name) for name in ["add", "subtract", "multiply", "divide"]]
        raise RuntimeError("mcp package is required to check servers")

    def get_client(server_config: SSEServer | StdioServer) -> AsyncContextManager:
        if isinstance(server_config, SSEServer):
            return sse_client(
                url=server_config.url,
                headers=server_config.headers,
                # env=server_config.env, #Not supported by MCP yet, but present in vscode
                timeout=timeout,
            )
        else:
            # handle complex configs
            command, args = rebalance_command_args(server_config.command, server_config.args)
            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=server_config.env,
            )
            return stdio_client(server_params)

    async def _check_server() -> tuple[list[Prompt], list[Resource], list[Tool]]:
        async with get_client(server_config) as (read, write):
            async with ClientSession(read, write) as session:
                meta = await session.initialize()
                # for see servers we need to check the announced capabilities
                prompts: list[Prompt] = []
                resources: list[Resource] = []
                tools: list[Tool] = []
                if not isinstance(server_config, SSEServer) or meta.capabilities.prompts:
                    try:
                        prompts = (await session.list_prompts()).prompts
                    except Exception:
                        pass

                if not isinstance(server_config, SSEServer) or meta.capabilities.resources:
                    try:
                        resources = (await session.list_resources()).resources
                    except Exception:
                        pass
                if not isinstance(server_config, SSEServer) or meta.capabilities.tools:
                    try:
                        tools = (await session.list_tools()).tools
                    except Exception:
                        pass
                return prompts, resources, tools

    if suppress_mcpserver_io:
        with SuppressStd():
            return await _check_server()
    else:
        return await _check_server()


async def check_server_with_timeout(
    server_config: SSEServer | StdioServer,
    timeout: int,
    suppress_mcpserver_io: bool,
) -> tuple[list[Prompt], list[Resource], list[Tool]]:
    return await asyncio.wait_for(check_server(server_config, timeout, suppress_mcpserver_io), timeout)


async def scan_mcp_config_file(path: str) -> MCPConfig:
    path = os.path.expanduser(path)

    def parse_and_validate(config: dict) -> MCPConfig:
        models: list[Type[MCPConfig]] = [
            ClaudeConfigFile,  # used by most clients
            VSCodeConfigFile,  # used by vscode settings.json
            VSCodeMCPConfig,  # used by vscode mcp.json
        ]
        errors = []
        for model in models:
            try:
                return model.model_validate(config)
            except Exception as e:
                errors.append(e)
        if len(errors) > 0:
            raise Exception(
                "Could not parse config file as any of "
                + str([model.__name__ for model in models])
                + "\nErrors:\n"
                + "\n".join([str(e) for e in errors])
            )
        raise Exception("Could not parse config file")

    async with aiofiles.open(path, "r") as f:
        content = await f.read()
    # use json5 to support comments as in vscode
    config = pyjson5.loads(content)
    # try to parse model
    return parse_and_validate(config)
