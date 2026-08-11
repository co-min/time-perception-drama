import platform
from pathlib import Path

# ─── Paths ───────────────────────────────────────────────────────────────────
ROOT_DIR     = Path(__file__).resolve().parents[2]
STIMULUS_DIR = ROOT_DIR / "stimuli"
DATA_DIR     = ROOT_DIR / "data"

# ─── Window ───────────────────────────────────────────────────────────────────
WINDOW_SIZE      = (1470, 956)   # TODO: adjust to your display
WINDOW_UNITS     = "pix"
WINDOW_FULLSCR   = False          # Set True for actual experiment
BACKGROUND_COLOR = "black"      
MONITOR_NAME     = "testMonitor"  # TODO: calibrate your monitor
SCREEN_NUMBER = 1

# ─── Timing ──────────────────────────────────────────────────────────────────
MAX_RESPONSE_TIME = 30.0          # seconds; None = unlimited
ITI_DURATION      = 1.5          # inter-trial interval (seconds)
FRAME_RATE        = 60           # Hz – used for frame log sanity checks
VIDEO_SIZE        = (1280, 720)

# ─── Text ────────────────────────────────────────────────────────────────────
FONT = "AppleGothic" if platform.system() == "Darwin" else "Malgun Gothic"
TEXT_COLOR       = "white"

# ─── Response ────────────────────────────────────────────────────────────────────

YES_KEY = "left"
NO_KEY = "right"
COMFIRM_KEY = "space"
QUIT_KEY   = "escape"
PAUSE_KEY  = "p"


RESPONSE_TEXT_SHORT = "영상의 길이가 1분 보다 짧았나요?"
RESPONSE_TEXT_LONG = "영상의 길이가 1분 보다 길었나요?"
RESPONSE_TEXT_HEIGHT = 40

YES_TEXT = "예"
NO_TEXT = "아니오"

BUTTON_SIZE = (350, 180)
YES_POSITION = (-300, 0)
NO_POSITION = (300, 0)
QUESTION_POSITION = (0, 380)



SELECTED_BUTTON_COLOR = "purple"
BUTTON_COLOR = "gray"

