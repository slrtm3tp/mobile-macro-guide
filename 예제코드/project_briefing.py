"""12장 종합 프로젝트: 아침 브리핑 자동화.

날씨·뉴스 같은 페이지를 차례로 열어 캡처하고, 결과를 날짜별 폴더와 CSV에 기록한다.

사용법:
    python3 project_briefing.py                 # 지금 바로 한 번 실행
    python3 project_briefing.py --at 07:30:00   # 오늘 해당 시각에 실행

결과:
    runs/2026-10-09/01_날씨.png ...   페이지별 캡처
    runs/history.csv                 실행 기록 (시각, 페이지, 결과, 걸린 시간, 메모)
    project.log                      자세한 로그
"""
import argparse
import csv
import datetime
import os
import time

from adb_helper import (AdbError, check_device, current_app, key, open_url,
                        screenshot, shell, stop)

BROWSER = "com.android.chrome"
PAGES = [                                     # (이름, 주소) - 원하는 페이지로 바꾸세요
    ("날씨", "https://www.google.com/search?q=seoul+weather"),
    ("뉴스", "https://news.google.com/?hl=ko&gl=KR&ceid=KR:ko"),
    ("환율", "https://www.google.com/search?q=usd+krw"),
]
CLOSE_FIRST = ["com.google.android.youtube"]  # 화면을 덮을 수 있는 앱 (PIP 등)
OUT_DIR = "runs"
LOG_FILE = "project.log"


def log(msg):
    line = f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def record(page, result, seconds, memo):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, "history.csv")
    new = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["시각", "페이지", "결과", "걸린 시간(초)", "메모"])
        w.writerow([f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}", page, result, f"{seconds:.1f}", memo])


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


def open_page(url):
    stop(BROWSER)
    time.sleep(1)
    open_url(url, BROWSER)
    for _ in range(20):                     # 최대 10초 동안 화면 확인
        pkg, _ = current_app()
        if pkg == BROWSER:
            return True
        time.sleep(0.5)
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--at", help="실행 시각 HH:MM:SS")
    args = ap.parse_args()

    check_device()
    if args.at:
        wait_until(args.at)

    day_dir = os.path.join(OUT_DIR, datetime.date.today().isoformat())
    os.makedirs(day_dir, exist_ok=True)

    try:
        log("1. 화면 깨우기")
        wake_and_unlock_check()
        for pkg in CLOSE_FIRST:
            stop(pkg)
    except AdbError as e:
        log(f"❌ {e}")
        screenshot(os.path.join(day_dir, "00_error.png"))
        record("-", "실패", 0, str(e))
        return

    ok = 0
    for i, (name, url) in enumerate(PAGES, 1):
        start = time.time()
        memo = ""
        try:
            log(f"{i + 1}. {name} 페이지 열기")
            if not open_page(url):
                raise AdbError(f"브라우저 화면이 뜨지 않았습니다: {current_app()}")
            time.sleep(4)                       # 페이지 내용이 그려질 시간
            result = "성공"
            ok += 1
        except AdbError as e:
            result, memo = "실패", str(e)
            log(f"   ❌ {e}")
        shot = screenshot(os.path.join(day_dir, f"{i:02d}_{name}.png"))
        record(name, result, time.time() - start, memo)
        log(f"   {'✅' if result == '성공' else '❌'} {name}: {shot}")

    stop(BROWSER)
    key("KEYCODE_HOME")
    log(f"완료: {ok}/{len(PAGES)} 성공, 캡처 폴더 {day_dir}")


if __name__ == "__main__":
    main()
