from typing import Any

# Basic stub of rich.print used for tests

def print(*args: Any, **kwargs: Any) -> None:  # noqa: A001
    __builtins__["print"](*args, **kwargs)
