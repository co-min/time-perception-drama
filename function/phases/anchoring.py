# 30 seconds anchoring
# 총 10번의 anchor

# stimuli/image
# total time = 30 sec 
# mean of time은 image 6개가 비슷한 distribution을 갖게
# sum of time(image 1~6) 30 sec

# phase.py - trial 6번 마다 한번씩 anchor 제시

import random
from pathlib import Path
from psychopy import visual, core
from function.io.event_logger import log_event
from utils.event_utils import check_escape, check_pause
from function.config.settings import ANCHOR_TOTAL_DURATION, ANCHOR_IMG_DURATION_SD

# Img size
IMG_SIZE = (1536, 864)

## Path
CURRENT_FILE = Path(__file__)
PROJECT_ROOT = CURRENT_FILE.parent.parent.parent
IMG_ROOT =  PROJECT_ROOT / "stimuli" / "image"


def _select_images():
    """ all image random seqence"""
    image_paths = sorted(
        p for ext in ("*.jpg", "*.jpeg", "*.png") for p in IMG_ROOT.glob(ext)
    )
    random.shuffle(image_paths)
    return image_paths    

# Function
def calculate_img_time(n_images, total_duration=ANCHOR_TOTAL_DURATION,
                    sd=ANCHOR_IMG_DURATION_SD):
    # image/에 있는 stimuli의 제시되는 mean time은 같게
    # phase의 6 trial 마다 한번씩 총 10번 제시될 예정.

    mean_time = total_duration / n_images
    # raw_times = [
    #     max(0.1, random.gauss(mean_time, sd)) for _ in range(n_images)
    # ]

    raw_times = []
    for _ in range(n_images):
        random_time = random.gauss(mean_time,sd)
        random_time = max(0.1, random_time)
        raw_times.append(random_time)
        
    scale = total_duration / sum(raw_times)
    return [t * scale for t in raw_times]

def run_anchor(win, rec, *, trial_i=0, event_log=None):
    """Anchor stimuli/image 전체, total duration 30s 제시"""

    ## step1. 이미지, 각 이미지 제시 시간 준비
    image_paths = _select_images()
    durations =calculate_img_time(len(image_paths))

    log_event(event_log, trial_i, "ANCHOR_ONSET", rec.global_clock)

    ## step2. 이미지 한장씩 제시

    for img_i,(image_path, duration) in enumerate(
        zip(image_paths, durations)
    ):
        # psychopy stimulus
        image_stim = visual.ImageStim(win, image=str(image_path),size=IMG_SIZE)

        # frame log에서 현재 이미비 구분하기 위한 segment
        rec.start_segment(
            phase=f"anchor_img{img_i}"
        )

        # 현재 이미지의 제시 시간을 측정을 위한 clock
        image_clock = core.Clock()

        first_flip = True

        # step3. 지정된 시간 동안 현재 이미지 계속 그리기
        while True:
            # first filp 일어나는 순간부터 시간 측정
            if first_flip:
                win.callOnFlip(image_clock.reset)

            # img를 다음 화면에 그릴 준비
            image_stim.draw()

            # 실제 화면 표시 + frame timing 기록
            flip_time = rec.flip_and_log(win)

            # first flip에서 image onset를 기록
            if first_flip:
                event_name = (
                    f"ANCHOR_IMG{img_i}_ONSET_{image_path.stem}"
                )

                log_event(
                    event_log,
                    trial_i,
                    event_name,
                    rec.global_clock,
                    flip_time=flip_time,
                )

                first_flip=False

                check_escape(win)
                check_pause(
                    win,
                    event_log=event_log,
                    trial_i=trial_i,
                    global_clock=rec.global_clock,
                    phase_clock=image_clock,
                )

            # step4. 지정된 시간이 지나면 현재 이미지 종료
            if image_clock.getTime() >= duration:
                event_name = ( 
                    f"ANCHOR_IMG{img_i}_OFFSET_{image_path.stem}" 
                ) 
                log_event( 
                    event_log, 
                    trial_i, 
                    event_name, 
                    rec.global_clock, 
                    flip_time=flip_time, 
                )

                break
        


    # step5 끝
    log_event(event_log, trial_i, "ANCHOR_OFFSET", rec.global_clock)

