# x axis: 5 section of time (53~68)
    # 53-56s, 56-59s, 59-62s, 62-65s, 65-68s
# y axis: P(Long) 
# excluding 53.14s_type2_AB, 54.02s_type1, 65.06s_type1

# python analysis/plot_psychometric.py --sub 

import argparse # argparse
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

# 1. load
# 2. exclude
# 3. duration
# 4. binnning
# 5. P(Long)


## Path
# Current File(plot_psychometric.py) 위치
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


## Command Line
parser = argparse.ArgumentParser(
    description="Plot psychometric"
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


## Extract duration
df["duration"] = df["video"].apply(extract_duration)
# apply : 각 행에 한 번씩 적용한다는 것, duration만 추출하기


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
            "duration",
            "duration_bin",
            "response",
            "is_long",
        ]

        ]
)

# Calculate P(Long)

p_long = (
    df.groupby("duration_bin", observed=False)["is_long"]
    .mean()
)

print("\nP(Long) by duration bin:")
print(p_long)


n_trials = (
    df.groupby("duration_bin", observed=False)["is_long"]
    .count()
)

print("\nNumber of trials by duration bin:")
print(n_trials)


## Plot
fig, ax = plt.subplots(figsize=(6, 4))

ax.plot(
    p_long.index.astype(str),
    p_long.values,
    marker="o",
    color="#8f3bf6",
    linewidth=2,
    markersize=8,
)

ax.set_xlabel("Duration bin (s)")
ax.set_ylabel("P(Long)")
ax.set_ylim(0, 1)
ax.set_title(f"Psychometric function (sub-{subject_id})")
ax.grid(True, alpha=0.3)

fig.tight_layout()


## Save
# outfile_data/sub-{subject_id}/ 폴더에 그림 저장
out_dir = OUTFILE_ROOT / f"sub-{subject_id}"
out_dir.mkdir(parents=True, exist_ok=True)

out_path = out_dir / f"sub-{subject_id}_psychometric.png"
fig.savefig(out_path, dpi=150)

print(f"\nSaved figure to {out_path}")