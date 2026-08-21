from psychopy import visual, core

from function.config.settings import (
    TEXT_COLOR, FIXATION_DURATION, QUIT_KEY,
)
from function.io.event_logger import log_event


def run_fixation(win, keyboard, *, trial_i=0, event_log=None, exp_clock=None):
    fixation = visual.TextStim(
        win=win,
        text="+",
        pos=(0, 0),
        color=TEXT_COLOR,
        height=60,
    )

    keyboard.clearEvents()

    fixation_clock = core.Clock()
    first_flip = True
    flip_time = None
    while True:
        if first_flip:
            win.callOnFlip(fixation_clock.reset)

        fixation.draw()
        flip_time = win.flip()
        if first_flip:
            log_event(event_log, trial_i, "FIXATION_ONSET", exp_clock, flip_time=flip_time)
            first_flip = False

        if fixation_clock.getTime() >= FIXATION_DURATION:
            log_event(event_log, trial_i, "FIXATION_OFFSET", exp_clock, flip_time=flip_time)
            break

        if keyboard.getKeys(keyList=[QUIT_KEY], waitRelease=False):
            print(f"[DEBUG] QUIT_KEY caught in run_fixation (trial {trial_i})")  # TEMPORARY diagnostic
            win.close()
            core.quit()