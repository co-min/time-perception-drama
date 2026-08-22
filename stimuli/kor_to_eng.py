from pathlib import Path

VIDEO_DIR = Path("stimuli/video")
AUDIO_DIR = Path("stimuli/audio")

def convert_filename(filename: str) -> str:
    """Convert Korean text to English using a predefined mapping."""

    new_name = filename

    new_name = new_name.replace("초", "s")
    new_name = new_name.replace("유형", "type")


    return new_name

def main():
     if not VIDEO_DIR.exists():
          raise FileNotFoundError(f"Video directory not found: {VIDEO_DIR.resolve()}")

     if not AUDIO_DIR.exists():
          raise FileNotFoundError(f"Audio directory not found: {AUDIO_DIR.resolve()}")

     video_files = sorted(VIDEO_DIR.glob("*.mp4"))

     audio_files = sorted(AUDIO_DIR.glob("*.wav"))

     if not video_files:
          print("No .mp4 files found")
          return

     if not audio_files:
               print("No .wav files found")
               return

     print(f"Found {len(video_files)} video files in {VIDEO_DIR.resolve()}")
     print(f"Found {len(audio_files)} auido files in {AUDIO_DIR.resolve()}")

     for old_path in video_files:
          new_name = convert_filename(old_path.name)
          new_path = old_path.with_name(new_name)

          if old_path == new_path:
               print(f"SKIP: {old_path.name}")
               continue
          if new_path.exists():
               print(f"WARNING: target already exists: {new_name}.")

          print(f"{old_path.name}")
          print(f"  -> {new_name}")   

          old_path.rename(new_path)

     for old_path in audio_files:
          new_name = convert_filename(old_path.name)
          new_path = old_path.with_name(new_name)

          if old_path == new_path:
               print(f"SKIP: {old_path.name}")
               continue
          if new_path.exists():
               print(f"WARNING: target already exists: {new_name}.")

          print(f"{old_path.name}")
          print(f"  -> {new_name}")   

          old_path.rename(new_path)

     print("\nRenaming completed.") 


if __name__ == "__main__":
     main()