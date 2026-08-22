from pathlib import Path


from function.config.settings import STIMULUS_DIR, AUDIO_DIR



def load_video_paths():

    video_paths = sorted(STIMULUS_DIR.glob("*.mp4"))

    return video_paths

def get_audio_path(video_path):
    return AUDIO_DIR / f"{video_path.stem}.wav"

def validate_audio_paths(video_paths):
    missing = [v.name for v in video_paths if not get_audio_path(v).exists()]
    if missing:
        raise FileNotFoundError(f"Missing matching .wav for: {missing}")