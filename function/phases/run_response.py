import time

from psychopy import visual, core

from function.config.settings import (
    TEXT_COLOR,
    MAX_RESPONSE_TIME,
    SHORT_KEY,
    LONG_KEY,
    QUIT_KEY,
    PAUSE_KEY,
    CONFIRM_KEY,
    SHORT_TEXT,
    LONG_TEXT,
    BUTTON_SIZE,
    SHORT_POSITION,
    LONG_POSITION,
    SELECTED_BUTTON_COLOR,
    BUTTON_COLOR,
    QUESTION_POSITION,
    RESPONSE_TEXT_HEIGHT,
    RESPONSE_QUESTION,
)

from function.io.event_logger import log_event
from function.io.frame_marker import get_shared_marker
from function.io.timing_diagnostics import record_response_construction
from function.phases.run_pause import run_pause

from utils.labjack_trigger import (
    send_trigger,
    TRIG_RESPONSE_ONSET,
    TRIG_RESP_SHORT,
    TRIG_RESP_LONG,
    TRIG_RESP_TIMEOUT,
)

from utils.neon_client import section_start_events, section_end_events


def run_response(
    win,
    keyboard,
    rec,
    *,
    lj_handle=None,
    neon=None,
    trial_i=0,
    event_log=None,
):

    construction_start = time.perf_counter()

    selected = None
    marker = get_shared_marker()

    # ─────────────────────────────────────────────────────────────
    # Buttons
    # ─────────────────────────────────────────────────────────────

    short_button = visual.Rect(
        win=win,
        width=BUTTON_SIZE[0],
        height=BUTTON_SIZE[1],
        pos=SHORT_POSITION,
        fillColor=BUTTON_COLOR,
    )

    long_button = visual.Rect(
        win=win,
        width=BUTTON_SIZE[0],
        height=BUTTON_SIZE[1],
        pos=LONG_POSITION,
        fillColor=BUTTON_COLOR,
    )

    # ─────────────────────────────────────────────────────────────
    # Button text
    # ─────────────────────────────────────────────────────────────

    short_text = visual.TextStim(
        win=win,
        text=SHORT_TEXT,
        pos=SHORT_POSITION,
        color=TEXT_COLOR,
        height=RESPONSE_TEXT_HEIGHT,
    )

    long_text = visual.TextStim(
        win=win,
        text=LONG_TEXT,
        pos=LONG_POSITION,
        color=TEXT_COLOR,
        height=RESPONSE_TEXT_HEIGHT,
    )

    # ─────────────────────────────────────────────────────────────
    # Question
    # ─────────────────────────────────────────────────────────────

    question = visual.TextStim(
        win=win,
        text=RESPONSE_QUESTION,
        pos=QUESTION_POSITION,
        color=TEXT_COLOR,
        height=RESPONSE_TEXT_HEIGHT,
    )

    record_response_construction(
        trial_i,
        time.perf_counter() - construction_start,
    )

    keyboard.clearEvents()

    first_flip = True
    flip_time = None

    # ─────────────────────────────────────────────────────────────
    # Response loop
    # ─────────────────────────────────────────────────────────────

    while True:

        # First response-screen flip
        if first_flip:
            win.callOnFlip(keyboard.clock.reset)
            win.callOnFlip(
                send_trigger,
                lj_handle,
                TRIG_RESPONSE_ONSET,
            )

            if neon is not None:
                neon.call_on_flip(
                    win,
                    section_start_events(
                        trial_i,
                        "RESPONSE",
                    ),
                    phase="response",
                    trial_index=trial_i,
                )

            if marker is not None:
                marker.trigger()

        # ─────────────────────────────────────────────────────────
        # Selected button color
        # ─────────────────────────────────────────────────────────

        if selected == 0:
            short_button.fillColor = SELECTED_BUTTON_COLOR
            long_button.fillColor = BUTTON_COLOR

        elif selected == 1:
            short_button.fillColor = BUTTON_COLOR
            long_button.fillColor = SELECTED_BUTTON_COLOR

        else:
            short_button.fillColor = BUTTON_COLOR
            long_button.fillColor = BUTTON_COLOR

        # ─────────────────────────────────────────────────────────
        # Draw
        # ─────────────────────────────────────────────────────────

        short_button.draw()
        long_button.draw()

        short_text.draw()
        long_text.draw()

        question.draw()

        if marker is not None:
            marker.draw()

        flip_time = rec.flip_and_log(win)

        if first_flip:
            log_event(
                event_log,
                trial_i,
                "RESPONSE_ONSET",
                rec.global_clock,
                flip_time=flip_time,
            )

            first_flip = False

        # ─────────────────────────────────────────────────────────
        # Timeout
        # ─────────────────────────────────────────────────────────

        if keyboard.clock.getTime() > MAX_RESPONSE_TIME:

            send_trigger(
                lj_handle,
                TRIG_RESP_TIMEOUT,
            )

            if neon is not None:
                neon.enqueue_events(
                    section_end_events(
                        trial_i,
                        "TIMEOUT",
                    ),
                    metadata={
                        "phase": "response",
                        "trial_index": trial_i,
                    },
                )

            log_event(
                event_log,
                trial_i,
                "RESPONSE_TIMEOUT",
                rec.global_clock,
            )

            return "timeout", None

        # ─────────────────────────────────────────────────────────
        # Keyboard input
        # ─────────────────────────────────────────────────────────

        keys = keyboard.getKeys(
            keyList=[
                SHORT_KEY,
                LONG_KEY,
                QUIT_KEY,
                PAUSE_KEY,
                CONFIRM_KEY,
            ],
            waitRelease=False,
        )

        if not keys:
            continue

        key = keys[0]

        # Quit
        if key.name == QUIT_KEY:
            win.close()
            core.quit()

        # Pause
        elif key.name == PAUSE_KEY:
            paused = run_pause(win, event_log=event_log, trial_i=trial_i,
                                global_clock=rec.global_clock)
            keyboard.clock.add(-paused)

        # LEFT → shorter than 1 minute
        elif key.name == SHORT_KEY:
            selected = 0

        # RIGHT → longer than 1 minute
        elif key.name == LONG_KEY:
            selected = 1

        # SPACE → confirm
        elif key.name == CONFIRM_KEY:

            if selected is None:
                continue

            if selected == 0:
                response = "short"
                lj_code = TRIG_RESP_SHORT

            else:
                response = "long"
                lj_code = TRIG_RESP_LONG

            send_trigger(
                lj_handle,
                lj_code,
            )

            if neon is not None:
                neon.enqueue_events(
                    section_end_events(
                        trial_i,
                        response.upper(),
                    ),
                    metadata={
                        "phase": "response",
                        "trial_index": trial_i,
                    },
                )

            log_event(
                event_log,
                trial_i,
                "RESPONSE_CONFIRMED",
                rec.global_clock,
            )

            return response, key.rt


if __name__ == "__main__":

    from psychopy.hardware import keyboard as kb_module
    from function.io.frame_logger import make_frame_log, FrameRecorder

    win = visual.Window(
        size=(1470, 956),
        fullscr=False,
        color="black",
        units="pix",
    )

    keyboard = kb_module.Keyboard()

    rec = FrameRecorder(
        make_frame_log(
            phase="response_test",
            trial_id=0,
            stim_pair_id="",
        ),
        core.Clock(),
    )

    response, rt = run_response(
        win=win,
        keyboard=keyboard,
        rec=rec,
    )

    print("response:", response)
    print("rt:", rt)

    win.close()
    core.quit()