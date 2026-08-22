from psychopy import visual, core

from function.config.settings import (
    TEXT_COLOR, TRIAL_NUMBER_DURATION, TRIAL_NUMBER_TEXT_HEIGHT,
    TRIAL_NUMBER_TEXT_TEMPLATE,
)
from function.io.event_logger import log_event
from utils.event_utils import check_escape, check_pause


def run_trial_number(win, trial_i, rec, *, event_log=None):
    """Briefly show 'Trial N' (current trial only, no total) before the video."""
    trial_number_text = visual.TextStim(
        win=win,
        text=TRIAL_NUMBER_TEXT_TEMPLATE.format(n=trial_i),
        pos=(0, 0),
        color=TEXT_COLOR,
        height=TRIAL_NUMBER_TEXT_HEIGHT,
    )

    phase_clock = core.Clock()
    first_flip = True
    flip_time = None
    while True:
        if first_flip:
            win.callOnFlip(phase_clock.reset)

        trial_number_text.draw()
        flip_time = rec.flip_and_log(win)
        if first_flip:
            log_event(event_log, trial_i, "TRIAL_NUMBER_ONSET", rec.global_clock, flip_time=flip_time)
            first_flip = False

        check_escape(win)
        check_pause(win, event_log=event_log, trial_i=trial_i,
                    global_clock=rec.global_clock, phase_clock=phase_clock)

        if phase_clock.getTime() >= TRIAL_NUMBER_DURATION:
            log_event(event_log, trial_i, "TRIAL_NUMBER_OFFSET", rec.global_clock, flip_time=flip_time)
            break
