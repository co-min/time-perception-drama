# Logistic regression: P(Long | Type2) - P(Long | Type1) as a function of Duration
#
# python analysis/regression/plot_difference_by_type.py --sub 1020


## Step 1. Import Libraries
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import patsy
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
from scipy import stats


## Step 2. Load and Inspect Data

parser = argparse.ArgumentParser(
    description="P(Long|Type2) - P(Long|Type1) as a function of duration"
)
parser.add_argument(
    "--sub",
    required=True,  # 반드시 입력
    help="Subject ID",
)
args = parser.parse_args()

SUBJECT_ID = args.sub

CURRENT_FILE = Path(__file__)
PROJECT_ROOT = CURRENT_FILE.parent.parent.parent
DATA_PATH = PROJECT_ROOT / "data" / f"sub-{SUBJECT_ID}" / "ses-1" / "trials.csv"
OUTFILE_ROOT = CURRENT_FILE.parent.parent / "outfile_data"

df = pd.read_csv(DATA_PATH)


## Step 3. Data Preparation (identical to plot_type_regression.py)

def extract_duration(video_name):
    duration_text = video_name.split("s")[0]
    return float(duration_text)


df["duration"] = df["video"].apply(extract_duration)

df = df[["trial", "duration", "type", "theme", "response"]].copy()
df = df.dropna(subset=["duration", "type", "theme", "response"])
df = df[df["response"].isin(["short", "long"])].copy()

df["response_long"] = (df["response"] == "long").astype(int)
df["type"] = df["type"].astype("category")
df["theme"] = df["theme"].astype("category")

print(f"N trials used: {len(df)}")


## Step 4. Logistic Regression
#
# Model 2: additive Type effect (Type-Theme interaction not allowed)
# Model 3: Type x Theme interaction (Type effect allowed to vary by theme)
MODEL_2_FORMULA = 'response_long ~ duration + C(type) + C(theme, Treatment(reference="wildlife"))'
MODEL_3_FORMULA = 'response_long ~ duration + C(type) * C(theme, Treatment(reference="wildlife"))'

model_2 = smf.logit(MODEL_2_FORMULA, data=df).fit()
model_3 = smf.logit(MODEL_3_FORMULA, data=df).fit()

type_terms_2 = [term for term in model_2.params.index if term.startswith("C(type)")]
print("\nNarrative Type effect (Model 2, log-odds scale):")
for term in type_terms_2:
    coef = model_2.params[term]
    ci_lower, ci_upper = model_2.conf_int().loc[term]
    p_value = model_2.pvalues[term]
    print(f"  {term}: coef={coef:.3f}, 95% CI=[{ci_lower:.3f}, {ci_upper:.3f}], p={p_value:.4f}")


## Step 5. P(Long|Type2) - P(Long|Type1): delta-method CI
#
# The Type coefficient is constant on the log-odds scale, but the logistic
# link is nonlinear, so the *probability*-scale gap P(Long|Type2) - P(Long|Type1)
# still changes shape across Duration. We get its standard error via the
# delta method: for diff = sigmoid(eta_2) - sigmoid(eta_1),
#   d(diff)/d(beta) = p2*(1-p2)*x2 - p1*(1-p1)*x1
#   Var(diff) = grad' * Cov(beta) * grad
# so the two curves' shared uncertainty (both come from the same fitted
# model) is correctly propagated, unlike naively combining two separate CIs.
def sigmoid(eta):
    return 1.0 / (1.0 + np.exp(-eta))


def predicted_diff_with_ci(model, pred_df_type1, pred_df_type2, alpha=0.05):
    design_info = model.model.data.orig_exog.design_info
    x1 = np.asarray(patsy.build_design_matrices([design_info], pred_df_type1)[0])
    x2 = np.asarray(patsy.build_design_matrices([design_info], pred_df_type2)[0])

    beta = model.params.values
    cov = model.cov_params().values

    p1 = sigmoid(x1 @ beta)
    p2 = sigmoid(x2 @ beta)
    diff = p2 - p1

    grad = (p2 * (1 - p2))[:, None] * x2 - (p1 * (1 - p1))[:, None] * x1
    var_diff = np.einsum("ij,jk,ik->i", grad, cov, grad)
    se_diff = np.sqrt(var_diff)

    z_crit = stats.norm.ppf(1 - alpha / 2)
    ci_lower = diff - z_crit * se_diff
    ci_upper = diff + z_crit * se_diff
    return diff, ci_lower, ci_upper


