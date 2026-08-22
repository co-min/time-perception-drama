from psychopy import visual, core, event

from function.config.settings import (
    TEXT_COLOR, RESPONSE_TEXT_HEIGHT, QUIT_KEY, START_KEY,
    INSTRUCTION_WRAP_WIDTH, PAUSE_TEXT,
)
from function.io.event_logger import log_event


def run_pause(win, *, event_log=None, trial_i=None, global_clock=None):
    """Block until START_KEY resumes or QUIT_KEY exits the experiment.

    Uses the global event buffer (psychopy.event) rather than a
    hardware.keyboard.Keyboard instance, so it works uniformly from every
    call site, including play_video which doesn't carry a Keyboard.

    Returns the wall-clock duration (seconds) the pause lasted, so the
    caller can rewind its own phase-duration clock by that amount — a
    pause should not eat into a fixation/ITI/response window.
    """
    pause_screen = visual.TextStim(
        win=win,
        text=PAUSE_TEXT,
        pos=(0, 0),
        color=TEXT_COLOR,
        height=RESPONSE_TEXT_HEIGHT,
        wrapWidth=INSTRUCTION_WRAP_WIDTH,
    )

    pause_clock = core.Clock()
    log_event(event_log, trial_i, "PAUSE_ONSET", global_clock)
    event.clearEvents()

    while True:
        pause_screen.draw()
        win.flip()

        keys = event.getKeys(keyList=[START_KEY, QUIT_KEY])

        if QUIT_KEY in keys:
            win.close()
            core.quit()

        if START_KEY in keys:
            break

    log_event(event_log, trial_i, "PAUSE_OFFSET", global_clock)
    return pause_clock.getTime()
