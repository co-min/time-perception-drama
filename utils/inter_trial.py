import gc

from psychopy import visual, core, event

from utils.event_utils import check_escape
from function.io.frame_logger import set_onset, log_frame
from function.io.event_logger import log_event
import random

def run_gaussian_iti(win, global_clock, frame_log, min_t=0.6, max_t=1.8, mean_t=1.2, sd_t=0.3,
                      event_log=None, trial_id=None):
    """지정된 가우시안 분포의 랜덤한 시간 동안 빈 화면(ITI)을 띄우고 로그를 남깁니다."""
    # ITI 시간 계산 (가우시안 분포 및 min/max 클램핑)
    iti_duration = random.gauss(mean_t, sd_t)
    iti_duration = max(min_t, min(iti_duration, max_t))

    phase_clock = core.Clock()
    frame_idx = 0
    flip_time = None

    temp_log_data=[]

    while phase_clock.getTime() < iti_duration:
        flip_time = win.flip()

        if frame_idx == 0:
            frame_log = set_onset(frame_log, flip_time)
            marker = f"iti_onset_dur_{iti_duration:.3f}"
            log_event(event_log, trial_id, "ITI_ONSET", global_clock, flip_time=flip_time)
        else:
            marker = ""

        temp_log_data.append((
            frame_idx,
            flip_time,
            global_clock.getTime(),
            marker
        ))

        frame_idx += 1
        check_escape(win)

    log_event(event_log, trial_id, "ITI_OFFSET", global_clock, flip_time=flip_time)
    return frame_log


