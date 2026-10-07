import re
from pathlib import Path

import matplotlib.pyplot as plt

VIDEO_DIR = Path("stimuli/video")
OUTPUT_PATH = Path("stimuli/histogram_num.png")

# x축 구간 (초 단위, 3초 간격)
BIN_EDGES = [23, 26, 29, 32, 35, 38]
BIN_LABELS = ["23-26s", "26-29s", "29-32s", "32-35s", "35-38s"]

# 파일명 맨 앞의 초 숫자를 읽어옴
FILENAME_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)s")


def get_video_seconds():
    """video 폴더의 각 mp4 파일에서 초(seconds) 값을 뽑아 리스트로 반환"""
    seconds_list = []

    for video_path in sorted(VIDEO_DIR.glob("*.mp4")):
        match = FILENAME_PATTERN.match(video_path.name)
        if match:
            seconds_list.append(float(match.group(1)))

    return seconds_list


def count_videos_per_bin(seconds_list):
    """구간별 영상 개수를 세서 리스트로 반환"""
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


def plot_histogram(counts):
    """구간별 영상 개수를 막대그래프로 그리고 파일로 저장"""
    fig, ax = plt.subplots(figsize=(8, 5))

    bars = ax.bar(BIN_LABELS, counts, color="#4C72B0")

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
    ax.set_title("Number of videos per time section")

    # 위/오른쪽 테두리 제거 (더 깔끔하게)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    fig.savefig(OUTPUT_PATH, dpi=150)
    print(f"히스토그램 저장 완료: {OUTPUT_PATH}")


def main():
    if not VIDEO_DIR.exists():
        raise FileNotFoundError("Video directory not found.")

    seconds_list = get_video_seconds()
    counts = count_videos_per_bin(seconds_list)

    for label, count in zip(BIN_LABELS, counts):
        print(f"{label}: {count}개")

    plot_histogram(counts)


if __name__ == "__main__":
    main()
