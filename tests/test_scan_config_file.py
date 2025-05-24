import json
import os
import tempfile
from mcp_scan.MCPScanner import scan_config_file


def test_scan_config_file_missing_key(tmp_path):
    data = {"notservers": {}}
    file = tmp_path / "cfg.json"
    file.write_text(json.dumps(data))
    servers = scan_config_file(str(file))
    assert servers == {}
