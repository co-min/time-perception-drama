import re
from pathlib import Path

import matplotlib.pyplot as plt

VIDEO_DIR = Path("stimuli/video")
OUTPUT_PATH = Path("stimuli/histogram_by_type.png")

# x축 구간 (파일명에 이미 박혀있는 s1~s5 라벨을 그대로 사용)
BIN_LABELS = ["s1", "s2", "s3", "s4", "s5"]

# 파일명에서 type과 section(s1~s5)을 뽑아냄
FILENAME_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)s_(type1|type2)_(s[1-5])_")

TYPE_NAMES = ["type1", "type2"]
TYPE_COLORS = {"type1": "#8B4CB0", "type2": "#DD5252"}


def get_video_sections_by_type():
    """video 폴더의 각 mp4 파일에서 (section, type)을 뽑아 type별 리스트로 반환"""
    sections_by_type = {"type1": [], "type2": []}

    for video_path in sorted(VIDEO_DIR.rglob("*.mp4")):
        match = FILENAME_PATTERN.match(video_path.name)
        if match:
            video_type = match.group(2)
            section = match.group(3)
            sections_by_type[video_type].append(section)
        else:
            print(f"경고: {video_path.name}에서 type/section을 찾지 못했습니다.")

    return sections_by_type


def count_videos_per_bin(sections_list):
    """구간별 영상 개수를 세서 리스트로 반환"""
    return [sections_list.count(label) for label in BIN_LABELS]


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


def plot_histograms(sections_by_type):
    """type1, type2 히스토그램을 나란히 그려서 하나의 png로 저장"""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)

    for ax, video_type in zip(axes, TYPE_NAMES):
        counts = count_videos_per_bin(sections_by_type[video_type])
        plot_bar_with_labels(ax, counts, video_type)

    fig.suptitle("Number of videos per time section, by type")
    fig.tight_layout()
    fig.savefig(OUTPUT_PATH, dpi=150)
    print(f"Saved histogram: {OUTPUT_PATH}")


def main():
    if not VIDEO_DIR.exists():
        raise FileNotFoundError("Video directory not found.")

    sections_by_type = get_video_sections_by_type()

    for video_type in TYPE_NAMES:
        print(f"{video_type}: {len(sections_by_type[video_type])}개")

    plot_histograms(sections_by_type)


if __name__ == "__main__":
    main()
