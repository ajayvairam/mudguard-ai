import sys
from pathlib import Path

# Ensure backend root and project root are always in sys.path
_current = Path(__file__).resolve().parent
_backend = str(_current.parent)
_root = str(_current.parent.parent)

for p in [_backend, _root]:
    if p not in sys.path:
        sys.path.insert(0, p)
