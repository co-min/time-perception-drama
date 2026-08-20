from psychopy import visual

from function.config.settings import VIDEO_SIZE
from function.io.event_logger import log_event
from utils.labjack_trigger import send_trigger, TRIG_VIDEO_ONSET, TRIG_VIDEO_OFFSET
from utils.neon_client import section_start_events, section_end_events


def play_video(win, video_path, *, lj_handle=None, neon=None, trial_i=0,
                event_log=None, exp_clock=None):
    movie = visual.MovieStim(
        win,
        filename=str(video_path),
        size=VIDEO_SIZE,
        loop=False,
    )

    first_flip = True
    flip_time = None
    while not movie.isFinished:
        if first_flip:
            win.callOnFlip(send_trigger, lj_handle, TRIG_VIDEO_ONSET)
            if neon is not None:
                neon.call_on_flip(
                    win,
                    section_start_events(trial_i, "VIDEO", first=True),
                    phase="video",
                    trial_index=trial_i,
                )
        movie.draw()
        flip_time = win.flip()
        if first_flip:
            log_event(event_log, trial_i, "VIDEO_ONSET", exp_clock, flip_time=flip_time)
            first_flip = False

    send_trigger(lj_handle, TRIG_VIDEO_OFFSET)
    if neon is not None:
        neon.enqueue_events(
            section_end_events(trial_i, "VIDEO_END"),
            metadata={"phase": "video", "trial_index": trial_i},
        )
    log_event(event_log, trial_i, "VIDEO_OFFSET", exp_clock, flip_time=flip_time)
