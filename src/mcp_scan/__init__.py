"""mcp-scan package initialization."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type checkers only
    from .MCPScanner import MCPScanner as _MCPScanner


def __getattr__(name: str):
    if name == "MCPScanner":  # defer heavy import until requested
        from .MCPScanner import MCPScanner as _MCPScanner

        return _MCPScanner
    raise AttributeError(name)


__all__ = ["MCPScanner"]
