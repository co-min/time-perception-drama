"""
event_saver.py
--------------
Writes accumulated event-log rows to event_log.csv.
"""

import csv
from pathlib import Path
from typing import Dict, List


EVENT_LOG_FILENAME = "event_log.csv"
FIELDNAMES = ["trial_id", "event", "global_time", "flip_time"]


def save_event_log(rows: List[Dict], save_dir: Path) -> Path:
    save_dir.mkdir(parents=True, exist_ok=True)
    out_path = save_dir / EVENT_LOG_FILENAME
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return out_path