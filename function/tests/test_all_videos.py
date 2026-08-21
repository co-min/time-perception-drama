"""
Smoke test: verify every stimulus video loads and plays a few frames.

Does NOT play videos to completion — for each video it opens the file,
draws/flips a handful of frames to confirm decoding actually works, then
moves on to the next one. Prints a pass/fail summary at the end.

Usage:
    python -m function.tests.test_all_videos
"""

import sys
import traceback

from psychopy import visual

from function.config.settings import VIDEO_SIZE, WINDOW_UNITS, BACKGROUND_COLOR
from function.phases.data_loader import load_video_paths

PROBE_FRAMES = 10  # frames to draw+flip per video before moving on


def check_video(win, video_path):
    """Return None on success, or an error string on failure."""
    movie = visual.MovieStim(win, filename=str(video_path), size=VIDEO_SIZE, loop=False)
    try:
        if not movie.duration or movie.duration <= 0:
            return f"suspicious duration: {movie.duration!r}"
        for _ in range(PROBE_FRAMES):
            if movie.isFinished:
                break
            movie.draw()
            win.flip()
        return None
    finally:
        movie.unload()


def main():
    video_paths = load_video_paths()
    if not video_paths:
        print("No videos found.")
        sys.exit(1)

    win = visual.Window(
        size=(960, 540),
        fullscr=False,
        units=WINDOW_UNITS,
        color=BACKGROUND_COLOR,
        colorSpace="hex",
        winType="pyglet",
        screen=0,
    )

    failures = []
    try:
        for i, video_path in enumerate(video_paths, start=1):
            print(f"[{i}/{len(video_paths)}] {video_path.name} ... ", end="", flush=True)
            try:
                error = check_video(win, video_path)
            except Exception:
                error = traceback.format_exc(limit=2)
            if error:
                print("FAIL")
                print(f"    {error}")
                failures.append((video_path.name, error))
            else:
                print("OK")
    finally:
        win.close()

    n_total = len(video_paths)
    n_passed = n_total - len(failures)
    print(f"\n=== {n_passed}/{n_total} videos passed ===")
    if failures:
        print("Failed videos:")
        for name, error in failures:
            print(f"  - {name}: {error.strip().splitlines()[-1]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
