from psychopy import visual, core

from function.config.settings import (
    TEXT_COLOR, RESPONSE_TEXT_HEIGHT, QUIT_KEY, START_KEY,
    INSTRUCTION_TEXT, FONT, INSTRUCTION_WRAP_WIDTH,
)


def run_instruction(win, keyboard,text):
    """Show the instruction screen and block until START_KEY is pressed.

    QUIT_KEY exits immediately, even if it arrives alongside other keys
    in the same polling cycle.
    """
    instruction = visual.TextStim(
        win=win,
        text=text,
        font=FONT,
        pos=(0, 0),
        color=TEXT_COLOR,
        height=RESPONSE_TEXT_HEIGHT,
        wrapWidth=INSTRUCTION_WRAP_WIDTH,
    )

    keyboard.clearEvents()

    started = False
    while not started:
        instruction.draw()
        win.flip()

        keys = keyboard.getKeys(keyList=[START_KEY, QUIT_KEY], waitRelease=False)
        key_names = {key.name for key in keys}

        if QUIT_KEY in key_names:
            win.close()
            core.quit()
        elif START_KEY in key_names:
            started = True
