import time

from psychopy import visual, sound
from function.config.settings import FRAME_RATE, VIDEO_SIZE
from function.io.event_logger import log_event
from function.io.frame_marker import get_shared_marker
from function.io.timing_diagnostics import record_video_diagnostics
from utils.labjack_trigger import send_trigger, TRIG_VIDEO_ONSET, TRIG_VIDEO_OFFSET
from utils.neon_client import section_start_events, section_end_events
from function.phases.data_loader import get_audio_path



def play_video(win, video_path, rec, *, lj_handle=None, neon=None, trial_i=0,
                event_log=None):
    creation_start = time.perf_counter()
    audio = sound.Sound(str(get_audio_path(video_path)))
    movie = visual.MovieStim(
        win,
        filename=str(video_path),
        size=VIDEO_SIZE,
        loop=False,
        noAudio=True,
    )
    movie_creation_time_s = time.perf_counter() - creation_start
    marker = get_shared_marker()

    win.frameIntervals = []
    win.recordFrameIntervals = True

    first_flip = True
    flip_time = None
    decoder_eof_error = False
    while not movie.isFinished:
        if first_flip:
            win.callOnFlip(send_trigger, lj_handle, TRIG_VIDEO_ONSET)
            win.callOnFlip(audio.play)
            if neon is not None:
                neon.call_on_flip(
                    win,
                    section_start_events(trial_i, "VIDEO", first=True),
                    phase="video",
                    trial_index=trial_i,
                )
            if marker is not None:
                marker.trigger()
        try:
            movie.draw()
        except RuntimeError as exc:
            decoder_eof_error = True
            break
        if marker is not None:
            marker.draw()
        flip_time = rec.flip_and_log(win)
        if first_flip:
            log_event(event_log, trial_i, "VIDEO_ONSET", rec.global_clock, flip_time=flip_time)
            first_flip = False
    win.recordFrameIntervals = False
    record_video_diagnostics(win, trial_i, video_path.name, movie_creation_time_s, FRAME_RATE)
    audio.stop()

    send_trigger(lj_handle, TRIG_VIDEO_OFFSET)
    if neon is not None:
        neon.enqueue_events(
            section_end_events(trial_i, "VIDEO_END"),
            metadata={"phase": "video", "trial_index": trial_i},
        )
    log_event(event_log, trial_i, "VIDEO_OFFSET", rec.global_clock, flip_time=flip_time)

    if decoder_eof_error:
        try:
            movie.stop()
        except Exception as cleanup_exc:
            print(
                f"[play_video] WARNING: movie.stop() cleanup failed after "
                f"decoder EOF error (trial_id={trial_i}): {cleanup_exc}"
            )
