import asyncio
import os
from typing import AsyncContextManager, Type

try:
    import aiofiles  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    aiofiles = None
try:
    import pyjson5
except Exception:  # pragma: no cover - optional dependency
    import json as pyjson5  # type: ignore
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from mcp.types import Prompt, Resource, Tool

from mcp_scan.models import MCPConfig, SSEServer, StdioServer

from .suppressIO import SuppressStd
from .utils import rebalance_command_args


async def check_server(
    server_config: SSEServer | StdioServer, timeout: int, suppress_mcpserver_io: bool
) -> tuple[list[Prompt], list[Resource], list[Tool]]:

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
    """Load a simple MCP config file."""
    path = os.path.expanduser(path)

    if aiofiles is not None:
        async with aiofiles.open(path, "r") as f:
            content = await f.read()
    else:
        with open(path, "r") as f:
            content = f.read()

    config = pyjson5.loads(content)

    if "mcpServers" in config:
        servers_cfg = config["mcpServers"]
    elif "servers" in config:
        servers_cfg = config["servers"]
    elif "mcp" in config and isinstance(config["mcp"], dict) and "servers" in config["mcp"]:
        servers_cfg = config["mcp"]["servers"]
    else:
        raise Exception("Could not parse config file")

    servers = {}
    for name, srv in servers_cfg.items():
        srv_type = srv.get("type", "stdio")
        if srv_type == "sse":
            servers[name] = SSEServer(url=srv["url"], headers=srv.get("headers", {}))
        else:
            servers[name] = StdioServer(
                command=srv["command"],
                args=srv.get("args"),
                env=srv.get("env", {}),
            )

    return MCPConfig(servers)
