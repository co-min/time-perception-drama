import random
from psychopy import core
from psychopy.hardware import keyboard as kb_module

from function.config.window_factory import create_window
from function.config.settings import DATA_DIR
from function.phases.data_loader import load_video_paths
from function.phases.phase import run_trial
from utils.labjack_trigger import (
    init_labjack, close_labjack, send_trigger,
    TRIG_EXP_START, TRIG_END, TRIG_Q_SHORT, TRIG_Q_LONG,
)
from utils.neon_client import NeonEventClient, NullNeonClient, save_neon_event_log

# ─── 실험 설정 ────────────────────────────────────────────────────────────────
USE_NEON   = False   # True: Neon Companion 연결, False: no-op
SUBJECT_ID = "S01"
SESSION_ID = "01"


def main():
    win      = create_window()
    keyboard = kb_module.Keyboard()
    lj       = init_labjack()

    neon = (
        NeonEventClient(subject_id=SUBJECT_ID, session_id=SESSION_ID)
        if USE_NEON else NullNeonClient()
    )

    video_paths    = load_video_paths()
    question_types = ["short"] * 16 + ["long"] * 16
    random.shuffle(question_types)
    results = []

    try:
        neon.start_session()
        send_trigger(lj, TRIG_EXP_START)

        for trial_num, (video_path, q_type) in enumerate(
            zip(video_paths, question_types), start=1
        ):
            print(f"Trial {trial_num}: {video_path.name} | {q_type}")
            send_trigger(lj, TRIG_Q_SHORT if q_type == "short" else TRIG_Q_LONG)

            response, rt = run_trial(
                win=win,
                keyboard=keyboard,
                video_path=video_path,
                question_type=q_type,
                lj_handle=lj,
                neon=neon,
                trial_i=trial_num,
            )

            results.append({
                "trial":         trial_num,
                "video":         video_path.name,
                "question_type": q_type,
                "response":      response,
                "rt":            rt,
            })
            print(f"  → response: {response}, rt: {rt}")

        send_trigger(lj, TRIG_END)

        print("\n=== Results ===")
        for r in results:
            print(r)

    finally:
        neon.close()
        close_labjack(lj)
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        save_neon_event_log(DATA_DIR, neon.event_log)
        win.close()
        core.quit()


if __name__ == "__main__":
    main()
