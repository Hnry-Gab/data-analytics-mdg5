"""Pytest configuration — add ``src/`` to sys.path so imports resolve."""

import sys
from pathlib import Path

# Insert src/ at the front of sys.path so that `import olist_mcp` and
# `import backend` resolve to packages under src/.
_SRC = str(Path(__file__).resolve().parent.parent)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
