"""Vercel entrypoint exposing the lightweight API gateway."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault("SENSEFORGE_MODE", "mock")

from api.gateway import app as starlette_app  # noqa: E402  pylint: disable=wrong-import-position

app = starlette_app
