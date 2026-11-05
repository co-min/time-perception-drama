# python analysis/psychometric/plot_wichmann_single.py --sub 1020

# 0. Import
# 1. load data
# 2. P(long) 계산
# 3. MLE 목적 함수
# 4. fit_model: maximum parameter 찾기
# 5. calculate pse slope
# 6. plot psychometric - figure 생성
# 7. main


## Step 1. Import Libraries
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.special import expit, logit
from scipy.stats import chi2

CURRENT_FILE = Path(__file__)
PROJECT_ROOT = CURRENT_FILE.parent.parent.parent
DATA_ROOT = PROJECT_ROOT / "data"
OUTFILE_ROOT = CURRENT_FILE.parent.parent / "outfile_data"

ALPHA = 0.05  # likelihood-ratio test level for "data support beta1 > 0"
JITTER_SEED = 0
DEFAULT_JITTER = 0.02  # max vertical offset of raw points, visualization only


## Step 2. Load Data
def extract_duration(video_name):
    duration_text = video_name.split("s")[0]
    return float(duration_text)


def load_data(subject_id):
    data_path = DATA_ROOT / f"sub-{subject_id}" / "ses-1" / "trials.csv"
    df = pd.read_csv(data_path)

    # timeout 제거
    df = df[df["response"].isin(["short", "long"])].copy()

    df["duration"] = df["video"].apply(extract_duration)
    df["is_long"] = (df["response"] == "long").astype(int)
    return df


## Psychometric function (Equation 1)
def psychometric_function(duration, beta0, beta1):
    """
    P(Long | duration)

    beta0: intercept
    beta1: duration coefficient
    """

    return expit(beta0 + beta1 * duration)


## Log-Likelihood (Equation 2)
def negative_log_likelihood(params, durations, responses):
    beta0, beta1 = params
    linear_predictor = beta0 + beta1 * durations

    # -log(p) = log(1 + e^-x), -log(1 - p) = log(1 + e^x); logaddexp avoids log(0)
    return np.sum(
        responses * np.logaddexp(0, -linear_predictor)
        + (1 - responses) * np.logaddexp(0, linear_predictor)
    )


def negative_log_likelihood_gradient(params, durations, responses):
    residuals = responses - psychometric_function(durations, *params)
    return np.array([-np.sum(residuals), -np.sum(residuals * durations)])


## Maximum Likelihood Estimation
def find_identifiability_problem(durations, responses):
    """Return why the MLE does not exist for these data, or None if it does."""
    if len(np.unique(responses)) < 2:
        return "Only one response category; PSE and slope are not identifiable"
    if len(np.unique(durations)) < 2:
        return "Only one duration; PSE and slope are not identifiable"

    # With perfectly separated responses, the likelihood keeps rising as |beta1| -> infinity
    short_durations = durations[responses == 0]
    long_durations = durations[responses == 1]
    if (
        short_durations.max() <= long_durations.min()
        or long_durations.max() <= short_durations.min()
    ):
        return "Responses are perfectly separated by duration; MLE does not exist"
    return None


def fit_model(durations, responses):
    """
    Fit Equation 1 to single trials by MLE.

    status: "ok" | "weak_slope" (beta1 > 0, but LR test not significant)
            | "not_increasing" (beta1 <= 0) | "failed" (no estimates)
    """
    durations = np.asarray(durations, dtype=float)
    responses = np.asarray(responses, dtype=float)

    fit = {
        "n_trials": len(durations),
        "beta0": np.nan,
        "beta1": np.nan,
        "log_likelihood": np.nan,
        "lr_p_value": np.nan,
        "status": "failed",
        "message": "",
    }

    problem = find_identifiability_problem(durations, responses)
    if problem:
        fit["message"] = problem
        return fit

    # Centering keeps beta0 and beta1 from being strongly correlated during the search
    mean_duration = durations.mean()
    centered_durations = durations - mean_duration
    result = minimize(
        negative_log_likelihood,
        x0=[0.0, 0.0],
        args=(centered_durations, responses),
        jac=negative_log_likelihood_gradient,
        method="BFGS",
    )
    if not result.success:
        fit["message"] = f"Optimization failed: {result.message}"
        return fit

    centered_beta0, beta1 = result.x
    log_likelihood = -result.fun

    # Likelihood-ratio test against a flat P(Long), which ignores duration
    null_params = [logit(responses.mean()), 0.0]
    null_log_likelihood = -negative_log_likelihood(null_params, durations, responses)
    lr_p_value = chi2.sf(2 * (log_likelihood - null_log_likelihood), df=1)

    if beta1 <= 0:
        status = "not_increasing"
        message = "beta1 <= 0: increasing function not supported; PSE and slope not reported"
    elif lr_p_value >= ALPHA:
        status = "weak_slope"
        message = f"Weak duration effect (LR p = {lr_p_value:.3f}); PSE and slope are uncertain"
    else:
        status = "ok"
        message = ""

    fit.update(
        beta0=centered_beta0 - beta1 * mean_duration,  # back to uncentered duration
        beta1=beta1,
        log_likelihood=log_likelihood,
        lr_p_value=lr_p_value,
        status=status,
        message=message,
    )
    return fit


