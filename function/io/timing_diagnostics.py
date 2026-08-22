
import json
import statistics
from pathlib import Path
from typing import Any, Dict, List, Optional

TIMING_DIAGNOSTICS_FILENAME = "timing_diagnostics.json"

_video_records: List[Dict[str, Any]] = []
_response_construction_records: List[Dict[str, Any]] = []


def get_refresh_threshold(win, fallback_hz: float) -> float:
    """Safe accessor for win.refreshThreshold; never reads win._monitorFrameRate."""
    threshold = getattr(win, "refreshThreshold", None)
    if threshold and threshold < 1.0:
        return threshold
    return (1.0 / fallback_hz) * 1.2


def record_video_diagnostics(
    win, trial_id: int, video_name: str, movie_creation_time_s: float, fallback_hz: float,
) -> Dict[str, Any]:
    """Snapshot win.frameIntervals right after a video's playback loop ends.

    Caller (run_video.play_video) must have reset win.frameIntervals to []
    and set win.recordFrameIntervals = True immediately before the loop, and
    must call this before the next trial resets the list again -- so every
    value here was measured strictly between two flips inside that one
    video's draw loop.
    """
    threshold = get_refresh_threshold(win, fallback_hz)
    intervals = list(win.frameIntervals)
    dropped = [iv for iv in intervals if iv > threshold]

    record = {
        "trial_id": trial_id,
        "video_name": video_name,
        "movie_creation_time_s": round(movie_creation_time_s, 6),
        "n_video_frame_intervals": len(intervals),
        "median_video_frame_interval_s": round(statistics.median(intervals), 6) if intervals else None,
        "max_video_frame_interval_s": round(max(intervals), 6) if intervals else None,
        "n_video_dropped_frames": len(dropped),
        "refresh_threshold_s": round(threshold, 6),
        # Folds in the old VIDEO_ONSET-next-frame diagnostic: intervals[0] is
        # the flip-to-flip gap right after the VIDEO_ONSET flip (see module
        # docstring).
        "first_interval_s": round(intervals[0], 6) if intervals else None,
        "first_interval_dropped": bool(intervals[0] > threshold) if intervals else None,
    }
    _video_records.append(record)
    return record


def record_response_construction(trial_id: int, duration_s: float) -> None:
    """Record how long response-stimulus construction took for one trial.

    Called while win.recordFrameIntervals is off (construction happens
    before the response loop's first flip), so this is wall-clock time only,
    not a frame-interval measurement.
    """
    _response_construction_records.append({
        "trial_id": trial_id,
        "response_construction_time_s": round(duration_s, 6),
    })


def save_timing_diagnostics(save_dir: Path) -> Optional[Path]:
    """Write accumulated video/response-construction diagnostics to disk.

    Must be called after all trials are done (still before win.close()).
    """
    if not _video_records and not _response_construction_records:
        return None

    out_data = {
        "video_diagnostics": _video_records,
        "response_construction": _response_construction_records,
    }

    save_dir.mkdir(parents=True, exist_ok=True)
    out_path = save_dir / TIMING_DIAGNOSTICS_FILENAME
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_data, f, ensure_ascii=False, indent=2)
    return out_path
