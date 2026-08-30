from pathlib import Path

VIDEO_DIR = Path("stimuli/video")
AUDIO_DIR = Path("stimuli/audio")


def counting_num_video():
    video_files = sorted(VIDEO_DIR.glob("*.mp4"))
    num_video = len(video_files)

    return num_video

def counting_num_audio():
    audio_files = sorted(AUDIO_DIR.glob("*.wav"))
    num_audio = len(audio_files)

    return num_audio

def main():
    if not VIDEO_DIR.exists():
        raise FileNotFoundError(f"Video directory not found.")

    num_video = counting_num_video()
    print(f"비디오 개수: {num_video}")

    num_audio = counting_num_audio()
    print(f"audio 개수: {num_audio}")

if __name__ == "__main__":
    main()