# python analysis/dot_type1_scatter.py --sub
# scatter, type1
# x axes: duration
# y axes: short or long

# 0. Import
from pathlib import Path
import argparse
import pandas as pd
import matplotlib.pyplot as plt

# 1. Path
CURRENT_FILE = Path(__file__)
PROJECT_ROOT = CURRENT_FILE.parent.parent
DATA_ROOT = PROJECT_ROOT / "data"
OUTFILE_ROOT = CURRENT_FILE.parent / "outfile_data"


# 2. command line
# 2-1.object 생성
parser = argparse.ArgumentParser(
    description="Scatter dots using type1"
)

# 2-2.argument 지정
parser.add_argument(
    "--sub",
    required=True,
    help="Subject ID"
)

# 2-3. terminal에서 불러온 값 변수에 담기
args = parser.parse_args()

# 3. Function
def extract_duration(video_name):
    duration_text=video_name.split("s")[0]
    return float(duration_text)

# 4. Load Data

# 4-1. data 경로 
subject_id = args.sub
data_path = (
    DATA_ROOT
    / f"sub-{subject_id}"
    / "ses-1"
    / "trials.csv"
)

# 4-2. data_path에 있는 data를 df에 담기
df = pd.read_csv(data_path)

# 4-3. column 추가 : duration, type1, mapping short/long
df["duration"] = df["video"].apply(extract_duration)

df = df[
    df["response"].isin(["short", "long"])
].copy()

response_map={
    "short":0,
    "long":1
}

df["is_long"] = df["response"].map(response_map)

# 4-4. type1 만 추출
df = df[df["type"] == "type1"].copy()

# 5. scatter
fig, ax = plt.subplots(figsize=(6,4))

ax.scatter(
    # x axe
    df["duration"],
    df["is_long"],
    marker="o",
    alpha = 0.5,
    color = "#3b82f6",
)

ax.set_xlabel("Duration (s)")
ax.set_ylabel("Response (0=short, 1=long)")

ax.set_yticks([0, 1])
ax.set_yticklabels(["short", "long"])
ax.set_title(f"Raw psychometric data - type1 (sub-{subject_id})")
ax.grid(True, alpha=0.3)

fig.tight_layout()

# 6. save

out_dir = OUTFILE_ROOT / f"sub-{subject_id}"
out_dir.mkdir(parents=True, exist_ok=True)

out_path = out_dir / f"sub-{subject_id}_type1_scatter.png"
fig.savefig(out_path, dpi=150)

print(f"\nSaved figure to {out_path}")