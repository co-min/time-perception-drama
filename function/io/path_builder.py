"""
path_builder.py
---------------
Single source of truth for all result-directory paths.

Directory schema
----------------
data/
  sub-{subject_id}/
    ses-{session_id}/
      trials.csv
      session_info.json
      event_log.csv
      neon_event_log.csv
      trial_{n}/
        frame_log.csv
"""

from pathlib import Path
from function.config.settings import DATA_DIR


def get_subject_dir(subject_id: str) -> Path:
    """Return  data/sub-{subject_id}/"""
    return DATA_DIR / f"sub-{subject_id}"


def build_trial_frame_dir(session_dir: Path, trial_i: int) -> Path:
    """Return (but do not create) the frame-log directory for one video trial.

    save_frame_log() creates the directory itself when it writes the CSV.

    Returns
    -------
    Path  e.g. session_dir / "trial_3"
    """
    return session_dir / f"trial_{trial_i}"


def get_session_dir(subject_id: str, session_id: str) -> Path:
    """Single source of truth for the session save directory.

    Returns (and creates)  data/sub-{subject_id}/ses-{session_id}/
    """
    session_dir = DATA_DIR / f"sub-{subject_id}" / f"ses-{session_id}"
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir
