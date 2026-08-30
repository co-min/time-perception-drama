import re
from pathlib import Path

import matplotlib.pyplot as plt

VIDEO_DIR = Path("stimuli/video")
OUTPUT_PATH = Path("stimuli/histogram_by_type.png")

# x축 구간 (초 단위, 3초 간격)
BIN_EDGES = [53, 56, 59, 62, 65, 68]
BIN_LABELS = ["53-56s", "56-59s", "59-62s", "62-65s", "65-68s"]

# 파일명에서 초 숫자와 type을 뽑아냄
# 예: "60.03s_type2_AB.mp4" -> seconds=60.03, type="type2"
FILENAME_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)s_(type1|type2)")

TYPE_NAMES = ["type1", "type2"]
TYPE_COLORS = {"type1": "#8B4CB0", "type2": "#DD5252"}


def get_video_seconds_by_type():
    """video 폴더의 각 mp4 파일에서 (초, type)을 뽑아 type별 리스트로 반환"""
    seconds_by_type = {"type1": [], "type2": []}

    for video_path in sorted(VIDEO_DIR.glob("*.mp4")):
        match = FILENAME_PATTERN.match(video_path.name)
        if match:
            seconds = float(match.group(1))
            video_type = match.group(2)
            seconds_by_type[video_type].append(seconds)
        else:
            print(f"경고: {video_path.name}에서 type을 찾지 못했습니다.")

    return seconds_by_type


def count_videos_per_bin(seconds_list):
    """구간별(53-56s, 56-59s, ...) 영상 개수를 세서 리스트로 반환"""
    counts = [0] * len(BIN_LABELS)

    for seconds in seconds_list:
        for i in range(len(BIN_LABELS)):
            lower = BIN_EDGES[i]
            upper = BIN_EDGES[i + 1]
            if lower <= seconds < upper:
                counts[i] += 1
                break
        else:
            print(f"경고: {seconds}s는 구간(53-68s) 밖이라 히스토그램에 포함되지 않았습니다.")

    return counts


def plot_bar_with_labels(ax, counts, video_type):
    """하나의 subplot에 type별 막대그래프를 그림"""
    bars = ax.bar(BIN_LABELS, counts, color=TYPE_COLORS[video_type])

    # 막대 위에 개수 숫자 표시
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            str(int(height)),
            ha="center",
            va="bottom",
        )

    ax.set_xlabel("Time section (s)")
    ax.set_ylabel("Number of videos")
    ax.set_title(video_type)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def plot_histograms(seconds_by_type):
    """type1, type2 히스토그램을 나란히 그려서 하나의 png로 저장"""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)

    for ax, video_type in zip(axes, TYPE_NAMES):
        counts = count_videos_per_bin(seconds_by_type[video_type])
        plot_bar_with_labels(ax, counts, video_type)

    fig.suptitle("Number of videos per time section, by type")
    fig.tight_layout()
    fig.savefig(OUTPUT_PATH, dpi=150)
    print(f"히스토그램 저장 완료: {OUTPUT_PATH}")


def main():
    if not VIDEO_DIR.exists():
        raise FileNotFoundError("Video directory not found.")

    seconds_by_type = get_video_seconds_by_type()

    for video_type in TYPE_NAMES:
        print(f"{video_type}: {len(seconds_by_type[video_type])}개")

    plot_histograms(seconds_by_type)


if __name__ == "__main__":
    main()
