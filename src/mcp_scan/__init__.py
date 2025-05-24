
"""mcp_scan package."""

# MCPScanner is imported lazily to avoid importing heavy dependencies when the
# package is used for its utility modules only (e.g. during testing).

def __getattr__(name: str):
    if name == "MCPScanner":
        from .MCPScanner import MCPScanner

        return MCPScanner
    raise AttributeError(name)
