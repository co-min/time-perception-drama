# Logistic regression: how Duration, Narrative Type, and Theme affect P(Long)
#
# python analysis/regression/plot_type_regression.py --sub 1020


## Step 1. Import Libraries
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
from scipy import stats


## Step 2. Load and Inspect Data

# 2-1. 변수에 Object 생성
parser = argparse.ArgumentParser(
    description="Logistic regression: P(Long) ~ duration + type + theme"
)

# 2-2. argument 추가
parser.add_argument(
    "--sub",
    required=True,  # 반드시 입력
    help="Subject ID",
)

# 2-3. 인자 값을 위한 변수 생성 후 실제 terminal에서 입력 읽고 담기
args = parser.parse_args()

SUBJECT_ID = args.sub

CURRENT_FILE = Path(__file__)
PROJECT_ROOT = CURRENT_FILE.parent.parent.parent
DATA_PATH = PROJECT_ROOT / "data" / f"sub-{SUBJECT_ID}" / "ses-1" / "trials.csv"
# outfile_data folder (analysis/outfile_data, 다른 analysis 스크립트와 공유)
OUTFILE_ROOT = CURRENT_FILE.parent.parent / "outfile_data"

df = pd.read_csv(DATA_PATH)

print("First 5 rows:")
print(df.head())

print("\nColumn names:", list(df.columns))

print("\nData info:")
print(df.info())





## Step 3. Data Preparation

# 3-1. The CSV has no standalone "duration" column, but the video filename
# starts with the duration in seconds (e.g. "29.01s_type2_..."), so we parse it.
def extract_duration(video_name):
    duration_text = video_name.split("s")[0]
    return float(duration_text)


df["duration"] = df["video"].apply(extract_duration)

# 3-2. Keep only the columns needed for this analysis
df = df[["trial", "duration", "type", "theme", "response"]].copy()

# 3-3. Drop rows with missing values (e.g. "timeout" trials have no usable response)
df = df.dropna(subset=["duration", "type", "theme", "response"])
df = df[df["response"].isin(["short", "long"])].copy()

# 3-4. Code the response as 0 (short) / 1 (long) -> this is the dependent variable
df["response_long"] = (df["response"] == "long").astype(int)

# 3-5. Treat Narrative Type and Theme as categorical variables
df["type"] = df["type"].astype("category")
df["theme"] = df["theme"].astype("category")
theme_levels = df["theme"].cat.categories.tolist()

print("\nPrepared data (first 5 rows):")
print(df.head())
print(f"\nN trials used: {len(df)}")


## Step 4. Logistic Regression
#
# Model specifications are kept as plain strings so they are easy to modify.
MODEL_1_FORMULA = "response_long ~ duration"
MODEL_2_FORMULA = 'response_long ~ duration + C(type) + C(theme, Treatment(reference="wildlife"))'
# Model 3 adds a Type x Theme interaction, so the Type effect is allowed to
# differ across themes instead of being forced to be the same everywhere.
MODEL_3_FORMULA = 'response_long ~ duration + C(type) * C(theme, Treatment(reference="wildlife"))'

# .fit() estimates the model coefficients (maximum likelihood) from the data.
model_1 = smf.logit(MODEL_1_FORMULA, data=df).fit()
model_2 = smf.logit(MODEL_2_FORMULA, data=df).fit()
model_3 = smf.logit(MODEL_3_FORMULA, data=df).fit()


## Step 5. Statistical Results

# .summary() prints coefficients, standard errors, z-values, p-values, and CIs.
print("\n=== Model 1: response_long ~ duration ===")
print(model_1.summary())

print("\n=== Model 2: response_long ~ duration + C(type) + C(theme) ===")
print(model_2.summary())

print("\n=== Model 3: response_long ~ duration + C(type) * C(theme) ===")
print(model_3.summary())

# Extract the same numbers into a clean table for easier reading.
results_table = pd.DataFrame(
    {
        "coef": model_2.params,
        "std_err": model_2.bse,
        "p_value": model_2.pvalues,
        "ci_lower": model_2.conf_int()[0],
        "ci_upper": model_2.conf_int()[1],
    }
)
print("\nModel 2 coefficient table:")
print(results_table)

