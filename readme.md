# Drama Video Time Perception Experiment

PsychoPy 기반 심리 실험 코드입니다. 참가자는 짧은 드라마 영상 클립을 시청한 후,
영상 길이가 1분보다 길게/짧게 느껴졌는지 응답합니다. LabJack T4를 통한 EEG(Natus
Quantum) TTL 트리거 전송과 Pupil Labs Neon 아이트래커 연동을 지원합니다.

## 요구 사항

- Python 3.11 (Windows `py -3.11` 런처 기준)
- [PsychoPy](https://www.psychopy.org/)
- (선택) LabJack `ljm` 라이브러리 — EEG 트리거 사용 시
- (선택) `pupil-labs-realtime-api`, `requests`, `pandas` — Neon 아이트래커 사용 시

## 설치

```bash
python set_up.py
```

`set_up.py`가 `.venv`를 Python 3.11로 생성하고 `requirements.txt`를 설치합니다.
이후 가상환경을 활성화합니다.

```bash
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS/Linux
```

## 실행

```bash
python main.py
```

실행하면 Subject ID / Session 번호를 입력하는 다이얼로그가 뜨고, 이후 지시문 →
(ITI → 시행 번호 표시 → 영상 재생 → 응시 화면 → 응답) 순서로 시행이 반복되며,
10시행마다 휴식 화면이 표시됩니다. 같은 subject/session 조합으로 이미 결과 파일이
존재하면 덮어쓰지 않고 에러를 발생시킵니다.

## 프로젝트 구조

```
main.py                 실험 진입점 (시행 루프, 트리거/Neon/저장 초기화)
set_up.py                가상환경 생성 및 의존성 설치 스크립트
requirements.txt

function/
  config/
    settings.py          모든 실험 설정값 (창 크기, 타이밍, 텍스트, 키, Neon/AprilTag 등)
    window_factory.py     PsychoPy Window 생성
  phases/
    data_loader.py        stimuli/video/*.mp4 목록 로드
    phase.py               한 시행(trial)의 전체 흐름 조합
    run_instruction.py     시작 지시문 화면
    run_break.py           휴식 화면
    run_trial_number.py    "Trial N" 표시
    run_video.py            영상 재생
    run_fixation.py         응시 십자가
    run_response.py         예/아니오 응답 수집
  io/
    path_builder.py         data/sub-{id}/ses-{id}/ 경로 생성 규칙
    session_saver.py        session_info.json 저장
    trial_saver.py           trials.csv 행 단위 저장
    event_saver.py / event_logger.py   event_log.csv 저장
    frame_saver.py / frame_logger.py   프레임 단위 타이밍 로그
    timing_diagnostics.py
  tests/
    test_all_videos.py

utils/
  screen_utils.py          피험자 정보 다이얼로그, 화면 헬퍼
  labjack_trigger.py        LabJack T4 TTL 트리거 (EIO 데이터 8핀 + CIO0 latch)
  neon_client.py             Pupil Labs Neon REST API 클라이언트 (NeonEventClient / NullNeonClient)
  apriltag_utils.py          Neon 시야 정합용 AprilTag 4개 코너 표시
  event_utils.py, inter_trial.py

stimuli/video/              실험에 사용하는 드라마 영상 클립 (.mp4)
data/                        시행 결과 저장 위치 (git에 커밋되지 않음)
```

## 설정 (`function/config/settings.py`)

주요 설정값은 아래와 같습니다. 실제 실험 전 반드시 확인/조정하세요.

| 항목 | 설명 |
| --- | --- |
| `WINDOW_SIZE`, `WINDOW_FULLSCR`, `SCREEN_NUMBER` | 창 크기 및 표시할 모니터 |
| `MONITOR_NAME` | PsychoPy Monitor Center에서 캘리브레이션된 모니터 이름 |
| `FIXATION_DURATION`, `ITI_DURATION`, `MAX_RESPONSE_TIME` | 시행 내 타이밍(초) |
| `YES_KEY` / `NO_KEY` / `COMFIRM_KEY` | 응답 키 (기본: ←/→, space) |
| `USE_NEON` | `True`로 설정 시 Neon Companion 기기와 연결, `False`면 no-op |
| `APRILTAG_SIZE`, `APRILTAG_POSITIONS` | Neon 시야 정합용 AprilTag 크기/위치 (실제 모니터에서 검증 필요) |
| `NO_AUDIO_DIAGNOSTIC`, `DIAGNOSTIC_FIXED_SEED` | 오디오 유무 타이밍 비교용 임시 진단 플래그 — 비교 완료 후 제거 예정 |

## 출력 데이터

`data/sub-{subject_id}/ses-{session_id}/` 아래에 다음 파일이 생성됩니다.

- `session_info.json` — 세션 메타데이터 (시작 시각, 시행 수, 타이밍 설정 등)
- `trials.csv` — 시행별 결과 (`trial`, `video`, `question_type`, `response`, `rt`)
- `event_log.csv` — 프레임 단위 이벤트/타이밍 로그
- `neon_event_log.csv` — Neon Companion으로 전송한 이벤트 로그 (`USE_NEON=True`일 때만 유효한 데이터 포함)

같은 subject/session에 이미 위 결과 파일이 하나라도 존재하면 실행이 중단됩니다.
새 Session ID를 사용하세요.

## 하드웨어 연동

- **LabJack T4 (EEG 트리거)**: `utils/labjack_trigger.py`. EIO0~7(8비트 코드) +
  CIO0(latch)로 Natus Quantum에 rising-edge 트리거를 전송합니다. `ljm`이 설치되어
  있지 않거나 장치 연결에 실패하면 자동으로 비활성화되고 실험은 계속 진행됩니다.
- **Pupil Labs Neon (아이트래커)**: `utils/neon_client.py`. `USE_NEON=True`일 때
  Neon Companion 앱과 같은 Wi-Fi에서 기기를 탐색하고, 이벤트를 백그라운드 스레드로
  전송합니다. Companion 앱에서 녹화가 시작되어 있어야 합니다.
