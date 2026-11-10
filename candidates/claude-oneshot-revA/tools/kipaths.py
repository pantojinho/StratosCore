"""Locate the KiCad 10 installation (CLI, symbol/footprint libraries) on Windows or Linux.

Override with the environment variables KICAD_CLI, KICAD10_SYMBOL_DIR and KICAD10_FOOTPRINT_DIR.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

_WIN = Path("C:/Program Files/KiCad/10.0")


def _first(*cands) -> Path:
    for c in cands:
        if c and Path(c).exists():
            return Path(c)
    return Path(cands[-1])


CLI = os.environ.get("KICAD_CLI") or shutil.which("kicad-cli") or str(_WIN / "bin" / "kicad-cli.exe")
KICAD_SYM = _first(os.environ.get("KICAD10_SYMBOL_DIR"), "/usr/share/kicad/symbols", _WIN / "share/kicad/symbols")
KICAD_FP = _first(os.environ.get("KICAD10_FOOTPRINT_DIR"), "/usr/share/kicad/footprints", _WIN / "share/kicad/footprints")
KICAD_3D = _first(os.environ.get("KICAD10_3DMODEL_DIR"), "/usr/share/kicad/3dmodels", _WIN / "share/kicad/3dmodels")
