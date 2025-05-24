"""Minimal ``mcp.types`` module used for tests."""
from dataclasses import dataclass
from typing import Any


@dataclass
class Prompt:
    name: str
    description: str | None = None


@dataclass
class Resource:
    name: str
    description: str | None = None


@dataclass
class Tool:
    name: str
    description: str | None = None
