"""
trial_saver.py
--------------
Writes one completed video trial to trials.csv immediately, appending
row by row rather than waiting until the end of the experiment.
"""

import csv
from pathlib import Path
from typing import Dict

TRIALS_FILENAME = "trials.csv"
FIELDNAMES = ["trial", "video", "question_type", "response", "rt"]


def append_trial_row(row: Dict, session_dir: Path) -> Path:
    out_path = session_dir / TRIALS_FILENAME
    write_header = not out_path.exists()
    with open(out_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        writer.writerow(row)
    return out_path
