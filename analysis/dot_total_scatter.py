# raw data로 dot 찍는 figure
# x axis: raw data duration
# y axis: short, long

# python analysis/dot_total_scatter.py --sub 

# 1. import
import argparse # for command line
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


# 1. Path
# 현재 위치, 프로젝트 파일 위치, 데이터 load 위치, 데이터 save 위치

# Current File 위치
CURRENT_FILE = Path(__file__)
# drama_viodeo project folder
PROJECT_ROOT = CURRENT_FILE.parent.parent
# data folder
DATA_ROOT = PROJECT_ROOT / "data"
# outfile data folder
OUTFILE_ROOT = CURRENT_FILE.parent / "outfile_data"
# CURRENT_FILE.parent = analysis folder 위치


# 2. Command Line

# 2-1.변수에 Object 생성
parser = argparse.ArgumentParser(
    description="Scatter figure using raw data"
)

# 2-2. argument 추가
parser.add_argument(
    "--sub",
    required=True, # 반드시 입력
    help= "Subject ID",
)

# 2-3. 인자 값을 위한 변수 생성 후 실제 terminal에서 입력 읽고 담기
args = parser.parse_args()


# 3. Function
def extract_duration(video_name):
    duration_text = video_name.split("s")[0]
    return float(duration_text)

# 4. Load Data 

# 4-1. data 불러오기 위한 경로 지정
subject_id = args.sub 
data_path = (
    DATA_ROOT
    / f"sub-{subject_id}"
    / "ses-1"
    / "trials.csv"
)

# 4-2. data_path에 있는 data를 읽어오기 -> data frame에 담기
df = pd.read_csv(data_path)

# Extract duration
df["duration"] = df["video"].apply(extract_duration)

# 4-3. mapping short and long
df = df[
    df["response"].isin(["short","long"])
].copy()


response_map = {
    "short" : 0,
    "long" : 1,
} # dictionary로 저장

# df에 "is_long" 추가 -> mapping 한 값을 기준으로 
df["is_long"] = df["response"].map(response_map)



# 5. Scatter
fig, ax = plt.subplots(figsize=(6, 4))

# fig: Graph whole size
# ax: Axes area
# figsize: 가로세로 6, 4 inch

ax.scatter(
    # x axes,
    df["duration"],
    # y axes,
    df["is_long"],

    # data marker 모양
    marker="o", # observed value circle
    # redundency -> density shown
    alpha = 0.5,
    # color
    color="#b53bf6",
    linewidth=2,
)

ax.set_xlabel("Duration (s)")
ax.set_ylabel("Response (0=short, 1=long)")

ax.set_yticks([0, 1])
ax.set_yticklabels(["short", "long"])
ax.set_title(f"Scatter Total data (sub-{subject_id})")
ax.grid(True, alpha=0.3)

fig.tight_layout()


# 6. Save

out_dir = OUTFILE_ROOT / f"sub-{subject_id}"
out_dir.mkdir(parents=True, exist_ok=True)

out_path = out_dir / f"sub-{subject_id}_scatter.png"
fig.savefig(out_path, dpi=150)

print(f"\nSaved figure to {out_path}")