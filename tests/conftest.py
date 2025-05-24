"""Global pytest configuration and fixtures for mcp-scan tests."""

from __future__ import annotations

import os
import sys
import pytest


# Ensure the project source directory is importable without installing the
# package. This mirrors the behavior of ``pip install -e .`` but avoids the
# need for network access during testing.
SRC_PATH = os.path.join(os.path.dirname(__file__), os.pardir, "src")
SRC_ABS_PATH = os.path.abspath(SRC_PATH)
if SRC_ABS_PATH not in sys.path:
    sys.path.insert(0, SRC_ABS_PATH)


@pytest.fixture
def sample_fixture() -> str:
    """Sample fixture for demonstration purposes."""
    return "sample_value"
