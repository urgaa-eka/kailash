"""Import bootstrap for the backend test suite.

`backend/__init__.py` and `backend/tests/__init__.py` both exist, so pytest walks
up past `backend/` when it works out the rootdir to put on `sys.path` and lands
on the repository root. Test modules are therefore imported as
`backend.tests.*`, and a bare `from app.main import app` raises
ModuleNotFoundError.

`python -m pytest` happens to hide this, because `-m` puts the working directory
on `sys.path` first. CI runs plain `pytest tests -q` from `backend/`, which does
not, so the bootstrap has to be explicit or the suite fails at collection.
"""
import sys
from pathlib import Path

_BACKEND_ROOT = str(Path(__file__).resolve().parent.parent)

if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)
