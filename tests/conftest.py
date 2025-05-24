import sys
from pathlib import Path

# Ensure src directory is on path for tests
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))
