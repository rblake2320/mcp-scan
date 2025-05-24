"""Global pytest fixtures for mcp-scan tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure the src directory is on the import path so tests can import the
# ``mcp_scan`` package without an editable install.
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR / "src"))
# Provide lightweight test stubs for optional dependencies such as ``pydantic``.
sys.path.insert(0, str(BASE_DIR / "tests" / "stubs"))


@pytest.fixture
def sample_fixture():
    """Sample fixture for demonstration purposes."""
    return "sample_value"


@pytest.fixture
def claudestyle_config():
    """Sample Claude-style MCP config."""
    return """{
    "mcpServers": {
        "claude": {
            "command": "mcp",
            "args": ["--server", "http://localhost:8000"],
        }
    }
}"""


@pytest.fixture
def vscode_mcp_config():
    """Sample VSCode MCP config with inputs."""
    return """{
  // Inputs are prompted on first server start, then stored securely by VS Code.
  "inputs": [
    {
      "type": "promptString",
      "id": "perplexity-key",
      "description": "Perplexity API Key",
      "password": true
    }
  ],
  "servers": {
    // https://github.com/ppl-ai/modelcontextprotocol/
    "Perplexity": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-perplexity-ask"],
      "env": {
        "PERPLEXITY_API_KEY": "ASDF"
      }
    }
  }
}
"""


@pytest.fixture
def vscode_config():
    """Sample VSCode settings.json with MCP config."""
    return """// settings.json
{
  "mcp": {
    "servers": {
      "my-mcp-server": {
        "type": "stdio",
        "command": "my-command",
        "args": []
      }
    }
  }
}"""


@pytest.fixture
def sample_configs(claudestyle_config, vscode_mcp_config, vscode_config):
    """List of all sample configs."""
    return [claudestyle_config, vscode_mcp_config, vscode_config]
