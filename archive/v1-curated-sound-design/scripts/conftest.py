"""Wspólne fixture'y testów skryptów."""
from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture()
def tmp(tmp_path: Path) -> Path:
    """Alias historyczny: testy pisały `tmp`, pytest daje `tmp_path`."""
    return tmp_path
