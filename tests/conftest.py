"""Make scripts/ importable so the import scripts can be tested directly.

The scripts are standalone executables rather than an installed package, so
there is no import path to them by default.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
