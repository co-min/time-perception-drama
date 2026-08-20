import platform
from pathlib import Path

# ─── Paths ───────────────────────────────────────────────────────────────────
ROOT_DIR     = Path(__file__).resolve().parents[2]
STIMULUS_DIR = ROOT_DIR / "stimuli" / "video"
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
ITI_DURATION      = 1.0          # inter-trial interval (seconds)
FRAME_RATE        = 60           # Hz – used for frame log sanity checks
VIDEO_SIZE        = (1280, 720)
FIXATION_DURATION = 10          # seconds; fixation cross duration between video and response

# ─── Trial Number Screen ──────────────────────────────────────────────────────
TRIAL_NUMBER_DURATION      = 0.75         # seconds; how long the "Trial N" screen is shown
TRIAL_NUMBER_TEXT_HEIGHT   = 40           # px; matches RESPONSE_TEXT_HEIGHT convention
TRIAL_NUMBER_TEXT_TEMPLATE = "Trial {n}"  # no total shown, by design

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

# ─── Instruction / Break ──────────────────────────────────────────────────────

START_KEY = "s"

INSTRUCTION_WRAP_WIDTH = 1200  # px; keeps long lines from wrapping against the window edge

INSTRUCTION_TEXT = (
    "이제부터 드라마 영상을 시청하게 됩니다.\n\n"
    "각 영상이 끝난 후,"
    "영상이 얼마나 길게 또는 짧게 느껴졌는지 생각해보세요.\n\n"
    "← 와 → 방향키를 눌러 응답을 선택하고,\n"
    "스페이스바를 눌러 선택을 확정해 주세요.\n\n"
    "준비가 되었다면 s를 눌러 시작해 주세요."
)

BREAK_TEXT = (
    "잠시 휴식을 취할 수 있습니다.\n\n"
    "준비가 되었다면 s를 눌러 계속 진행해 주세요"
)

YES_TEXT = "예"
NO_TEXT = "아니오"

BUTTON_SIZE = (350, 180)
YES_POSITION = (-300, 0)
NO_POSITION = (300, 0)
QUESTION_POSITION = (0, 380)



SELECTED_BUTTON_COLOR = "purple"
BUTTON_COLOR = "gray"

# ─── Neon (Pupil Labs Companion) ───────────────────────────────────────────────
USE_NEON = False   # True: Neon Companion 연결, False: no-op

# ─── AprilTag (Pupil Labs Neon) ────────────────────────────────────────────────
# Provisional — must be tested on the actual monitor and adjusted if necessary.
APRILTAG_SIZE = 0.09

APRILTAG_POSITIONS = (
    (-0.70, -0.44),
    (0.70, -0.44),
    (-0.70, 0.44),
    (0.70, 0.44),
)

