import builtins
import importlib

import pytest

from mcp_scan.printer import format_err_str

_ExceptionGroup: type[BaseException] | None

_candidate = getattr(builtins, "ExceptionGroup", None)
if isinstance(_candidate, type):
    _ExceptionGroup = _candidate
else:  # pragma: no cover - optional dependency for Python <3.11
    try:
        module = importlib.import_module("exceptiongroup")
    except ModuleNotFoundError:  # pragma: no cover - executed on very old interpreters
        _ExceptionGroup = None
    else:
        candidate = getattr(module, "ExceptionGroup", None)
        _ExceptionGroup = candidate if isinstance(candidate, type) else None

if _ExceptionGroup is None:  # pragma: no cover - executed on very old interpreters
    pytestmark = pytest.mark.skip("ExceptionGroup not available")


def test_format_err_str_handles_exception_group() -> None:
    assert _ExceptionGroup is not None
    try:
        raise ValueError("inner error")
    except ValueError as inner:
        group = _ExceptionGroup("wrapper", [inner])

    message = format_err_str(group)
    assert "ValueError" in message
    assert "inner error" in message


def test_format_err_str_timeout() -> None:
    message = format_err_str(TimeoutError())
    assert message == "Could not reach server within timeout"


def test_format_err_str_generic_exception() -> None:
    message = format_err_str(ValueError("bad"))
    assert message == "ValueError: bad"


@pytest.mark.parametrize("max_length", [5, 10])
def test_format_err_str_truncates(max_length: int) -> None:
    message = format_err_str(ValueError("a" * 20), max_length=max_length)
    assert len(message) <= max_length
