"""8장 예제: 스크린샷에서 버튼 그림을 찾아 누른다.

준비:
    pip3 install opencv-python numpy
    1. python3 image_match.py crop 400 1100 300 120 button.png
       → 현재 화면에서 (x=400, y=1100) 위치의 300x120 영역을 button.png로 저장
    2. python3 image_match.py find button.png
       → 화면에서 button.png를 찾아 위치와 일치도 출력
    3. python3 image_match.py tap button.png
       → 찾아서 누르기
"""
import sys
import time

import cv2
import numpy as np

from adb_helper import adb, check_device, tap


def grab_screen():
    """현재 화면을 OpenCV 이미지(BGR 배열)로 가져온다."""
    png = adb("exec-out", "screencap", "-p")
    return cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_COLOR)


def find_image(template_path, threshold=0.85, screen=None):
    """화면에서 템플릿을 찾아 (가운데 x, 가운데 y, 일치도)를 돌려준다. 없으면 None."""
    screen = grab_screen() if screen is None else screen
    tpl = cv2.imread(template_path)
    if tpl is None:
        raise FileNotFoundError(template_path)
    res = cv2.matchTemplate(screen, tpl, cv2.TM_CCOEFF_NORMED)
    _, score, _, (x, y) = cv2.minMaxLoc(res)
    if score < threshold:
        return None
    h, w = tpl.shape[:2]
    return x + w // 2, y + h // 2, score


def wait_image(template_path, timeout=10, threshold=0.85):
    deadline = time.time() + timeout
    while time.time() < deadline:
        hit = find_image(template_path, threshold)
        if hit:
            return hit
        time.sleep(0.5)
    return None


def tap_image(template_path, timeout=10, threshold=0.85):
    hit = wait_image(template_path, timeout, threshold)
    if hit is None:
        raise RuntimeError(f"화면에서 {template_path}를 찾지 못했습니다")
    x, y, score = hit
    tap(x, y)
    return hit


def crop(x, y, w, h, out):
    cv2.imwrite(out, grab_screen()[y:y + h, x:x + w])


if __name__ == "__main__":
    check_device()
    cmd, *args = sys.argv[1:] or ["help"]
    if cmd == "crop":
        x, y, w, h = map(int, args[:4])
        crop(x, y, w, h, args[4])
        print(f"{args[4]} 저장 완료")
    elif cmd == "find":
        print(find_image(args[0], threshold=0) or "없음")
    elif cmd == "tap":
        print("탭:", tap_image(args[0]))
    else:
        print(__doc__)
