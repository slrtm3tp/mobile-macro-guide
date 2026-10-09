"""ADB 기반 안드로이드 매크로.

사용법:
    python3 macro.py            # STEPS를 REPEAT번 실행
    python3 macro.py screenshot # 현재 화면을 screen.png로 저장 (좌표 확인용)
    python3 macro.py apps       # 설치된 앱 패키지명 목록
"""
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

VIDEO_URL = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # 유튜브 최초의 영상 "Me at the zoo"

# 실행할 동작 목록. 좌표는 screenshot으로 확인하세요.
STEPS = [
    ("open", VIDEO_URL, "com.google.android.youtube"),  # 유튜브 앱에서 영상 바로 열기
    ("wait", 3),
    # ("launch", "com.example.app"),     # 앱 실행 (패키지명)
    # ("tap_text", "이벤트"),             # 화면에서 해당 글자가 있는 요소 찾아 탭
    # ("tap", 540, 1200),                # (x, y) 탭
    # ("swipe", 540, 1600, 540, 600, 300), # (x1, y1, x2, y2, ms) 스와이프
    # ("text", "hello"),                 # 텍스트 입력 (영문/숫자만)
    # ("key", "KEYCODE_BACK"),           # 키 입력: BACK, HOME, ENTER 등
]
REPEAT = 1


def adb(*args):
    return subprocess.run(["adb", *map(str, args)], check=True, capture_output=True).stdout


def run_step(step):
    kind, *a = step
    if kind == "tap":
        adb("shell", "input", "tap", *a)
    elif kind == "swipe":
        adb("shell", "input", "swipe", *a)
    elif kind == "text":
        adb("shell", "input", "text", a[0].replace(" ", "%s"))
    elif kind == "key":
        adb("shell", "input", "keyevent", a[0])
    elif kind == "launch":
        adb("shell", "monkey", "-p", a[0], "-c", "android.intent.category.LAUNCHER", "1")
    elif kind == "open":
        # adb shell은 인자를 다시 셸로 해석하므로 URL의 &가 잘리지 않게 따옴표로 감싼다
        adb("shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", f"'{a[0]}'", *a[1:])
    elif kind == "tap_text":
        x, y = find_text(a[0], a[1] if len(a) > 1 else 10)
        adb("shell", "input", "tap", x, y)
    elif kind == "wait":
        time.sleep(a[0])
    else:
        raise ValueError(f"알 수 없는 동작: {kind}")


def find_text(text, timeout=10):
    """화면 UI 트리에서 text/content-desc에 text가 포함된 요소의 중심 좌표를 찾는다."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
        root = ET.fromstring(adb("exec-out", "cat", "/sdcard/ui.xml"))
        for node in root.iter("node"):
            if text in node.get("text", "") or text in node.get("content-desc", ""):
                x1, y1, x2, y2 = map(int, re.findall(r"\d+", node.get("bounds")))
                return (x1 + x2) // 2, (y1 + y2) // 2
        time.sleep(1)
    raise RuntimeError(f"화면에서 '{text}'를 찾지 못했습니다")


def check_device():
    lines = adb("devices").decode().strip().splitlines()[1:]
    devices = [l for l in lines if l.endswith("\tdevice")]
    if not devices:
        sys.exit("연결된 기기가 없습니다. USB 디버깅과 연결 허용을 확인하세요.\n" + "\n".join(lines))


def main():
    check_device()
    if len(sys.argv) > 1 and sys.argv[1] == "screenshot":
        with open("screen.png", "wb") as f:
            f.write(adb("exec-out", "screencap", "-p"))
        print("screen.png 저장 완료")
        return
    if len(sys.argv) > 1 and sys.argv[1] == "apps":
        print(adb("shell", "pm", "list", "packages", "-3").decode())
        return
    for i in range(REPEAT):
        print(f"[{i + 1}/{REPEAT}]")
        for step in STEPS:
            run_step(step)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n중지됨")
