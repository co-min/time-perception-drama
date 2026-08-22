from function.config.settings import ITI_DURATION
from function.io.frame_logger import make_frame_log
from function.phases.run_fixation import run_fixation
from function.phases.run_response import run_response
from function.phases.run_trial_number import run_trial_number
from function.phases.run_video import play_video
from utils.inter_trial import run_gaussian_iti


def run_trial(win, keyboard, video_path, question_type, *, lj_handle=None, neon=None, trial_i=1,
            event_log=None, exp_clock=None):  
    run_gaussian_iti(
        win=win,
        global_clock=exp_clock,
        frame_log=make_frame_log(phase="iti", trial_id=trial_i, stim_pair_id=""),
        min_t=ITI_DURATION,
        max_t=ITI_DURATION,
        mean_t=ITI_DURATION,
        sd_t=0,
        event_log=event_log,
        trial_id=trial_i,
    )

    run_trial_number(win, trial_i, event_log=event_log, exp_clock=exp_clock)

    play_video(win, video_path, lj_handle=lj_handle, neon=neon, trial_i=trial_i,
            event_log=event_log, exp_clock=exp_clock) 

    run_fixation(win, keyboard, trial_i=trial_i, event_log=event_log, exp_clock=exp_clock)
    print(f"[DEBUG] fixation done, entering run_response (trial {trial_i})")  

    response, rt = run_response(
        win=win,
        keyboard=keyboard,
        question_type=question_type,
        lj_handle=lj_handle,
        neon=neon,
        trial_i=trial_i,
        event_log=event_log,
        exp_clock=exp_clock,
    )

    return response, rt
