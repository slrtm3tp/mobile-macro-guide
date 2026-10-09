"""5장에서 만드는 ADB 도우미 모듈.

다른 예제에서 `from adb_helper import *`로 불러 씁니다.
"""
import re
import subprocess
import time
import xml.etree.ElementTree as ET

SERIAL = None  # 기기가 여러 대면 "R5CT1234ABC"처럼 시리얼을 넣으세요.


class AdbError(Exception):
    """adb 명령이 실패했을 때 발생하는 예외."""


def adb(*args, timeout=30):
    """adb 명령을 실행하고 출력(bytes)을 돌려준다."""
    cmd = ["adb"]
    if SERIAL:
        cmd += ["-s", SERIAL]
    cmd += [str(a) for a in args]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AdbError(f"시간 초과: {' '.join(cmd)}")
    if result.returncode != 0:
        raise AdbError(result.stderr.decode(errors="ignore").strip() or "알 수 없는 오류")
    return result.stdout


def shell(command, timeout=30):
    """폰 안에서 셸 명령을 실행하고 출력(str)을 돌려준다."""
    return adb("shell", command, timeout=timeout).decode(errors="ignore").strip()


# ---------- 연결 ----------

def devices():
    """연결된 기기 목록: [(시리얼, 상태), ...]"""
    out = subprocess.run(["adb", "devices"], capture_output=True, text=True).stdout
    rows = [line.split("\t") for line in out.strip().splitlines()[1:] if "\t" in line]
    return [(serial, state) for serial, state in rows]


def check_device():
    """사용 가능한 기기가 없으면 이유를 알려 주고 종료한다."""
    found = devices()
    if not found:
        raise SystemExit("연결된 기기가 없습니다. 케이블과 USB 디버깅을 확인하세요.")
    for serial, state in found:
        if state == "unauthorized":
            raise SystemExit(f"{serial}: 폰에서 USB 디버깅을 허용해 주세요.")
    if not any(state == "device" for _, state in found):
        raise SystemExit(f"사용 가능한 기기가 없습니다: {found}")


# ---------- 입력 ----------

def tap(x, y):
    shell(f"input tap {int(x)} {int(y)}")


def swipe(x1, y1, x2, y2, ms=300):
    shell(f"input swipe {int(x1)} {int(y1)} {int(x2)} {int(y2)} {int(ms)}")


def long_press(x, y, ms=1000):
    swipe(x, y, x, y, ms)


def key(code):
    shell(f"input keyevent {code}")


def text(s):
    """영문·숫자 입력. 공백은 %s로, 특수문자는 역슬래시로 감싼다."""
    escaped = re.sub(r"([\\&|;<>()$`'\"*?#~])", r"\\\1", s).replace(" ", "%s")
    shell(f"input text {escaped}")


# ---------- 앱 ----------

def launch(package):
    shell(f"monkey -p {package} -c android.intent.category.LAUNCHER 1")


def stop(package):
    shell(f"am force-stop {package}")


def open_url(url, package=None):
    """URL을 연다. package를 주면 그 앱으로 연다."""
    cmd = f"am start -a android.intent.action.VIEW -d '{url}'"
    if package:
        cmd += f" {package}"
    shell(cmd)


def current_app():
    """지금 화면에 떠 있는 (패키지명, 액티비티명)."""
    out = shell("dumpsys activity activities | grep topResumedActivity")
    m = re.search(r"u0 ([^/\s]+)/(\S+)", out)
    return (m.group(1), m.group(2)) if m else (None, None)


# ---------- 화면 ----------

def screenshot(path="screen.png"):
    with open(path, "wb") as f:
        f.write(adb("exec-out", "screencap", "-p"))
    return path


def screen_size():
    m = re.search(r"(\d+)x(\d+)", shell("wm size"))
    return int(m.group(1)), int(m.group(2))


def dump_ui():
    """화면 구조를 읽어 XML 루트 요소를 돌려준다."""
    shell("uiautomator dump /sdcard/ui.xml", timeout=20)
    return ET.fromstring(adb("exec-out", "cat", "/sdcard/ui.xml"))


def center(node):
    """bounds="[x1,y1][x2,y2]"의 가운데 좌표."""
    x1, y1, x2, y2 = map(int, re.findall(r"\d+", node.get("bounds")))
    return (x1 + x2) // 2, (y1 + y2) // 2


def find(text=None, desc=None, rid=None, exact=False, root=None):
    """조건에 맞는 첫 요소를 찾는다. 없으면 None."""
    root = root if root is not None else dump_ui()

    def match(value, want):
        if want is None:
            return True
        return value == want if exact else want in value

    for node in root.iter("node"):
        if (match(node.get("text", ""), text)
                and match(node.get("content-desc", ""), desc)
                and match(node.get("resource-id", ""), rid)):
            return node
    return None


def wait_for(text=None, desc=None, rid=None, timeout=10, interval=0.5):
    """요소가 나타날 때까지 기다린다. 시간 안에 못 찾으면 None."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            node = find(text=text, desc=desc, rid=rid)
        except (AdbError, ET.ParseError):
            node = None  # 화면이 움직이는 중이면 dump가 실패할 수 있다
        if node is not None:
            return node
        time.sleep(interval)
    return None


def tap_text(text, timeout=10):
    """글자(또는 접근성 설명)가 있는 요소를 찾아 가운데를 누른다."""
    node = wait_for(text=text, timeout=timeout) or wait_for(desc=text, timeout=1)
    if node is None:
        raise AdbError(f"화면에서 '{text}'를 찾지 못했습니다")
    tap(*center(node))
    return node


def scroll_to_text(text, max_scrolls=8):
    """글자가 보일 때까지 아래로 스크롤하며 찾는다. 못 찾으면 None."""
    w, h = screen_size()
    for _ in range(max_scrolls):
        node = find(text=text)
        if node is not None:
            return node
        swipe(w // 2, h * 3 // 4, w // 2, h * 3 // 8, 400)
        time.sleep(0.8)
    return None


if __name__ == "__main__":
    check_device()
    print("기기:", devices())
    print("해상도:", screen_size())
    print("현재 앱:", current_app())
