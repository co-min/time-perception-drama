# y axis : P(long) - logisitic regression
# y = beta1 * X1(acutal duration section) + beta2 * X2(delta) + error

# python analysis/regression/plot_delta_regression.py sub-1020


import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

## Path
# Current File(plot_delta_regression.py) 위치: analysis/regression/plot_delta_regression.py
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


## Command Line
parser = argparse.ArgumentParser(
    description="Logistic regression: p(long) ~ section + delta_section"
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

# timeout 제거
df = df[
    df["response"].isin(["short", "long"])
].copy()

# trial 순서 보장 (lag 계산 전에 반드시 정렬)
df = df.sort_values("trial").reset_index(drop=True)


## Section (5 duration bins, 23~38s) - plot_delta.py와 동일 기준
TIME_BINS = [23, 26, 29, 32, 35, 38]

df["section"] = pd.cut(
    df["duration"],
    bins=TIME_BINS,
    labels=False,
    right=False,
)

## Delta section (lag-1: 바로 이전 trial과의 section 차이)
# NOTE: timeout 제거 "이후"에 lag를 계산함 -> "이전 trial"이 실제 응답했던 직전 trial이 되도록 보장
df["delta_section"] = df["section"] - df["section"].shift(1)

# 첫 trial은 이전 값이 없으므로 제거
df = df.dropna(subset=["section", "delta_section"]).copy()
df["section"] = df["section"].astype(int)
df["delta_section"] = df["delta_section"].astype(int)

## Binary response (long = 1, short = 0)
df["response_long"] = (df["response"] == "long").astype(int)


## Fit logistic regression (GLM, Binomial family)
# y = beta1 * X1(section) + beta2 * X2(delta_section) + error
model = smf.glm(
    "response_long ~ section + delta_section",
    data=df,
    family=sm.families.Binomial(),
).fit()

print(model.summary())


## Prediction curve: X1(section)을 평균에 고정, X2(delta_section)만 변화
section_fixed = df["section"].mean()
delta_range = np.linspace(df["delta_section"].min(), df["delta_section"].max(), 200)

pred_df = pd.DataFrame({
    "section": section_fixed,
    "delta_section": delta_range,
})

pred = model.get_prediction(pred_df).summary_frame(alpha=0.05)
# columns: mean, mean_se, mean_ci_lower, mean_ci_upper (probability scale)


## Observed p(long) per delta_section (정수값이라 bin 없이 값별로 집계)
observed = (
    df.groupby("delta_section")["response_long"]
    .agg(n="size", p_long="mean")
    .reset_index()
)
observed["se"] = np.sqrt(observed["p_long"] * (1 - observed["p_long"]) / observed["n"])
observed["ci"] = 1.96 * observed["se"]

print(observed)


## Plot
fig, ax = plt.subplots(figsize=(7, 5))

# jitter: 실제 binary response를 배경에 살짝 흔들어서 표시
rng = np.random.default_rng(0)
jitter_x = rng.uniform(-0.1, 0.1, size=len(df))
jitter_y = rng.uniform(-0.03, 0.03, size=len(df))

ax.scatter(
    df["delta_section"] + jitter_x,
    df["response_long"] + jitter_y,
    color="#94a3b8",
    alpha=0.35,
    s=20,
    label="trial (jittered)",
)

# fitted curve + 95% CI band
ax.plot(
    delta_range,
    pred["mean"],
    color="#ef4444",
    linewidth=2,
    label="fitted p(long)",
)
ax.fill_between(
    delta_range,
    pred["mean_ci_lower"],
    pred["mean_ci_upper"],
    color="#ef4444",
    alpha=0.15,
)

# observed proportion per delta_section
ax.errorbar(
    observed["delta_section"],
    observed["p_long"],
    yerr=observed["ci"],
    fmt="o",
    color="#1d4ed8",
    ecolor="#1d4ed8",
    markersize=6,
    capsize=3,
    label="observed p(long)",
)

ax.axhline(0.5, color="gray", linestyle="--", linewidth=0.8)
ax.set_ylim(-0.05, 1.05)
ax.set_xlabel("Delta section (current - previous trial)")
ax.set_ylabel("p(long)")
ax.set_title(
    f"Logistic regression: p(long) vs delta_section (sub-{subject_id})\n"
    f"y = β1·section + β2·delta_section (section fixed at mean={section_fixed:.2f})"
)
ax.legend(loc="lower right", fontsize=8)

fig.tight_layout()


## Save
out_dir = OUTFILE_ROOT / f"sub-{subject_id}"
out_dir.mkdir(parents=True, exist_ok=True)

out_path = out_dir / f"sub-{subject_id}_delta_regression.png"
fig.savefig(out_path, dpi=150)

print(f"\nSaved figure to {out_path}")

## Save coefficients CSV (beta, se, z, p-value, 95% CI per term)
coef_df = model.summary2().tables[1].reset_index().rename(columns={"index": "term"})
coef_df.columns = ["term", "coef", "std_err", "z", "p_value", "ci_lower", "ci_upper"]
coef_df["significant_p05"] = coef_df["p_value"] < 0.05

coef_path = out_dir / f"sub-{subject_id}_delta_regression_coefficients.csv"
coef_df.to_csv(coef_path, index=False)
print(f"Saved coefficients to {coef_path}")

## Save observed p(long) per delta_section CSV
observed_path = out_dir / f"sub-{subject_id}_delta_regression_observed.csv"
observed.to_csv(observed_path, index=False)
print(f"Saved observed table to {observed_path}")


## Save interpretation TXT
def term_label(term):
    return {
        "Intercept": "Intercept",
        "section": "section",
        "delta_section": "delta_section",
    }.get(term, term)


def interpret_term(row):
    sig = "유의함 (p < 0.05)" if row["p_value"] < 0.05 else "유의하지 않음 (p >= 0.05)"
    direction = "증가" if row["coef"] > 0 else "감소"
    return (
        f"- {term_label(row['term'])}: beta = {row['coef']:.4f}, "
        f"SE = {row['std_err']:.4f}, z = {row['z']:.3f}, p = {row['p_value']:.4f}, "
        f"95% CI = [{row['ci_lower']:.3f}, {row['ci_upper']:.3f}] -> {sig}\n"
        f"  (1단위 증가 시 p(long)의 로그오즈가 {abs(row['coef']):.4f}만큼 {direction})"
    )


lines = []
lines.append(f"Subject: sub-{subject_id}")
lines.append(f"Model: response_long ~ section + delta_section (GLM, Binomial/Logit)")
lines.append(f"N observations: {int(model.nobs)}")
lines.append(f"Log-Likelihood: {model.llf:.3f}")
lines.append(f"Pseudo R-squ. (McFadden): {1 - (model.deviance / model.null_deviance):.4f}")
lines.append("")
lines.append("[Coefficients]")
for _, row in coef_df.iterrows():
    lines.append(interpret_term(row))
lines.append("")

sig_terms = coef_df[(coef_df["term"] != "Intercept") & (coef_df["significant_p05"])]["term"].tolist()
nonsig_terms = coef_df[(coef_df["term"] != "Intercept") & (~coef_df["significant_p05"])]["term"].tolist()

lines.append("[요약 / Summary]")
if sig_terms:
    lines.append(f"- 유의미한 예측변수: {', '.join(term_label(t) for t in sig_terms)}")
else:
    lines.append("- 유의미한 예측변수 없음")
if nonsig_terms:
    lines.append(f"- 유의하지 않은 예측변수: {', '.join(term_label(t) for t in nonsig_terms)}")

lines.append("")
lines.append("[Observed p(long) by delta_section]")
for _, row in observed.iterrows():
    lines.append(
        f"- delta_section={int(row['delta_section'])}: n={int(row['n'])}, "
        f"p(long)={row['p_long']:.3f} (95% CI +-{row['ci']:.3f})"
    )

summary_path = out_dir / f"sub-{subject_id}_delta_regression_summary.txt"
summary_path.write_text("\n".join(lines), encoding="utf-8")
print(f"Saved interpretation to {summary_path}")
