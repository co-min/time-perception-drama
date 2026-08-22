from psychopy import visual, core, event

from utils.event_utils import check_escape, check_pause
from function.io.event_logger import log_event
import random

def run_gaussian_iti(win, rec, min_t=0.6, max_t=1.8, mean_t=1.2, sd_t=0.3,
                      event_log=None, trial_id=None):
    """지정된 가우시안 분포의 랜덤한 시간 동안 빈 화면(ITI)을 띄우고 로그를 남깁니다."""
    # ITI 시간 계산 (가우시안 분포 및 min/max 클램핑)
    iti_duration = random.gauss(mean_t, sd_t)
    iti_duration = max(min_t, min(iti_duration, max_t))

    phase_clock = core.Clock()
    first_flip = True
    flip_time = None

    while phase_clock.getTime() < iti_duration:
        marker = f"iti_onset_dur_{iti_duration:.3f}" if first_flip else ""
        flip_time = rec.flip_and_log(win, marker=marker)

        if first_flip:
            log_event(event_log, trial_id, "ITI_ONSET", rec.global_clock, flip_time=flip_time)
            first_flip = False

        check_escape(win)
        check_pause(win, event_log=event_log, trial_i=trial_id,
                    global_clock=rec.global_clock, phase_clock=phase_clock)

    log_event(event_log, trial_id, "ITI_OFFSET", rec.global_clock, flip_time=flip_time)


