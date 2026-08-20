"""
event_logger.py
----------------
Minimal event-level timing log: one row per named experimental event
(e.g. VIDEO_ONSET, FIXATION_OFFSET). Independent of the frame-level
FrameLog in frame_logger.py. Rows accumulate in a plain list for the
whole session and are written once at the end — same pattern as
NeonEventClient.event_log in utils/neon_client.py.

global_time vs. flip_time
--------------------------
global_time  : exp_clock.getTime() — one shared core.Clock reset once at
               session start. This is the common experiment-relative
               timeline; use it to compare/order events across phases
               and trials.
flip_time    : the raw return value of win.flip() (PsychoPy's own
               monotonicClock), captured only when the event *is*
               itself a flip. Every flip_time in a session comes from
               the same underlying window/clock, so flip_time values
               ARE comparable to each other across phases within a
               session — e.g. FIXATION_ONSET.flip_time -
               VIDEO_ONSET.flip_time is a valid duration.
               What is NOT valid is subtracting a flip_time from a
               global_time (or vice versa) — those two columns have
               different clock origins. Use global_time for
               cross-column comparisons; use flip_time only against
               other flip_time values.
               flip_time is None for events that are not themselves a
               flip: RESPONSE_CONFIRMED and RESPONSE_TIMEOUT are
               detected by polling after the response screen's last
               flip already happened, not at a flip itself. Their
               global_time marks when the response loop detected the
               keypress/timeout. The behavioral `rt` returned by
               run_response.py remains the authoritative response-time
               measure — this log does not change or duplicate it.

Persistence
-----------
event_log is an in-memory list for the whole session and is written to
disk once, in main.py's `finally` block (see event_saver.save_event_log).
A hard process kill before that point loses the unsaved event log for
the whole session, same as the existing NeonEventClient.event_log /
save_neon_event_log behavior. Not addressed here — Step 6 does not
change this.
"""

from typing import Any, Dict, List, Optional


def log_event(
    event_log: Optional[List[Dict[str, Any]]],
    trial_id: Optional[int],
    event_name: str,
    exp_clock,
    flip_time: Optional[float] = None,
) -> None:
    """Append one timestamped row to *event_log* (mutated in place).

    No-op if event_log or exp_clock is None, so callers (and the
    standalone __main__ blocks) work without wiring a session clock.
    """
    if event_log is None or exp_clock is None:
        return
    event_log.append({
        "trial_id":    trial_id,
        "event":       event_name,
        "global_time": round(exp_clock.getTime(), 6),
        "flip_time":   round(flip_time, 6) if flip_time is not None else None,
    })