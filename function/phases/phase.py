from function.phases.run_response import run_response
from function.phases.run_video import play_video


def run_trial(win, keyboard, video_path, question_type, *, lj_handle=None, neon=None, trial_i=1):
    play_video(win, video_path, lj_handle=lj_handle, neon=neon, trial_i=trial_i)

    response, rt = run_response(
        win=win,
        keyboard=keyboard,
        question_type=question_type,
        lj_handle=lj_handle,
        neon=neon,
        trial_i=trial_i,
    )

    return response, rt
