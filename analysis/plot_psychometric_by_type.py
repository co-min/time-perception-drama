# x axis: 5 section of time (53~68)
    # 53-56s, 56-59s, 59-62s, 62-65s, 65-68s
# y axis: P(Long)
# type1 vs type2 비교 (한 figure에 두 곡선)
# excluding 53.14s_type2_AB, 54.02s_type1, 65.06s_type1

import argparse # argparse
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

# 1. load
# 2. exclude
# 3. duration + type
# 4. binning
# 5. type별 P(Long)


## Path
# Current File(plot_psychometric_by_type.py) 위치
CURRENT_FILE = Path(__file__)
# drama_video 프로젝트 폴더
PROJECT_ROOT = CURRENT_FILE.parent.parent
# data folder
DATA_ROOT = PROJECT_ROOT / "data"
# outfile_data folder (analysis/outfile_data)
OUTFILE_ROOT = CURRENT_FILE.parent / "outfile_data"


## Function
def extract_duration(video_name):
    duration_text = video_name.split("s")[0]
    return float(duration_text)


def extract_type(video_name):
    if "type1" in video_name:
        return "type1"
    elif "type2" in video_name:
        return "type2"
    return "unknown"


## Command Line
parser = argparse.ArgumentParser(
    description="Plot psychometric (type1 vs type2)"
)

parser.add_argument(
    "--sub",
    required=True, # 반드시 입력해야 함
    help="Subject ID"
)

args = parser.parse_args() # 실제 terminal에서 입력을 읽기

## Load Data
subject_id = args.sub
data_path = (
    DATA_ROOT
    / f"sub-{subject_id}"
    / "ses-1"
    / "trials.csv"
)

#df에 data_path에 있는 파일 data를 담기(읽어오기)
df = pd.read_csv(data_path)


## Extract duration & type
df["duration"] = df["video"].apply(extract_duration)
df["type"] = df["video"].apply(extract_type)
# apply : 각 행에 한 번씩 적용한다는 것


# Excluded video
EXCLUDED_VIDEOS = [
    "53.14s_type2_AB.mp4",
    "54.02s_type1.mp4",
    "65.06s_type1.mp4",
]

# 제외 목록에 없는 영상만 선택하기
df = df[
    ~df["video"].isin(EXCLUDED_VIDEOS)
].copy()


# timeout 제거

df = df[
    df["response"].isin(["short", "long"])
].copy()


# mapping to 0-1
response_map = {
    "short" : 0,
    "long" : 1,
}

df["is_long"] = df["response"].map(response_map)


## Duration bin 5개 구간 만들기

TIME_BINS = [53, 56, 59, 62, 65, 68]

BIN_LABELS = [
    "53-56",
    "56-59",
    "59-62",
    "62-65",
    "65-68",
]

df["duration_bin"] = pd.cut(
    df["duration"],
    bins=TIME_BINS,
    labels=BIN_LABELS,
    right=False,
)

print(
    df[
        [
            "trial",
            "video",
            "type",
            "duration",
            "duration_bin",
            "response",
            "is_long",
        ]

        ]
)

# Calculate P(Long) per type

p_long_by_type = (
    df.groupby(["type", "duration_bin"], observed=False)["is_long"]
    .mean()
)

print("\nP(Long) by type & duration bin:")
print(p_long_by_type)


n_trials_by_type = (
    df.groupby(["type", "duration_bin"], observed=False)["is_long"]
    .count()
)

print("\nNumber of trials by type & duration bin:")
print(n_trials_by_type)


## Plot
fig, ax = plt.subplots(figsize=(6, 4))

TYPE_STYLES = {
    "type1": {"color": "#3b82f6", "marker": "o"},
    "type2": {"color": "#ef4444", "marker": "s"},
}

for video_type, style in TYPE_STYLES.items():
    if video_type not in p_long_by_type.index.get_level_values("type"):
        continue

    p_long = p_long_by_type.loc[video_type]

    ax.plot(
        p_long.index.astype(str),
        p_long.values,
        marker=style["marker"],
        color=style["color"],
        linewidth=2,
        markersize=8,
        label=video_type,
    )

ax.set_xlabel("Duration bin (s)")
ax.set_ylabel("P(Long)")
ax.set_ylim(0, 1)
ax.set_title(f"Psychometric function: type1 vs type2 (sub-{subject_id})")
ax.grid(True, alpha=0.3)
ax.legend(title="Video type")

fig.tight_layout()


## Save
# outfile_data/sub-{subject_id}/ 폴더에 그림 저장
out_dir = OUTFILE_ROOT / f"sub-{subject_id}"
out_dir.mkdir(parents=True, exist_ok=True)

out_path = out_dir / f"sub-{subject_id}_psychometric_by_type.png"
fig.savefig(out_path, dpi=150)

print(f"\nSaved figure to {out_path}")
