from typing import Any


class Tree:
    def __init__(self, label: str) -> None:
        self.label = label

    def add(self, item: Any) -> "Tree":
        return Tree(str(item))
