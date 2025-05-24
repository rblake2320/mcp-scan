"""mcp_scan package."""

__all__ = ["MCPScanner"]


def __getattr__(name):
    if name == "MCPScanner":
        from .MCPScanner import MCPScanner
        return MCPScanner
    raise AttributeError(name)