duration_range = np.linspace(df["duration"].min(), df["duration"].max(), 200)

out_dir = OUTFILE_ROOT / f"sub-{SUBJECT_ID}"
out_dir.mkdir(parents=True, exist_ok=True)


## Step 6. Visualization

# 6-1. Model 2: single difference curve, Theme held fixed at the reference level
theme_fixed = "wildlife"
pred_type1 = pd.DataFrame({"duration": duration_range, "type": "type1", "theme": theme_fixed})
pred_type2 = pd.DataFrame({"duration": duration_range, "type": "type2", "theme": theme_fixed})

diff_2, ci_lower_2, ci_upper_2 = predicted_diff_with_ci(model_2, pred_type1, pred_type2)

fig1, ax1 = plt.subplots(figsize=(6, 4))
ax1.axhline(0, color="#9ca3af", linewidth=1, linestyle="--", zorder=1)
ax1.fill_between(duration_range, ci_lower_2, ci_upper_2, color="#7c3aed", alpha=0.15, linewidth=0, zorder=2)
ax1.plot(duration_range, diff_2, color="#7c3aed", linewidth=2, zorder=3)

type_term_2 = [t for t in type_terms_2 if "type2" in t][0]
annotation_2 = (
    f"type2 vs type1: coef={model_2.params[type_term_2]:.2f}, "
    f"95% CI=[{model_2.conf_int().loc[type_term_2, 0]:.2f}, {model_2.conf_int().loc[type_term_2, 1]:.2f}], "
    f"p={model_2.pvalues[type_term_2]:.3f}"
)
ax1.text(
    0.02, 0.02, annotation_2, transform=ax1.transAxes, fontsize=8, va="bottom", ha="left",
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.8, edgecolor="#9ca3af"),
)

ax1.set_xlabel("Duration (s)")
ax1.set_ylabel("P(Long | Type2) - P(Long | Type1)")
ax1.set_title(f"Type effect on P(Long) (sub-{SUBJECT_ID})")
fig1.tight_layout()

fig1_path = out_dir / f"sub-{SUBJECT_ID}_diff_by_type_model2.png"
fig1.savefig(fig1_path, dpi=150)
print(f"Saved figure to {fig1_path}")

# 6-2. Model 3: one difference-curve panel per Theme (Type x Theme interaction)
theme_levels = df["theme"].cat.categories.tolist()

fig2, axes2 = plt.subplots(1, len(theme_levels), figsize=(5 * len(theme_levels), 4), sharey=True)
for ax, theme_level in zip(axes2, theme_levels):
    pred_type1_3 = pd.DataFrame({"duration": duration_range, "type": "type1", "theme": theme_level})
    pred_type2_3 = pd.DataFrame({"duration": duration_range, "type": "type2", "theme": theme_level})
    diff_3, ci_lower_3, ci_upper_3 = predicted_diff_with_ci(model_3, pred_type1_3, pred_type2_3)

    ax.axhline(0, color="#9ca3af", linewidth=1, linestyle="--", zorder=1)
    ax.fill_between(duration_range, ci_lower_3, ci_upper_3, color="#7c3aed", alpha=0.15, linewidth=0, zorder=2)
    ax.plot(duration_range, diff_3, color="#7c3aed", linewidth=2, zorder=3)
    ax.set_xlabel("Duration (s)")
    ax.set_title(f"theme = {theme_level}")

axes2[0].set_ylabel("P(Long | Type2) - P(Long | Type1)")
fig2.suptitle(f"Type effect on P(Long) by Theme (sub-{SUBJECT_ID})")
fig2.tight_layout()

fig2_path = out_dir / f"sub-{SUBJECT_ID}_diff_by_type_model3.png"
fig2.savefig(fig2_path, dpi=150)
print(f"Saved figure to {fig2_path}")

plt.show()


## Step 7. Save difference curve values

diff_table = pd.DataFrame({
    "duration": duration_range,
    "diff_model2": diff_2,
    "ci_lower_model2": ci_lower_2,
    "ci_upper_model2": ci_upper_2,
})
diff_results_path = out_dir / f"sub-{SUBJECT_ID}_diff_by_type_results.csv"
diff_table.to_csv(diff_results_path, index=False)
print(f"Saved difference curve values to {diff_results_path}")
