"""Unit tests for the mcp_client module."""

import asyncio
import tempfile
from unittest.mock import AsyncMock, Mock, patch

import pytest

from mcp_scan.mcp_client import check_server, scan_mcp_config_file
from mcp_scan.models import StdioServer


def test_scan_mcp_config(sample_configs):
    for config in sample_configs:
        with tempfile.NamedTemporaryFile(mode="w") as temp_file:
            temp_file.write(config)
            temp_file.flush()

            asyncio.run(scan_mcp_config_file(temp_file.name))


def test_check_server_mocked():
    # Create mock objects
    mock_session = Mock()
    mock_read = AsyncMock()
    mock_write = AsyncMock()

    # Mock initialize response
    mock_meta = Mock()
    mock_meta.capabilities = Mock()
    mock_meta.capabilities.prompts = Mock()
    mock_meta.capabilities.resources = Mock()
    mock_meta.capabilities.tools = Mock()
    mock_meta.capabilities.prompts.supported = True
    mock_meta.capabilities.resources.supported = True
    mock_meta.capabilities.tools.supported = True
    mock_session.initialize = AsyncMock(return_value=mock_meta)

    # Mock list responses
    mock_prompts = Mock()
    mock_prompts.prompts = ["prompt1", "prompt2"]
    mock_session.list_prompts = AsyncMock(return_value=mock_prompts)

    mock_resources = Mock()
    mock_resources.resources = ["resource1"]
    mock_session.list_resources = AsyncMock(return_value=mock_resources)

    mock_tools = Mock()
    mock_tools.tools = ["tool1", "tool2", "tool3"]
    mock_session.list_tools = AsyncMock(return_value=mock_tools)

    # Set up the mock stdio client to return our mocked read/write pair
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = (mock_read, mock_write)

    def fake_stdio_client(*args, **kwargs):
        return mock_client

    # Mock ClientSession with proper async context manager protocol
    class MockClientSession:
        def __init__(self, read, write):
            self.read = read
            self.write = write

        async def __aenter__(self):
            return mock_session

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    # Test function with mocks
    async def run_test():
        with patch("mcp_scan.mcp_client.ClientSession", MockClientSession), patch(
            "mcp_scan.mcp_client.stdio_client", new=fake_stdio_client
        ):
            server = StdioServer(command="mcp", args=["run", "some_file.py"])
            return await check_server(server, 2, True)

    prompts, resources, tools = asyncio.run(run_test())

    # Verify the results
    assert len(prompts) == 2
    assert len(resources) == 1
    assert len(tools) == 3


def test_mcp_server():
    pytest.skip("Requires full mcp implementation", allow_module_level=False)
