from psychopy import visual, core

from function.config.settings import (
    TEXT_COLOR, RESPONSE_TEXT_HEIGHT, QUIT_KEY, START_KEY,
    BREAK_TEXT,
)


def run_break(win, keyboard):
    break_screen = visual.TextStim(
        win=win,
        text=BREAK_TEXT,
        pos=(0, 0),
        color=TEXT_COLOR,
        height=RESPONSE_TEXT_HEIGHT,
    )

    keyboard.clearEvents()

    while True:
        break_screen.draw()
        win.flip()

        keys = keyboard.getKeys(keyList=[START_KEY, QUIT_KEY], waitRelease=False)
        if not keys:
            continue

        key = keys[0]
        if key.name == QUIT_KEY:
            win.close()
            core.quit()
        elif key.name == START_KEY:
            break
