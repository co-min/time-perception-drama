# x axis: 5 section of time (53~68)
# 53-56s, 56-59s, 59-62s, 62-65s, 65-68s
# y axis: count of videos 

from pathlib import Path
import argparse
import pandas as pd
import matplotlib.pyplot as plt


## Path
CURRENT_FILE = Path(__file__)
PROJECT_ROOT = CURRENT_FILE.parent.parent
DATA_ROOT = PROJECT_ROOT / "data"
OUTFILE_ROOT = CURRENT_FILE.parent / "outfile_data"


## Function
def extract_duration(video_name):
    duration_text = video_name.split("s")[0]
    return float(duration_text)

## Command Line
parser = argparse.ArgumentParser(
    description = "Histogram"
)

parser.add_argument(
    "--sub",
    required=True,
    help="Subject ID"
)

args = parser.parse_args()

## Load Data
subject_id = args.sub
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
    "53.14s_type2_AB.mp4",
    "54.02s_type1.mp4",
    "65.06s_type1.mp4",
]

df = df[
    ~df["video"].isin(EXCLUDED_VIDEOS)
].copy()


df=df[
    df["response"].isin(["short", "long"])
].copy()

BIN_LABELS = [
    "53-56",
    "56-59",
    "59-62",
    "62-65",
    "65-68",
]

## Total video count
total_videos = df.shape[0]
print(f"전체 영상 수: {total_videos}")

## Count videos per duration bin
bin_edges = [53, 56, 59, 62, 65, 68]

counts = []
for low, high in zip(bin_edges[:-1], bin_edges[1:]):
    n = df[(df["duration"] >= low) & (df["duration"] < high)].shape[0]
    counts.append(n)

## Plot
plt.figure(figsize=(8, 5))
plt.bar(BIN_LABELS, counts, edgecolor="black")
plt.xlabel("Duration (s)")
plt.ylabel("Number of videos")
plt.title(f"Video count by duration (sub-{subject_id})")

for i, n in enumerate(counts):
    plt.text(i, n + 0.1, str(n), ha="center")

plt.tight_layout()
plt.show()