## PSE and Slope
def calculate_metrics(beta0, beta1, durations):
    # PSE and slope assume an increasing function (beta1 > 0)
    if not beta1 > 0:
        return {"pse": np.nan, "slope": np.nan, "pse_in_range": False}

    pse = -beta0 / beta1
    slope = beta1 / 4  # derivative of the logistic at P(Long) = 0.5
    pse_in_range = bool(np.min(durations) <= pse <= np.max(durations))

    return {"pse": pse, "slope": slope, "pse_in_range": pse_in_range}


## Plot
def plot_psychometric(
    durations, responses, fit, metrics, subject_id, out_path, jitter=DEFAULT_JITTER
):
    durations = np.asarray(durations, dtype=float)
    responses = np.asarray(responses, dtype=float)

    fig, ax = plt.subplots(figsize=(6.5, 5.5))

    # Jitter only moves the drawn points; the fit never sees it
    rng = np.random.default_rng(JITTER_SEED)
    drawn_responses = responses + rng.uniform(-jitter, jitter, size=len(responses))
    raw_label = "Raw responses (0 = Short, 1 = Long)"
    if jitter > 0:
        raw_label += ", vertical jitter for display"
    ax.scatter(
        durations, drawn_responses,
        s=30, alpha=0.5, color="#6b7280", linewidths=0, label=raw_label,
    )

    if fit["status"] != "failed":
        duration_range = np.linspace(durations.min(), durations.max(), 300)
        ax.plot(
            duration_range,
            psychometric_function(duration_range, fit["beta0"], fit["beta1"]),
            color="#1d4ed8", linewidth=2, label="Fitted logistic P(Long)",
        )

    pse, slope = metrics["pse"], metrics["slope"]
    if metrics["pse_in_range"]:
        ax.axvline(
            pse, color="#111827", linestyle="--", linewidth=1.2,
            label=f"PSE = {pse:.2f} s",
        )

        # Tangent spans at most P(Long) +/- 0.2 and 10% of the range on each side, inside the data
        half_width = min(0.2 / slope, 0.1 * (durations.max() - durations.min()))
        tangent_x = np.clip([pse - half_width, pse + half_width], durations.min(), durations.max())
        ax.plot(
            tangent_x, 0.5 + slope * (tangent_x - pse),
            color="#ef4444", linewidth=2.5, label=f"Slope at PSE = {slope:.3f} s$^{{-1}}$",
        )
    elif np.isfinite(pse):
        # An extrapolated PSE has no place on the axis, so it is reported in the legend only
        ax.plot(
            [], [], " ",
            label=(
                f"PSE = {pse:.2f} s (extrapolated, outside stimulus range; not drawn)\n"
                f"Slope at PSE = {slope:.3f} s$^{{-1}}$ (not drawn)"
            ),
        )

    if fit["message"]:
        ax.plot([], [], " ", label=fit["message"])

    ax.set_xlabel("Video Duration (s)")
    ax.set_ylabel("Response / P(Long)")
    ax.set_ylim(-0.08, 1.08)
    ax.set_yticks([0, 0.5, 1])
    ax.set_title(f"Psychometric function (sub-{subject_id})")
    ax.grid(True, axis="y", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)

    # Legend sits under the axes so it never covers the raw responses at 0 and 1
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), frameon=False, fontsize=9)

    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


## Main
def main():
    parser = argparse.ArgumentParser(
        description="Fit a logistic psychometric function to single trials by MLE"
    )
    parser.add_argument(
        "--sub",
        required=True,  # 반드시 입력
        help="Subject ID",
    )
    parser.add_argument(
        "--jitter",
        type=float,
        default=DEFAULT_JITTER,
        help="Max vertical jitter of raw points, display only (0 = off)",
    )
    args = parser.parse_args()
    subject_id = args.sub

    df = load_data(subject_id)
    durations = df["duration"].to_numpy()
    responses = df["is_long"].to_numpy()

    fit = fit_model(durations, responses)
    metrics = calculate_metrics(fit["beta0"], fit["beta1"], durations)

    out_dir = OUTFILE_ROOT / f"sub-{subject_id}" / "psychometric"
    out_dir.mkdir(parents=True, exist_ok=True)

    figure_path = out_dir / f"sub-{subject_id}_wichmann_single.png"
    plot_psychometric(
        durations, responses, fit, metrics, subject_id, figure_path, jitter=args.jitter
    )

    estimates = {"subject": subject_id, **fit, **metrics}
    estimates_path = out_dir / f"sub-{subject_id}_wichmann_single_estimates.csv"
    pd.DataFrame([estimates]).to_csv(estimates_path, index=False)

    print(f"sub-{subject_id}: valid trials = {fit['n_trials']}, status = {fit['status']}")
    print(f"  beta0 = {fit['beta0']:.4f}, beta1 = {fit['beta1']:.4f}, LR p = {fit['lr_p_value']:.4f}")
    print(f"  PSE = {metrics['pse']:.3f} s, Slope = {metrics['slope']:.4f} s^-1")
    if np.isfinite(metrics["pse"]) and not metrics["pse_in_range"]:
        print("  WARNING: PSE is outside the stimulus range (extrapolated)")
    if fit["message"]:
        print(f"  WARNING: {fit['message']}")
    print(f"Saved figure to {figure_path}")
    print(f"Saved estimates to {estimates_path}")


if __name__ == "__main__":
    main()
