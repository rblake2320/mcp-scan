"""Global pytest fixtures for mcp-scan tests."""

import os
import sys

import pytest

# Ensure src package is discoverable when running tests without installation
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_PATH = os.path.join(ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)


@pytest.fixture
def sample_fixture():
    """Sample fixture for demonstration purposes."""
    return "sample_value"
