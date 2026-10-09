"""10장 예제: uiautomator2로 같은 매크로를 더 짧게.

준비:
    pip3 install uiautomator2
사용법:
    python3 u2_example.py
"""
import uiautomator2 as u2

CHROME = "com.android.chrome"

d = u2.connect()                      # USB로 연결된 폰 (여러 대면 u2.connect("시리얼"))
print("기기:", d.info.get("productName"), d.window_size())

# 1. 설정 → 디스플레이 들어가기
d.app_start("com.android.settings", stop=True)
d(text="디스플레이").click(timeout=10)
if d(text="다크 모드").wait(timeout=5):
    print("✅ 디스플레이 메뉴에 들어왔습니다")
d.screenshot("u2_display.png")

# 2. 크롬에서 한글로 검색하기 (키보드를 바꾸지 않아도 한글 입력 가능)
d.app_stop(CHROME)
d.shell(f"am start -a android.intent.action.VIEW -d about:blank {CHROME}")   # 빈 탭으로 시작
d(resourceId=f"{CHROME}:id/url_bar").click(timeout=10)                      # 주소창
d.send_keys("서울 날씨", clear=True)
d.press("enter")
d.sleep(3)
print("현재 앱:", d.app_current())

d.swipe_ext("up", scale=0.6)          # 화면의 60%만큼 위로 밀기 = 아래 내용 보기
d.screenshot("u2_weather.png")
print("캡처 완료: u2_display.png, u2_weather.png")
