"""12장 종합 프로젝트: 트립닷컴 고재팬 페이지 자동 열기 + 확인 + 기록.

사용법:
    python3 project_gojapan.py                 # 지금 바로 한 번 실행
    python3 project_gojapan.py --at 09:59:30   # 오늘 해당 시각에 실행
    python3 project_gojapan.py --tap 받기       # 페이지가 열리면 '받기' 글자를 찾아 탭

결과:
    runs/날짜_시각.png   실행 결과 캡처
    runs/history.csv     실행 기록 (시각, 결과, 걸린 시간, 메모)
    project.log          자세한 로그
"""
import argparse
import csv
import datetime
import os
import time

from adb_helper import (AdbError, check_device, current_app, dump_ui, key,
                        open_url, screenshot, shell, stop, swipe, tap_text)

PACKAGE = "ctrip.english"
URL = "https://kr.trip.com/sale/w/37676/gojapan.html?locale=ko-KR&transparentBar=1&wkp=1"
H5_ACTIVITY = "TripH5Container"        # 트립닷컴이 웹페이지를 띄우는 화면
CLOSE_FIRST = ["com.google.android.youtube"]   # 화면을 덮을 수 있는 앱 (PIP 등)
OUT_DIR = "runs"
LOG_FILE = "project.log"


def log(msg):
    line = f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def record(result, seconds, memo):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, "history.csv")
    new = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["시각", "결과", "걸린 시간(초)", "메모"])
        w.writerow([f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}", result, f"{seconds:.1f}", memo])


def wait_until(hhmmss):
    hh, mm, ss = map(int, hhmmss.split(":"))
    target = datetime.datetime.now().replace(hour=hh, minute=mm, second=ss, microsecond=0)
    if target < datetime.datetime.now():
        raise SystemExit(f"{hhmmss}은 이미 지난 시각입니다")
    log(f"{target:%H:%M:%S}까지 기다립니다")
    while (left := (target - datetime.datetime.now()).total_seconds()) > 0:
        time.sleep(min(left, 30) if left > 1 else 0.01)


def wake_and_unlock_check():
    key("KEYCODE_WAKEUP")
    time.sleep(0.5)
    locked = "mDreamingLockscreen=true" in shell("dumpsys window | grep mDreamingLockscreen")
    if locked:
        raise AdbError("폰이 잠겨 있습니다. 잠금을 풀어 두거나 충전 중 화면 켜짐 유지를 켜세요")


def open_page():
    for pkg in CLOSE_FIRST:
        stop(pkg)
    stop(PACKAGE)
    time.sleep(1)
    open_url(URL, PACKAGE)
    for _ in range(20):                 # 최대 10초 동안 화면 확인
        pkg, activity = current_app()
        if pkg == PACKAGE and activity and H5_ACTIVITY in activity:
            return True
        time.sleep(0.5)
    return False


def page_words(limit=8):
    try:
        root = dump_ui()
    except Exception:
        return []
    return [n.get("text") for n in root.iter("node") if n.get("text")][:limit]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--at", help="실행 시각 HH:MM:SS")
    ap.add_argument("--tap", help="페이지가 열린 뒤 찾아서 누를 글자")
    args = ap.parse_args()

    check_device()
    if args.at:
        wait_until(args.at)

    start = time.time()
    memo = ""
    try:
        log("1. 화면 깨우기")
        wake_and_unlock_check()
        log("2. 고재팬 페이지 열기")
        if not open_page():
            raise AdbError(f"페이지 화면이 뜨지 않았습니다: {current_app()}")
        time.sleep(3)                   # 웹페이지 내용이 그려질 시간
        words = page_words()
        log(f"3. 화면 글자: {words}")
        if args.tap:
            log(f"4. '{args.tap}' 찾아서 탭")
            tap_text(args.tap, timeout=10)
            time.sleep(2)
            memo = f"'{args.tap}' 탭"
        else:
            swipe(720, 2400, 720, 1400, 500)   # 쿠폰 영역이 보이도록 살짝 스크롤
            time.sleep(1)
        result = "성공"
    except AdbError as e:
        result, memo = "실패", str(e)
        log(f"❌ {e}")

    os.makedirs(OUT_DIR, exist_ok=True)
    shot = screenshot(os.path.join(OUT_DIR, f"{datetime.datetime.now():%Y%m%d_%H%M%S}.png"))
    seconds = time.time() - start
    record(result, seconds, memo)
    log(f"{'✅' if result == '성공' else '❌'} {result} ({seconds:.1f}초) 캡처: {shot}")


if __name__ == "__main__":
    main()