# 5-2. Isolate the Narrative Type coefficient(s) specifically, since this is
# the term the Model 2 plot (type1 vs type2) is testing for significance.
type_terms = [term for term in model_2.params.index if term.startswith("C(type)")]
print("\nNarrative Type effect (Model 2):")
for term in type_terms:
    coef = model_2.params[term]
    ci_lower, ci_upper = model_2.conf_int().loc[term]
    p_value = model_2.pvalues[term]
    significant = "significant" if p_value < 0.05 else "not significant"
    print(
        f"  {term}: coef={coef:.3f}, 95% CI=[{ci_lower:.3f}, {ci_upper:.3f}], "
        f"p={p_value:.4f} -> {significant} at alpha=0.05"
    )

# 5-2b. Model 3 includes a Type x Theme interaction, so the type1-vs-type2
# gap is a different linear combination of coefficients in each theme panel:
# for the reference theme (wildlife) it's just C(type)[T.type2]; for the
# other themes it's C(type)[T.type2] + the matching interaction term. Use
# t_test() with a contrast vector to get the CI/p-value for that combined
# effect in each theme, so we can tell whether an overlapping pair of lines
# (as in the wildlife panel) reflects a genuine near-zero effect or just a
# plotting artifact.
type_term = "C(type)[T.type2]"
interaction_term_by_theme = {}
for term in model_3.params.index:
    if term.startswith(f"{type_term}:C(theme"):
        theme_name = term.split("[T.")[-1].rstrip("]")
        interaction_term_by_theme[theme_name] = term

model3_type_effects = {}
print("\nNarrative Type effect per Theme (Model 3, type2 vs type1):")
for theme_level in theme_levels:
    contrast = pd.Series(0.0, index=model_3.params.index)
    contrast[type_term] = 1.0
    if theme_level in interaction_term_by_theme:
        contrast[interaction_term_by_theme[theme_level]] = 1.0
    test_result = model_3.t_test(contrast.values)
    coef = test_result.effect.item()
    p_value = test_result.pvalue.item()
    ci_lower, ci_upper = test_result.conf_int()[0]
    significant = "significant" if p_value < 0.05 else "not significant"
    model3_type_effects[theme_level] = (coef, ci_lower, ci_upper, p_value)
    print(
        f"  theme={theme_level}: coef={coef:.3f}, 95% CI=[{ci_lower:.3f}, {ci_upper:.3f}], "
        f"p={p_value:.4f} -> {significant} at alpha=0.05"
    )

# 5-1. Combine Model 1 and Model 2 coefficients into a single table, so the
# full result set can be saved to one CSV instead of only printed here.
def coef_table(model, model_name):
    table = pd.DataFrame(
        {
            "coef": model.params,
            "std_err": model.bse,
            "p_value": model.pvalues,
            "ci_lower": model.conf_int()[0],
            "ci_upper": model.conf_int()[1],
        }
    ).reset_index().rename(columns={"index": "term"})
    table.insert(0, "model", model_name)
    table["aic"] = model.aic
    return table


combined_results = pd.concat(
    [
        coef_table(model_1, "model_1_duration_only"),
        coef_table(model_2, "model_2_duration_type_theme"),
        coef_table(model_3, "model_3_duration_type_theme_interaction"),
    ],
    ignore_index=True,
)

out_dir = OUTFILE_ROOT / f"sub-{SUBJECT_ID}"
out_dir.mkdir(parents=True, exist_ok=True)
results_path = out_dir / f"sub-{SUBJECT_ID}_type_regression_results.csv"
combined_results.to_csv(results_path, index=False)
print(f"\nSaved combined results to {results_path}")

# How to interpret these values:
# - coef: change in log-odds of responding "Long" per 1-unit increase in the
#   predictor (or vs. the reference category, for categorical variables).
#   Positive -> higher P(Long); negative -> lower P(Long).
# - std_err: uncertainty of the coefficient estimate.
# - p_value: < 0.05 is usually considered statistically significant.
# - ci_lower / ci_upper: 95% confidence interval for the coefficient; if this
#   range does not include 0, the effect is significant at the 0.05 level.


