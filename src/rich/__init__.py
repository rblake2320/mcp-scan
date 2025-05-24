"""Minimal stub of the ``rich`` package used in tests."""

from typing import Any


class Text(str):
    """Simple Text stub used by MCPScanner tests."""

    @classmethod
    def from_markup(cls, text: str) -> "Text":
        return cls(text)


class Tree:
    """Simple Tree stub used by MCPScanner tests."""

    def __init__(self, label: str) -> None:
        self.label = label

    def add(self, item: Any) -> "Tree":
        return Tree(str(item))


def print(*args: Any, **kwargs: Any) -> None:  # type: ignore
    __builtins__["print"](*args, **kwargs)

__all__ = ["print", "Tree", "Text"]
