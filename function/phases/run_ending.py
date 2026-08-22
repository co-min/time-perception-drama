# function/phases/run_ending.py

from psychopy import visual

from function.config.settings import (
    TEXT_COLOR, RESPONSE_TEXT_HEIGHT, QUIT_KEY,
    INSTRUCTION_WRAP_WIDTH, ENDING_TEXT,
)


def run_ending(win, keyboard):
    """Show the ending screen and block until QUIT_KEY is pressed.

    Does not close the window or quit itself — the caller's cleanup
    (saving logs, closing devices) still needs to run afterward.
    """

    ending_stim = visual.TextStim(
        win=win,
        text=ENDING_TEXT,
        pos=(0, 0),
        color=TEXT_COLOR,
        height=RESPONSE_TEXT_HEIGHT,
        wrapWidth=INSTRUCTION_WRAP_WIDTH,
    )

    keyboard.clearEvents()

    while True:
        ending_stim.draw()
        win.flip()

        keys = keyboard.getKeys(keyList=[QUIT_KEY], waitRelease=False)
        if keys:
            break
