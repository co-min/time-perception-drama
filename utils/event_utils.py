from psychopy import event, visual, core


def check_escape(win: visual.Window) -> None:
    if event.getKeys(keyList=["escape"]):
        print("[DEBUG] QUIT_KEY caught in check_escape (event.getKeys)")  # TEMPORARY diagnostic
        win.close()
        core.quit()
