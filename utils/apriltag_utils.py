"""
apriltag_utils.py
------------------
Pupil Labs Neon AprilTag marker stimulus creation.

Public API
----------
    create_neon_apriltags(win, positions, size)
"""

from typing import List, Sequence

from function.config.settings import APRILTAG_POSITIONS, APRILTAG_SIZE


def create_neon_apriltags(
    win,
    positions: Sequence = APRILTAG_POSITIONS,
    size: float = APRILTAG_SIZE,
) -> List:
    """Create AprilTagStim markers at screen edges and keep them visible (AutoDraw).

    Parameters
    ----------
    win       : psychopy.visual.Window
    positions : sequence of (x, y) tuples in 'height' units
    size      : marker size in 'height' units

    Returns
    -------
    List of AprilTagStim instances. The caller must keep a reference so that
    Python does not garbage-collect them while the window is open.

    Raises RuntimeError if psychopy-eyetracker-pupil-labs is not installed.
    """
    try:
        from psychopy_eyetracker_pupil_labs.pupil_labs.stimuli import AprilTagStim
    except ImportError:
        raise RuntimeError(
            "psychopy-eyetracker-pupil-labs not installed. "
            "Run: pip install psychopy-eyetracker-pupil-labs"
        )
    tags = [
        AprilTagStim(
            win=win,
            marker_id=i,
            units="height",
            pos=pos,
            size=(size, size),
            interpolate=False,
            autoLog=False,
        )
        for i, pos in enumerate(positions)
    ]
    for tag in tags:
        tag.setAutoDraw(True)
    print(f"[Neon] {len(tags)} AprilTag markers created and set to AutoDraw.")
    return tags
