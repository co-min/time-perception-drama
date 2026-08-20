"""
session_saver.py
-----------------
Writes session-level metadata to session_info.json once, at session start.
"""

import json
from pathlib import Path
from typing import Any, Dict

SESSION_INFO_FILENAME = "session_info.json"


def save_session_info(session_dir: Path, **fields: Any) -> Path:
    out_path = session_dir / SESSION_INFO_FILENAME
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(fields, f, ensure_ascii=False, indent=2)
    return out_path
