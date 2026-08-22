from function.config.settings import ITI_DURATION
from function.io.frame_logger import make_frame_log, get_rows, FrameRecorder
from function.io.frame_saver import save_frame_log
from function.io.path_builder import build_trial_frame_dir
from function.phases.run_fixation import run_fixation
from function.phases.run_response import run_response
from function.phases.run_trial_number import run_trial_number
from function.phases.run_video import play_video
from utils.inter_trial import run_gaussian_iti


def run_trial(win, keyboard, video_path, question_type, *, lj_handle=None, neon=None, trial_i=1,
            event_log=None, exp_clock=None, session_dir=None):
    rec = FrameRecorder(
        make_frame_log(phase="iti", trial_id=trial_i, stim_pair_id=""),
        exp_clock,
    )

    run_gaussian_iti(
        win=win,
        rec=rec,
        min_t=ITI_DURATION,
        max_t=ITI_DURATION,
        mean_t=ITI_DURATION,
        sd_t=0,
        event_log=event_log,
        trial_id=trial_i,
    )

    rec.start_segment(phase="trial_number")
    run_trial_number(win, trial_i, rec, event_log=event_log)

    rec.start_segment(phase="video")
    play_video(win, video_path, rec, lj_handle=lj_handle, neon=neon, trial_i=trial_i,
            event_log=event_log)

    rec.start_segment(phase="fixation")
    run_fixation(win, keyboard, rec, trial_i=trial_i, event_log=event_log)
    print(f"[DEBUG] fixation done, entering run_response (trial {trial_i})")

    rec.start_segment(phase="response")
    response, rt = run_response(
        win=win,
        keyboard=keyboard,
        question_type=question_type,
        rec=rec,
        lj_handle=lj_handle,
        neon=neon,
        trial_i=trial_i,
        event_log=event_log,
    )

    if session_dir is not None:
        trial_dir = build_trial_frame_dir(session_dir, trial_i)
        save_frame_log(get_rows(rec.frame_log), trial_dir)

    return response, rt
