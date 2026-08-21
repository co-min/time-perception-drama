"""
timing_diagnostics.py
----------------------
TEMPORARY diagnostic module (Step 10C). Not part of the permanent
pipeline -- delete this file and its call sites (see run_video.py,
run_response.py and main.py) once the dropped-frame investigation is
done.

Step 10B measured the frame interval right after VIDEO_ONSET, with
win.recordFrameIntervals left on for the whole session. That could not
tell apart three different things:
  1. MovieStim construction/loading time (before the first flip)
  2. actual frame-to-flip intervals during active video playback
  3. gaps caused by other phases (fixation/response stim construction,
     trial-number screen, ITI, etc.)
because every flip in the session -- not just video flips -- was being
timed into the same win.frameIntervals list.

Step 10C narrows the scope: run_video.play_video() now flips
win.recordFrameIntervals on only for the duration of its own draw loop
(see module docstring there), after clearing win.frameIntervals to [].
So by the time record_video_diagnostics() is called, every interval in
win.frameIntervals belongs to that one trial's video playback -- no
other phase can contribute to it.

frame_index / first-interval semantics (verified against
psychopy/visual/window.py)
--------------------------------------------------------------------
Window.flip() does two relevant things, in this order, every call:
  1. runs every queued callOnFlip callback, in registration order
     (window.py ~line 1456)
  2. if recordFrameIntervals is True: computes deltaT = now -
     lastFrameT, then either discards it (if
     recordFrameIntervalsJustTurnedOn) or appends it to
     win.frameIntervals (window.py ~line 1462-1470)
Setting win.recordFrameIntervals = True sets
recordFrameIntervalsJustTurnedOn = True (window.py ~line 910), which
causes the very next flip's deltaT to be discarded rather than
appended. In play_video(), recordFrameIntervals is turned on *before*
the loop starts, so that discarded flip is the VIDEO_ONSET flip itself
-- exactly right, since "time since some flip that happened while
recording was off" is not a meaningful interval. The interval that IS
appended first (win.frameIntervals[0]) is therefore VIDEO_ONSET flip ->
second video flip, i.e. the interval immediately following the
boundary. This is the same quantity Step 10B's mark_boundary() had to
defer to session end to resolve; here it's just intervals[0], captured
inline right after the loop, before the next trial clears the list.
This replaces mark_boundary()/_boundaries from the previous version of
this module -- see record_video_diagnostics()'s first_interval_s /
first_interval_dropped fields.

refreshThreshold safety
------------------------
win.refreshThreshold defaults to a 1.0s sentinel (window.py ~line 622)
and is only replaced with a real per-monitor value as a side effect of
calling the public win.getActualFrameRate() (window.py ~line 659, which
itself reads the private win._monitorFrameRate -- we do not touch that
attribute ourselves). This experiment never calls getActualFrameRate()
(it's a blocking ~1s measurement we don't want to add to the session),
so refreshThreshold is expected to still be at its 1.0s default here.
get_refresh_threshold() falls back to a threshold derived from the
public FRAME_RATE setting whenever refreshThreshold looks like that
untouched sentinel.
"""

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
        "first_interval_dropped": (intervals[0] > threshold) if intervals else None,
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
