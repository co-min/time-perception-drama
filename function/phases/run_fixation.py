from psychopy import visual, core

from function.config.settings import (
    TEXT_COLOR, FIXATION_DURATION, QUIT_KEY, PAUSE_KEY,
)
from function.io.event_logger import log_event
from function.phases.run_pause import run_pause


def run_fixation(win, keyboard, rec, *, trial_i=0, event_log=None, duration=FIXATION_DURATION):
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
        flip_time = rec.flip_and_log(win)
        if first_flip:
            log_event(event_log, trial_i, "FIXATION_ONSET", rec.global_clock, flip_time=flip_time)
            first_flip = False

        if fixation_clock.getTime() >= duration:
            log_event(event_log, trial_i, "FIXATION_OFFSET", rec.global_clock, flip_time=flip_time)
            break

        keys = keyboard.getKeys(keyList=[QUIT_KEY, PAUSE_KEY], waitRelease=False)
        key_names = {key.name for key in keys}

        if QUIT_KEY in key_names:
            print(f"[DEBUG] QUIT_KEY caught in run_fixation (trial {trial_i})")  # TEMPORARY diagnostic
            win.close()
            core.quit()

        if PAUSE_KEY in key_names:
            paused = run_pause(win, event_log=event_log, trial_i=trial_i,
                                global_clock=rec.global_clock)
            fixation_clock.add(-paused)