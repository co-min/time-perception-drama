from pathlib import Path


from function.config.settings import STIMULUS_DIR



def load_video_paths():

    video_paths = sorted(STIMULUS_DIR.glob("*.mp4"))

    return video_paths