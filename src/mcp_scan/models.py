from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal, NamedTuple, TypeAlias

from mcp.types import Prompt, Resource, Tool

Entity: TypeAlias = Prompt | Resource | Tool


def entity_type_to_str(entity: Entity) -> str:
    if isinstance(entity, Prompt):
        return "prompt"
    if isinstance(entity, Resource):
        return "resource"
    if isinstance(entity, Tool):
        return "tool"
    raise ValueError(f"Unknown entity type: {type(entity)}")


@dataclass
class ScannedEntity:
    hash: str
    type: str
    verified: bool
    timestamp: datetime
    description: str | None = None


ScannedEntities: TypeAlias = dict[str, ScannedEntity]


class Result(NamedTuple):
    value: Any = None
    message: str | None = None


@dataclass
class SSEServer:
    url: str
    type: Literal["sse"] | None = "sse"
    headers: dict[str, str] = field(default_factory=dict)


@dataclass
class StdioServer:
    command: str
    args: list[str] | None = None
    type: Literal["stdio"] | None = "stdio"
    env: dict[str, str] = field(default_factory=dict)


class MCPConfig:
    def get_servers(self) -> dict[str, SSEServer | StdioServer]:
        raise NotImplementedError

    def set_servers(self, servers: dict[str, SSEServer | StdioServer]) -> None:
        raise NotImplementedError


@dataclass
class ClaudeConfigFile(MCPConfig):
    mcpServers: dict[str, SSEServer | StdioServer]

    def get_servers(self) -> dict[str, SSEServer | StdioServer]:
        return self.mcpServers

    def set_servers(self, servers: dict[str, SSEServer | StdioServer]) -> None:
        self.mcpServers = servers


@dataclass
class VSCodeMCPConfig(MCPConfig):
    inputs: list[Any] | None = None
    servers: dict[str, SSEServer | StdioServer] = field(default_factory=dict)

    def get_servers(self) -> dict[str, SSEServer | StdioServer]:
        return self.servers

    def set_servers(self, servers: dict[str, SSEServer | StdioServer]) -> None:
        self.servers = servers


@dataclass
class VSCodeConfigFile(MCPConfig):
    mcp: VSCodeMCPConfig

    def get_servers(self) -> dict[str, SSEServer | StdioServer]:
        return self.mcp.servers

    def set_servers(self, servers: dict[str, SSEServer | StdioServer]) -> None:
        self.mcp.servers = servers
