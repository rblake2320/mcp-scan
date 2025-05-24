from __future__ import annotations


class FastMCP:
    def __init__(self, name: str) -> None:
        self.name = name
        self._tools = []

    def tool(self):
        def decorator(func):
            self._tools.append(func)
            return func
        return decorator

    def run(self):
        raise RuntimeError("FastMCP stub does not implement run")
