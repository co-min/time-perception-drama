from psychopy import visual, sound
from function.config.settings import FRAME_RATE, VIDEO_SIZE
from function.io.event_logger import log_event
from utils.labjack_trigger import send_trigger, TRIG_VIDEO_ONSET, TRIG_VIDEO_OFFSET
from utils.neon_client import section_start_events, section_end_events
from function.phases.data_loader import get_audio_path



def play_video(win, video_path, *, lj_handle=None, neon=None, trial_i=0,
                event_log=None, exp_clock=None): 
    audio = sound.Sound(str(get_audio_path(video_path)))
    movie = visual.MovieStim(
        win,
        filename=str(video_path),
        size=VIDEO_SIZE,
        loop=False,
        noAudio=True,
    )

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
        try:
            movie.draw()
        except RuntimeError as exc:
            decoder_eof_error = True
            break
        flip_time = win.flip()
        if first_flip:
            log_event(event_log, trial_i, "VIDEO_ONSET", exp_clock, flip_time=flip_time)
            first_flip = False
    audio.stop()

    send_trigger(lj_handle, TRIG_VIDEO_OFFSET)
    if neon is not None:
        neon.enqueue_events(
            section_end_events(trial_i, "VIDEO_END"),
            metadata={"phase": "video", "trial_index": trial_i},
        )
    log_event(event_log, trial_i, "VIDEO_OFFSET", exp_clock, flip_time=flip_time)

    if decoder_eof_error:
        try:
            movie.stop()
        except Exception as cleanup_exc:
            print(
                f"[play_video] WARNING: movie.stop() cleanup failed after "
                f"decoder EOF error (trial_id={trial_i}): {cleanup_exc}"
            )
