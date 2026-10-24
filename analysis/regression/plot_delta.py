# y axis : short or long
# x axis : delta of difference between trials
# why? 이전 trial이 다음 trial 선택에 영향을 주지는 않을까?
# Q1: 그러니까 즉 이전의 trial이 길다고 느껴졌다면, 다음 trial은 짧다고 판단할 가능성 있음.
# window-size: 3 trials? -> 추후 확장 (현재는 lag-1만 사용)
# distribution: current trial - previous trial 에 대한 분포도

# python analysis/regression/plot_delta.py sub-1020

# neg: 이전 trial - 일 때, 현재 trial에서는 short일 것이다.
# pos: 이전 trial + 일 때, 현재 trial에서는 long일 것이다. 




import argparse # argparse
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

## Path
# Current File(plot_delta.py) 위치: analysis/regression/plot_delta.py
CURRENT_FILE = Path(__file__)
# drama_video 프로젝트 폴더 (regression -> analysis -> project root)
PROJECT_ROOT = CURRENT_FILE.parent.parent.parent
# data folder
DATA_ROOT = PROJECT_ROOT / "data"
# outfile_data folder (analysis/outfile_data, 다른 analysis 스크립트와 공유)
OUTFILE_ROOT = CURRENT_FILE.parent.parent / "outfile_data"


## Function
def extract_duration(video_name):
    duration_text = video_name.split("s")[0]
    return float(duration_text)


def categorize_delta(delta):
    if delta < 0:
        return "negative"
    elif delta == 0:
        return "0"
    else:
        return "positive"


## Command Line
parser = argparse.ArgumentParser(
    description="Plot response (short/long) by section delta between consecutive trials"
)

parser.add_argument(
    "--sub",
    required=False,
    help="Subject ID (e.g. 1020 or sub-1020)"
)

parser.add_argument(
    "sub_pos",
    nargs="?",
    help="Subject ID, positional form (e.g. sub-1020 or 1020)"
)

args = parser.parse_args()

subject_id_raw = args.sub or args.sub_pos
if subject_id_raw is None:
    parser.error("Subject ID is required (--sub 1020 or sub-1020)")

## Load Data
subject_id = subject_id_raw.removeprefix("sub-")
data_path = (
    DATA_ROOT
    / f"sub-{subject_id}"
    / "ses-1"
    / "trials.csv"
)

df = pd.read_csv(data_path)

## Extract duration
df["duration"] = df["video"].apply(extract_duration)

# Excluded video
EXCLUDED_VIDEOS = [

]

df = df[
    ~df["video"].isin(EXCLUDED_VIDEOS)
].copy()

# timeout 제거
df = df[
    df["response"].isin(["short", "long"])
].copy()

# trial 순서 보장 (lag 계산 전에 반드시 정렬)
df = df.sort_values("trial").reset_index(drop=True)


## Section (5 duration bins, 23~38s)
TIME_BINS = [23, 26, 29, 32, 35, 38]

df["section"] = pd.cut(
    df["duration"],
    bins=TIME_BINS,
    labels=False,
    right=False,
)


## Delta section (lag-1: 바로 이전 trial과의 section 차이)
# NOTE: excluded/timeout trial을 제거한 "이후"에 lag를 계산함
#       -> "이전 trial"이 실제로 응답했던 직전 trial이 되도록 보장
df["delta_section"] = df["section"] - df["section"].shift(1)

## Delta duration (lag-1: 바로 이전 trial과의 실제 영상 길이(초) 차이)
df["delta_duration"] = df["duration"] - df["duration"].shift(1)

# 첫 trial은 이전 값이 없으므로 제거
df = df.dropna(subset=["delta_section", "delta_duration"]).copy()

df["delta_category"] = df["delta_section"].apply(categorize_delta)

DELTA_CATEGORIES = ["negative", "0", "positive"]


## Count short / long per delta category
counts = (
    df.groupby(["delta_category", "response"])
    .size()
    .unstack(fill_value=0)
    .reindex(DELTA_CATEGORIES)
    .reindex(columns=["short", "long"], fill_value=0)
)

print(counts)


## Map each trial to a plot coordinate
# x: delta_duration (연속값, 초 단위) - 분포(위)와 산점도(아래)가 x축을 공유
# y: response (short/long) -> binary position
RESPONSE_TO_Y = {"short": 0, "long": 1}

df["plot_x"] = df["delta_duration"]
df["plot_y"] = df["response"].map(RESPONSE_TO_Y)

# jitter: 같은 (delta_duration, response) 근처 trial이 겹쳐서
# 한 점처럼 보이지 않도록 y에 약간의 흔들림을 줌
rng = np.random.default_rng(0)
jitter_y = rng.uniform(-0.08, 0.08, size=len(df))

## Plot
# 위: delta_duration 분포 (histogram + fitted normal/bell curve)
# 아래: response vs delta_duration 산점도
# -> x축(delta_duration)을 공유해서 분포와 개별 trial을 한 그림에서 비교
fig, (ax_dist, ax_scatter) = plt.subplots(
    2,
    1,
    figsize=(6, 6),
    sharex=True,
    gridspec_kw={"height_ratios": [1, 2]},
)

dist_mean = df["delta_duration"].mean()
dist_std = df["delta_duration"].std()

ax_dist.hist(
    df["delta_duration"],
    bins=15,
    density=True,
    color="#3b82f6",
    edgecolor="black",
    alpha=0.6,
)

x_curve = np.linspace(df["delta_duration"].min(), df["delta_duration"].max(), 200)
bell_curve = (
    1 / (dist_std * np.sqrt(2 * np.pi))
) * np.exp(-0.5 * ((x_curve - dist_mean) / dist_std) ** 2)
ax_dist.plot(x_curve, bell_curve, color="#ef4444", linewidth=2)

ax_dist.set_ylabel("Density")
ax_dist.set_title(f"Delta duration distribution & response (sub-{subject_id})")

ax_scatter.scatter(
    df["plot_x"],
    df["plot_y"] + jitter_y,
    color="#3b82f6",
    edgecolor="black",
    linewidth=0.3,
    alpha=0.5,
    s=30,
)

ax_scatter.set_yticks(list(RESPONSE_TO_Y.values()))
ax_scatter.set_yticklabels(list(RESPONSE_TO_Y.keys()))
ax_scatter.set_ylim(-0.5, 1.5)
ax_scatter.set_ylabel("Response")
ax_scatter.set_xlabel("Delta duration (sec, current - previous trial)")

fig.tight_layout()


## Save
out_dir = OUTFILE_ROOT / f"sub-{subject_id}"
out_dir.mkdir(parents=True, exist_ok=True)

out_path = out_dir / f"sub-{subject_id}_delta.png"
fig.savefig(out_path, dpi=150)

print(f"\nSaved figure to {out_path}")
