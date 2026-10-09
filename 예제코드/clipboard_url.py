"""7장 예제: 폰 클립보드의 내용을 크롬 주소창에 붙여넣어 읽어 온다.

안드로이드 10부터는 adb로 클립보드를 직접 읽을 수 없어서 쓰는 우회 방법이다.
주소창에 붙여넣기만 하고 Enter는 누르지 않으므로 페이지 이동은 일어나지 않는다.

사용법:
    1. 폰에서 원하는 페이지의 "공유 → 링크 복사"
    2. python3 clipboard_url.py
"""
import time

from adb_helper import center, check_device, find, key, shell, tap, wait_for

CHROME = "com.android.chrome"
URL_BAR = "com.android.chrome:id/url_bar"


def read_clipboard_via_chrome():
    shell(f"am start -a android.intent.action.VIEW -d about:blank {CHROME}")
    bar = wait_for(rid=URL_BAR, timeout=10)
    if bar is None:
        raise SystemExit("크롬 주소창을 찾지 못했습니다")
    tap(*center(bar))                 # 주소창 선택
    time.sleep(1)
    key("KEYCODE_MOVE_END")
    key("KEYCODE_DEL")                # 기존 내용(about:blank 등) 정리
    key("KEYCODE_PASTE")              # 붙여넣기 (279)
    time.sleep(1)
    value = find(rid=URL_BAR).get("text", "")
    key("KEYCODE_ESCAPE")             # 주소창 편집 취소 (이동하지 않음)
    key("KEYCODE_BACK")
    return value


if __name__ == "__main__":
    check_device()
    url = read_clipboard_via_chrome()
    print("클립보드 내용:", url)
