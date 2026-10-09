"""9장 예제: 정해진 시각에 정확히 매크로를 실행한다.

사용법:
    python3 scheduled_run.py 10:00:00          # 오늘 10시 정각에 실행
    python3 scheduled_run.py 10:00:00 --now    # 시간 무시하고 바로 테스트

동작:
    1. 시작 PREPARE_SEC초 전에 페이지를 미리 열어 둔다
    2. 정각까지 기다렸다가 FIRE 동작을 실행한다
"""
import datetime
import sys
import time

from adb_helper import check_device, key, open_url, screenshot, stop, tap_text

PACKAGE = "ctrip.english"
URL = "https://kr.trip.com/sale/w/37676/gojapan.html?locale=ko-KR&transparentBar=1&wkp=1"
PREPARE_SEC = 60          # 정각 몇 초 전에 준비를 시작할지


def prepare():
    key("KEYCODE_WAKEUP")
    stop(PACKAGE)
    open_url(URL, PACKAGE)
    time.sleep(5)


def fire():
    # 정각에 할 일. 예: 화면을 새로고침하고 "받기" 버튼 누르기
    try:
        tap_text("받기", timeout=5)
    finally:
        screenshot(f"fire_{datetime.datetime.now():%H%M%S}.png")


def wait_until(target):
    """target(datetime)까지 기다린다. 마지막 1초는 촘촘하게 확인한다."""
    while True:
        left = (target - datetime.datetime.now()).total_seconds()
        if left <= 0:
            return
        time.sleep(min(left - 0.5, 30) if left > 1 else 0.01)


def main():
    check_device()
    hh, mm, ss = map(int, sys.argv[1].split(":"))
    target = datetime.datetime.now().replace(hour=hh, minute=mm, second=ss, microsecond=0)
    if "--now" in sys.argv:
        target = datetime.datetime.now() + datetime.timedelta(seconds=PREPARE_SEC + 5)
    if target < datetime.datetime.now():
        raise SystemExit("이미 지난 시각입니다")

    print(f"목표 시각: {target:%H:%M:%S}")
    wait_until(target - datetime.timedelta(seconds=PREPARE_SEC))
    print(f"[{datetime.datetime.now():%H:%M:%S}] 준비 시작")
    prepare()
    wait_until(target)
    print(f"[{datetime.datetime.now():%H:%M:%S.%f}] 실행!")
    fire()
    print("완료")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
    else:
        main()
