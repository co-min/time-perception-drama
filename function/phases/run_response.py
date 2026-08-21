from psychopy import visual, core

from function.config.settings import (
    TEXT_COLOR, MAX_RESPONSE_TIME,
    YES_KEY, NO_KEY,
    QUIT_KEY, PAUSE_KEY, COMFIRM_KEY,
    YES_TEXT, NO_TEXT, BUTTON_SIZE, YES_POSITION, NO_POSITION,
    SELECTED_BUTTON_COLOR, BUTTON_COLOR, QUESTION_POSITION,
    RESPONSE_TEXT_HEIGHT, RESPONSE_TEXT_LONG, RESPONSE_TEXT_SHORT,
)
from function.io.event_logger import log_event
from utils.labjack_trigger import (
    send_trigger,
    TRIG_RESPONSE_ONSET, TRIG_RESP_YES, TRIG_RESP_NO, TRIG_RESP_TIMEOUT,
)
from utils.neon_client import section_start_events, section_end_events


def run_response(win, keyboard, question_type, *, lj_handle=None, neon=None, trial_i=0,
                  event_log=None, exp_clock=None):

    selected = None

    yes_button = visual.Rect(
        win=win,
        width=BUTTON_SIZE[0],
        height=BUTTON_SIZE[1],
        pos=YES_POSITION,
        fillColor=BUTTON_COLOR,
    )

    no_button = visual.Rect(
        win=win,
        width=BUTTON_SIZE[0],
        height=BUTTON_SIZE[1],
        pos=NO_POSITION,
        fillColor=BUTTON_COLOR,
    )

    yes_text = visual.TextStim(
        win=win,
        text=YES_TEXT,
        pos=YES_POSITION,
        color=TEXT_COLOR,
        height=RESPONSE_TEXT_HEIGHT,
    )

    no_text = visual.TextStim(
        win=win,
        text=NO_TEXT,
        pos=NO_POSITION,
        color=TEXT_COLOR,
        height=RESPONSE_TEXT_HEIGHT,
    )

    question_short = visual.TextStim(
        win=win,
        text=RESPONSE_TEXT_SHORT,
        pos=QUESTION_POSITION,
        color=TEXT_COLOR,
        height=RESPONSE_TEXT_HEIGHT,
    )

    question_long = visual.TextStim(
        win=win,
        text=RESPONSE_TEXT_LONG,
        pos=QUESTION_POSITION,
        color=TEXT_COLOR,
        height=RESPONSE_TEXT_HEIGHT,
    )

    if question_type == "short":
        question = question_short
    elif question_type == "long":
        question = question_long
    else:
        raise ValueError(f"Unknown question_type: {question_type!r}")

    keyboard.clearEvents()

    first_flip = True
    flip_time = None
    while True:
        if first_flip:
            win.callOnFlip(keyboard.clock.reset)
            win.callOnFlip(send_trigger, lj_handle, TRIG_RESPONSE_ONSET)
            if neon is not None:
                neon.call_on_flip(
                    win,
                    section_start_events(trial_i, "RESPONSE"),
                    phase="response",
                    trial_index=trial_i,
                )

        if selected == 0:
            yes_button.fillColor = SELECTED_BUTTON_COLOR
            no_button.fillColor = BUTTON_COLOR
        elif selected == 1:
            yes_button.fillColor = BUTTON_COLOR
            no_button.fillColor = SELECTED_BUTTON_COLOR
        else:
            yes_button.fillColor = BUTTON_COLOR
            no_button.fillColor = BUTTON_COLOR

        yes_button.draw()
        no_button.draw()
        yes_text.draw()
        no_text.draw()
        question.draw()

        flip_time = win.flip()
        if first_flip:
            log_event(event_log, trial_i, "RESPONSE_ONSET", exp_clock, flip_time=flip_time)
            first_flip = False

        if keyboard.clock.getTime() > MAX_RESPONSE_TIME:
            send_trigger(lj_handle, TRIG_RESP_TIMEOUT)
            if neon is not None:
                neon.enqueue_events(
                    section_end_events(trial_i, "TIMEOUT"),
                    metadata={"phase": "response", "trial_index": trial_i},
                )
            log_event(event_log, trial_i, "RESPONSE_TIMEOUT", exp_clock)
            return "timeout", None

        keys = keyboard.getKeys(
            keyList=[YES_KEY, NO_KEY, QUIT_KEY, PAUSE_KEY, COMFIRM_KEY],
            waitRelease=False,
        )

        if not keys:
            continue

        key = keys[0]

        if key.name == QUIT_KEY:
            print(f"[DEBUG] QUIT_KEY caught in run_response (trial {trial_i})")  # TEMPORARY diagnostic
            win.close()
            core.quit()

        elif key.name == YES_KEY:
            selected = 0

        elif key.name == NO_KEY:
            selected = 1

        elif key.name == COMFIRM_KEY:
            if selected is None:
                continue
            response = "yes" if selected == 0 else "no"
            lj_code  = TRIG_RESP_YES if selected == 0 else TRIG_RESP_NO
            send_trigger(lj_handle, lj_code)
            if neon is not None:
                neon.enqueue_events(
                    section_end_events(trial_i, response.upper()),
                    metadata={"phase": "response", "trial_index": trial_i},
                )
            log_event(event_log, trial_i, "RESPONSE_CONFIRMED", exp_clock)
            return response, key.rt


if __name__ == "__main__":
    from psychopy.hardware import keyboard as kb_module

    win = visual.Window(
        size=(1470, 956),
        fullscr=False,
        color="black",
        units="pix"
    )

    keyboard = kb_module.Keyboard()

    response, rt = run_response(
        win=win,
        keyboard=keyboard,
        question_type="short",
    )

    print("response:", response)
    print("rt:", rt)

    win.close()
    core.quit()
