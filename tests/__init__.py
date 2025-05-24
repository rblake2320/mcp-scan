"""Test package for mcp-scan.

This module ensures that the project's ``src`` directory is importable during
tests without requiring an editable install.  This mirrors ``pip install -e .``
but keeps the tests self contained.
"""

from __future__ import annotations

import os
import sys

SRC_PATH = os.path.join(os.path.dirname(__file__), os.pardir, "src")
SRC_ABS_PATH = os.path.abspath(SRC_PATH)
if SRC_ABS_PATH not in sys.path:
    sys.path.insert(0, SRC_ABS_PATH)
