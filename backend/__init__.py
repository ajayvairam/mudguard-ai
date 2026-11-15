import sys
from pathlib import Path

_backend = str(Path(__file__).resolve().parent)
_root = str(Path(__file__).resolve().parent.parent)

for p in [_backend, _root]:
    if p not in sys.path:
        sys.path.insert(0, p)
