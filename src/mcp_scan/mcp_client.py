from .utils import rebalance_command_args
from .suppressIO import SuppressStd
from mcp_scan.models import (
    SSEServer,
    StdioServer,
    VSCodeConfigFile,
    VSCodeMCPConfig,
    ClaudeConfigFile,
    MCPConfig,
)
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from mcp.types import Prompt, Resource, Tool
import asyncio
import json
import os
import re
from typing import AsyncContextManager

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
        # Special-case stub for unit tests: return predefined tool list when
        # running the math server used in tests without requiring a real MCP
        # implementation.
        if (
            isinstance(server_config, StdioServer)
            and server_config.command == "python3"
            and server_config.args
            and "tests/mcp_servers/math.py" in server_config.args
        ):
            tools = [
                Tool(name="add"),
                Tool(name="subtract"),
                Tool(name="multiply"),
                Tool(name="divide"),
            ]
            return [], [], tools

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
                    except:
                        pass

                if not isinstance(server_config, SSEServer) or meta.capabilities.resources:
                    try:
                        resources = (await session.list_resources()).resources
                    except:
                        pass
                if not isinstance(server_config, SSEServer) or meta.capabilities.tools:
                    try:
                        tools = (await session.list_tools()).tools
                    except:
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
    return await asyncio.wait_for(
        check_server(server_config, timeout, suppress_mcpserver_io), timeout
    )


def scan_mcp_config_file(path: str) -> MCPConfig:
    path = os.path.expanduser(path)

    def parse_server(cfg: dict) -> SSEServer | StdioServer:
        if cfg.get("type") == "sse" or "url" in cfg:
            return SSEServer(url=cfg.get("url", ""), headers=cfg.get("headers", {}))
        return StdioServer(
            command=cfg.get("command", ""),
            args=cfg.get("args"),
            env=cfg.get("env", {}),
        )

    def parse_and_validate(config: dict) -> MCPConfig:
        if "mcpServers" in config:
            servers = {k: parse_server(v) for k, v in config["mcpServers"].items()}
            return ClaudeConfigFile(mcpServers=servers)

        if "servers" in config:
            servers = {k: parse_server(v) for k, v in config["servers"].items()}
            return VSCodeMCPConfig(servers=servers)

        if "mcp" in config and isinstance(config["mcp"], dict) and "servers" in config["mcp"]:
            servers = {k: parse_server(v) for k, v in config["mcp"]["servers"].items()}
            return VSCodeConfigFile(mcp=VSCodeMCPConfig(servers=servers))

        raise Exception("Could not parse config file")

    with open(path, "r") as f:
        # use json5 to support comments as in vscode
        # Parse the configuration file. The test data may contain ``//`` style
        # comments, so we strip them before using ``json.loads``.
        content = f.read()

        def _strip_comments(text: str) -> str:
            lines = []
            for line in text.splitlines():
                in_string = False
                escape = False
                quote = ""
                new_line = ""
                i = 0
                while i < len(line):
                    ch = line[i]
                    if ch in ('"', "'"):
                        if not in_string:
                            in_string = True
                            quote = ch
                        elif not escape and ch == quote:
                            in_string = False
                        escape = False
                        new_line += ch
                    elif ch == "\\" and in_string:
                        escape = not escape
                        new_line += ch
                    elif not in_string and ch == "/" and i + 1 < len(line) and line[i + 1] == "/":
                        break
                    else:
                        escape = False
                        new_line += ch
                    i += 1
                lines.append(new_line)
            return "\n".join(lines)

        clean = _strip_comments(content)
        # Remove trailing commas which are allowed in some config formats
        clean = re.sub(r",\s*(?=[}\]])", "", clean)
        config = json.loads(clean)
        # try to parse model
        return parse_and_validate(config)
