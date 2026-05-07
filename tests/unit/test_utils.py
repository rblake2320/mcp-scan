import pytest

from mcp_scan.utils import rebalance_command_args


def test_rebalance_command_args() -> None:
    command, args = rebalance_command_args("ls -l", ["-a"])
    assert command == "ls"
    assert args == ["-l", "-a"]

    command, args = rebalance_command_args("ls -l", [])
    assert command == "ls"
    assert args == ["-l"]

    command, args = rebalance_command_args("ls   -l    ", [])
    assert command == "ls"
    assert args == ["-l"]


def test_rebalance_command_args_handles_quotes() -> None:
    command, args = rebalance_command_args("python -m module --flag='some value'", None)
    assert command == "python"
    assert args == ["-m", "module", "--flag=some value"]

    command, args = rebalance_command_args('cmd "quoted arg"', ("--foo",))
    assert command == "cmd"
    assert args == ["quoted arg", "--foo"]


def test_rebalance_command_args_rejects_empty_command() -> None:
    with pytest.raises(ValueError):
        rebalance_command_args("   ", [])
