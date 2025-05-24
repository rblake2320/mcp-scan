from dataclasses import dataclass
from typing import Optional

@dataclass
class Prompt:
    name: str
    description: Optional[str] = None

@dataclass
class Resource:
    name: str
    description: Optional[str] = None

@dataclass
class Tool:
    name: str
    description: Optional[str] = None
