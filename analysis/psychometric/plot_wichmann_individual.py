# python analysis/psychometric/plot_wichmann_individual.py --sub

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
import patsy
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
from scipy.special import expit

## Step 2. Load and Inspect Data

parser = argparse.ArgumentParser(
    description=""
)
parser.add_argument(
    "--sub",
    required=True,  # 반드시 입력
    help="Subject ID",
)

# terminal에서 입력 읽고 args 변수에 담기
args = parser.parse_args()
SUBJECT_ID = args.sub

CURRENT_FILE = Path(__file__)
PROJECT_ROOT = CURRENT_FILE.parent.parent.parent
DATA_PATH = PROJECT_ROOT / "data" / f"sub-{SUBJECT_ID}" / "ses-1" / "trials.csv"
OUTFILE_ROOT = CURRENT_FILE.parent.parent / "outfile_data"

df = pd.read_csv(DATA_PATH)

## Psychometric function (Equation 1)
def psychometric_function(duration, beta0, beta1):
    """
    P(Long | duration)

    beta0: intercept
    beta1: duration coefficient
    """

    return expit(beta0 + beta1 * duration)

# Log-Likelihood (Equation 2)


# Maximum Likelihood Estimation


# PSE and Slope
def calculate_pse_slope(beta0, beta1):

    pse = -beta0 / beta1
    slope = beta1 / 4

    return pse, slope


## Main
def main():
    None

if __name__ == "__main__":
    main()