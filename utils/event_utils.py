from psychopy import event, visual, core

from function.config.settings import PAUSE_KEY


def check_escape(win: visual.Window) -> None:
    if event.getKeys(keyList=["escape"]):
        print("[DEBUG] QUIT_KEY caught in check_escape (event.getKeys)")  # TEMPORARY diagnostic
        win.close()
        core.quit()


def check_pause(win: visual.Window, *, event_log=None, trial_i=None, global_clock=None,
                phase_clock=None) -> None:
    """If PAUSE_KEY was pressed, block on the pause screen until resumed.

    If *phase_clock* is given, it is rewound by the pause duration so the
    pause doesn't count against that phase's own timing window.
    """
    if event.getKeys(keyList=[PAUSE_KEY]):
        from function.phases.run_pause import run_pause
        paused = run_pause(win, event_log=event_log, trial_i=trial_i, global_clock=global_clock)
        if phase_clock is not None:
            phase_clock.add(-paused)
