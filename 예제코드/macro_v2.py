"""6장 예제: 재시도·기록·반복을 갖춘 매크로 실행기.

사용법:
    python3 macro_v2.py           # STEPS를 REPEAT번 실행
"""
import datetime
import time

from adb_helper import (AdbError, check_device, key, launch, open_url,
                        screenshot, stop, swipe, tap, tap_text, text, wait_for)

PACKAGE = "com.google.android.youtube"
VIDEO_URL = "https://www.youtube.com/watch?v=jNQXAC9IVRw"   # 유튜브 최초의 영상 "Me at the zoo"

STEPS = [
    ("stop", PACKAGE),
    ("open", VIDEO_URL, PACKAGE),
    ("wait_for", "zoo"),               # 영상 제목이 보일 때까지 최대 15초
    ("wait", 2),
    ("shot", "youtube"),
    ("key", "KEYCODE_BACK"),
]
REPEAT = 1
RETRIES = 2          # 단계가 실패하면 다시 시도할 횟수
LOG_FILE = "macro.log"


def log(msg):
    line = f"[{datetime.datetime.now():%H:%M:%S}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_step(step):
    kind, *a = step
    if kind == "tap":
        tap(*a)
    elif kind == "swipe":
        swipe(*a)
    elif kind == "key":
        key(a[0])
    elif kind == "text":
        text(a[0])
    elif kind == "wait":
        time.sleep(a[0])
    elif kind == "launch":
        launch(a[0])
    elif kind == "stop":
        stop(a[0])
    elif kind == "open":
        open_url(*a)
    elif kind == "tap_text":
        tap_text(*a)
    elif kind == "wait_for":
        if wait_for(text=a[0], timeout=a[1] if len(a) > 1 else 15) is None:
            raise AdbError(f"'{a[0]}'가 나타나지 않았습니다")
    elif kind == "shot":
        screenshot(f"{a[0]}_{datetime.datetime.now():%m%d_%H%M%S}.png")
    else:
        raise ValueError(f"알 수 없는 동작: {kind}")


def run_with_retry(step):
    for attempt in range(1, RETRIES + 2):
        try:
            run_step(step)
            return True
        except AdbError as e:
            log(f"   ⚠️ 실패 ({attempt}회차): {e}")
            time.sleep(1)
    return False


def main():
    check_device()
    for r in range(1, REPEAT + 1):
        log(f"=== {r}/{REPEAT}회 시작 ===")
        for i, step in enumerate(STEPS, 1):
            log(f"{i}. {step}")
            if not run_with_retry(step):
                path = screenshot(f"error_{datetime.datetime.now():%H%M%S}.png")
                log(f"❌ {i}단계에서 중단. 화면을 {path}에 저장했습니다")
                return
        log(f"✅ {r}회 완료")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("사용자가 중지했습니다")
