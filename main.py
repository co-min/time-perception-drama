import random
from datetime import datetime

from psychopy import core
from psychopy.hardware import keyboard as kb_module

from function.config.window_factory import create_window
from function.config import settings as cfg
from function.io.event_saver import save_event_log
from function.io.path_builder import get_session_dir
from function.io.session_saver import save_session_info
from function.io.trial_saver import append_trial_row
from function.phases.data_loader import load_video_paths
from function.phases.phase import run_trial
from function.phases.run_instruction import run_instruction
from function.phases.run_break import run_break
from utils.apriltag_utils import create_neon_apriltags
from utils.labjack_trigger import (
    init_labjack, close_labjack, send_trigger,
    TRIG_EXP_START, TRIG_END, TRIG_Q_SHORT, TRIG_Q_LONG,
)
from utils.neon_client import NeonEventClient, NullNeonClient, save_neon_event_log
from utils.screen_utils import get_subject_info


def main():
    subject_info = get_subject_info()
    SUBJECT_ID   = subject_info["subject_id"]
    SESSION_ID   = subject_info["session"]

    session_dir = get_session_dir(SUBJECT_ID, SESSION_ID)
    existing_outputs = [
        p for p in ("trials.csv", "session_info.json", "event_log.csv", "neon_event_log.csv")
        if (session_dir / p).exists()
    ]
    if existing_outputs:
        raise FileExistsError(
            f"Session directory already contains experimental output {existing_outputs}: "
            f"{session_dir}. Choose a new Session ID rather than overwriting a completed session."
        )

    win      = create_window()
    tags     = create_neon_apriltags(win)  # created once, stays on AutoDraw for entire experiment
    keyboard = kb_module.Keyboard()
    lj       = init_labjack()
    event_log  = []

    neon = (
        NeonEventClient(subject_id=SUBJECT_ID, session_id=SESSION_ID)
        if cfg.USE_NEON else NullNeonClient()
    )

    video_path    = load_video_paths()
    video_paths = video_path
    n_videos       = len(video_paths)
    n_short        = n_videos // 2
    question_types = ["short"] * n_short + ["long"] * (n_videos - n_short)
    random.shuffle(question_types)
    results = []

    save_session_info(
        session_dir,
        subject_id=SUBJECT_ID,
        session_id=SESSION_ID,
        experiment_start_datetime=datetime.now().isoformat(),
        n_trials=n_videos,
        fixation_duration=cfg.FIXATION_DURATION,
        iti_duration=cfg.ITI_DURATION,
        max_response_time=cfg.MAX_RESPONSE_TIME,
        use_neon=cfg.USE_NEON,
    )

    try:
        run_instruction(win, keyboard)

        exp_clock = core.Clock()

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
                event_log=event_log,
                exp_clock=exp_clock,
            )

            trial_row = {
                "trial":         trial_num,
                "video":         video_path.name,
                "question_type": q_type,
                "response":      response,
                "rt":            rt,
            }
            results.append(trial_row)
            append_trial_row(trial_row, session_dir)
            print(f"  → response: {response}, rt: {rt}")

            if trial_num < n_videos:
                if trial_num % 10 == 0:
                    run_break(win, keyboard)

        send_trigger(lj, TRIG_END)

        print("\n=== Results ===")
        for r in results:
            print(r)

    finally:
        neon.close()
        close_labjack(lj)
        save_neon_event_log(session_dir, neon.event_log)
        save_event_log(event_log, session_dir)
        win.close()
        core.quit()


if __name__ == "__main__":
    main()
