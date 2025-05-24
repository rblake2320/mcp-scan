from dataclasses import dataclass, field
from datetime import datetime
from hashlib import md5
from types import SimpleNamespace
from typing import Any, Dict, Literal, TypeAlias

from mcp.types import Prompt, Resource, Tool

Entity: TypeAlias = Prompt | Resource | Tool


def hash_entity(entity: Entity | None) -> str | None:
    if entity is None or not getattr(entity, "description", None):
        return None
    return md5(entity.description.encode()).hexdigest()


def entity_type_to_str(entity: Entity) -> str:
    if isinstance(entity, Prompt):
        return "prompt"
    if isinstance(entity, Resource):
        return "resource"
    if isinstance(entity, Tool):
        return "tool"
    raise ValueError(f"Unknown entity type: {type(entity)}")


@dataclass
class StdioServer:
    command: str
    args: list[str] | None = None
    type: Literal["stdio"] | None = "stdio"
    env: Dict[str, str] = field(default_factory=dict)


@dataclass
class SSEServer:
    url: str
    type: Literal["sse"] | None = "sse"
    headers: Dict[str, str] = field(default_factory=dict)


class MCPConfig:
    def __init__(self, servers: Dict[str, SSEServer | StdioServer]):
        self._servers = servers

    def get_servers(self) -> Dict[str, SSEServer | StdioServer]:
        return self._servers

    def set_servers(self, servers: Dict[str, SSEServer | StdioServer]) -> None:
        self._servers = servers


class ScanException(Exception):
    def __init__(self, message: str | None = None, error: Exception | None = None):
        super().__init__(message)
        self.message = message
        self.error = error

    @property
    def text(self) -> str:
        return self.message or (str(self.error) if self.error else "")


@dataclass
class EntityScanResult:
    verified: bool | None = None
    changed: bool | None = None
    whitelisted: bool | None = None
    status: str | None = None
    messages: list[str] = field(default_factory=list)


@dataclass
class CrossRefResult:
    found: bool | None = None
    sources: list[str] = field(default_factory=list)


@dataclass
class ServerScanResult:
    name: str | None
    server: SSEServer | StdioServer
    prompts: list[Prompt] = field(default_factory=list)
    resources: list[Resource] = field(default_factory=list)
    tools: list[Tool] = field(default_factory=list)
    result: list[EntityScanResult] | None = None
    error: ScanException | None = None

    @property
    def entities(self) -> list[Entity]:
        return self.prompts + self.resources + self.tools

    @property
    def is_verified(self) -> bool:
        return self.result is not None

    @property
    def entities_with_result(self) -> list[tuple[Entity, EntityScanResult | None]]:
        if self.result is not None:
            return list(zip(self.entities, self.result))
        return [(entity, None) for entity in self.entities]


@dataclass
class ScanPathResult:
    path: str
    servers: list[ServerScanResult] = field(default_factory=list)
    error: ScanException | None = None
    cross_ref_result: CrossRefResult | None = None