## Step 6. Visualization

# 6-1. Observed responses vs. fitted logistic curve (Model 1: duration only)
duration_range = np.linspace(df["duration"].min(), df["duration"].max(), 200)
pred_df_1 = pd.DataFrame({"duration": duration_range})

# .predict() returns the model's predicted P(Long) for new data.
predicted_p_long_1 = model_1.predict(pred_df_1)

fig1, ax1 = plt.subplots(figsize=(6, 4))
ax1.scatter(
    df["duration"], df["response_long"],
    alpha=0.4, color="#1d4ed8", label="observed response",
)
ax1.plot(
    duration_range, predicted_p_long_1,
    color="#ef4444", linewidth=2, label="fitted P(Long)",
)
ax1.set_xlabel("Duration (s)")
ax1.set_ylabel("P(Long)")
ax1.set_yticks([0, 1])
ax1.set_title(f"Model 1: P(Long) vs Duration (sub-{SUBJECT_ID})")
ax1.legend(loc="center right")
fig1.tight_layout()

fig1_path = out_dir / f"sub-{SUBJECT_ID}_type_regression_model1.png"
fig1.savefig(fig1_path, dpi=150)
print(f"Saved figure to {fig1_path}")

# 6-2. Predicted P(Long) for Narrative Type 1 vs Type 2 (Model 2, averaged over Themes)
duration_points = np.quantile(df["duration"], [0.1, 0.3, 0.5, 0.7, 0.9])
x_offsets = {"type1": -0.2, "type2": 0.2}  # keeps the two sets of error bars apart

fig2, ax2 = plt.subplots(figsize=(6, 4))
# type1/type2 also get distinct line styles (not just color), so the two
# curves stay distinguishable even where they nearly overlap.
type_styles = [("type1", "#3b82f6", "-"), ("type2", "#ef4444", "--")]
for type_level, color, linestyle in type_styles:
    # average=True predicts every trial with its observed theme and averages
    # them, so no single theme has to be chosen. Its 95% CI uses the delta method.
    pred_summary_2 = pd.DataFrame([
        model_2.get_prediction(
            df.assign(duration=duration_point, type=type_level), average=True
        ).summary_frame(alpha=0.05).iloc[0]
        for duration_point in duration_points
    ])
    predicted_p_long_2 = pred_summary_2["predicted"].to_numpy()
    # Delta-method limits can fall outside [0, 1], so clip them to valid probabilities.
    ci_lower_2 = pred_summary_2["ci_lower"].clip(0, 1).to_numpy()
    ci_upper_2 = pred_summary_2["ci_upper"].clip(0, 1).to_numpy()
    ax2.errorbar(
        duration_points + x_offsets[type_level], predicted_p_long_2,
        yerr=[predicted_p_long_2 - ci_lower_2, ci_upper_2 - predicted_p_long_2],
        color=color, linestyle=linestyle, linewidth=2, marker="o", capsize=4, label=type_level,
    )

# Annotate the plot with the Narrative Type coefficient's CI and p-value
# (computed in Step 5) so the statistical basis for the two lines is visible
# alongside them, not just in the console output.
type_annotation_lines = [
    f"{term.replace('C(type)', 'type')}: "
    f"coef={model_2.params[term]:.2f}, "
    f"95% CI=[{model_2.conf_int().loc[term, 0]:.2f}, {model_2.conf_int().loc[term, 1]:.2f}], "
    f"p={model_2.pvalues[term]:.3f}"
    for term in type_terms
]
ax2.text(
    0.98, 0.02, "\n".join(type_annotation_lines),
    transform=ax2.transAxes, fontsize=8, va="bottom", ha="right",
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.8, edgecolor="#9ca3af"),
)

ax2.set_xlabel("Duration (s)")
ax2.set_ylabel("P(Long)")
ax2.set_ylim(0, 1)
ax2.set_title("Model 2: P(Long) by Narrative Type (averaged over themes)")
ax2.legend(title="Narrative Type", loc="upper left")
fig2.tight_layout()

fig2_path = out_dir / f"sub-{SUBJECT_ID}_type_regression_model2.png"
fig2.savefig(fig2_path, dpi=150)
print(f"Saved figure to {fig2_path}")

# 6-3. Predicted P(Long) for Type 1 vs Type 2, one panel per Theme (Model 3)
# Because Model 3 includes a Type x Theme interaction, the gap between the
# type1 and type2 curves is allowed to change across panels; if the gap looks
# about the same (or the lines overlap) in a panel, that reflects a genuinely
# weak/near-zero Type effect in that theme (see model3_type_effects from
# Step 5), not a plotting artifact -- the dashed vs. solid style below keeps
# such overlapping lines visible rather than hiding one under the other.
fig3, axes3 = plt.subplots(1, len(theme_levels), figsize=(5 * len(theme_levels), 4), sharey=True)
for ax, theme_level in zip(axes3, theme_levels):
    for type_level, color, linestyle in type_styles:
        pred_df_3 = pd.DataFrame({
            "duration": duration_range,
            "type": type_level,
            "theme": theme_level,
        })
        predicted_p_long_3 = model_3.predict(pred_df_3)
        ax.plot(
            duration_range, predicted_p_long_3,
            color=color, linestyle=linestyle, linewidth=2.5, label=type_level,
        )

    # Annotate with the theme-specific Type effect (coef/CI/p) computed in
    # Step 5, so it's clear whether the visible gap (or lack of one) between
    # the two lines in this panel is statistically significant.
    coef, ci_lower, ci_upper, p_value = model3_type_effects[theme_level]
    ax.text(
        0.02, 0.02,
        f"type2 vs type1:\ncoef={coef:.2f}, 95% CI=[{ci_lower:.2f}, {ci_upper:.2f}]\np={p_value:.3f}",
        transform=ax.transAxes, fontsize=8, va="bottom", ha="left",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8, edgecolor="#9ca3af"),
    )

    ax.set_xlabel("Duration (s)")
    ax.set_title(f"theme = {theme_level}")
    ax.set_ylim(0, 1)

axes3[0].set_ylabel("P(Long)")
axes3[0].legend(title="Narrative Type")
fig3.suptitle(f"Model 3: P(Long) by Type x Theme interaction (sub-{SUBJECT_ID})")
fig3.tight_layout()

fig3_path = out_dir / f"sub-{SUBJECT_ID}_type_regression_model3.png"
fig3.savefig(fig3_path, dpi=150)
print(f"Saved figure to {fig3_path}")

plt.show()


## Step 7. Model Comparison

# AIC balances model fit against model complexity; lower AIC = better trade-off.
print(f"\nModel 1 AIC (duration only): {model_1.aic:.2f}")
print(f"Model 2 AIC (duration + type + theme): {model_2.aic:.2f}")
print(f"Model 3 AIC (duration + type * theme): {model_3.aic:.2f}")

if model_2.aic < model_1.aic:
    print("Model 2 has a lower AIC -> adding Narrative Type and Theme improves the model.")
else:
    print("Model 1 has a lower (or equal) AIC -> Narrative Type and Theme do not improve the model.")

if model_3.aic < model_2.aic:
    print("Model 3 has a lower AIC -> the Type x Theme interaction improves the model.")
else:
    print("Model 2 has a lower (or equal) AIC -> the Type x Theme interaction does not improve the model.")

# A likelihood-ratio test gives a formal significance test for the interaction
# terms (Model 3 vs. Model 2), since Model 2 is nested inside Model 3.
lr_stat = 2 * (model_3.llf - model_2.llf)
lr_df = model_3.df_model - model_2.df_model
lr_p_value = 1 - stats.chi2.cdf(lr_stat, lr_df)
print(f"\nLikelihood-ratio test (Model 3 vs Model 2): "
      f"chi2({lr_df:.0f}) = {lr_stat:.2f}, p = {lr_p_value:.4f}")
if lr_p_value < 0.05:
    print("p < 0.05 -> the Type x Theme interaction is statistically significant.")
else:
    print("p >= 0.05 -> the Type x Theme interaction is not statistically significant.")
