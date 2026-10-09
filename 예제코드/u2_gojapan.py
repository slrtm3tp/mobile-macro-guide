"""10장 예제: uiautomator2로 같은 매크로를 더 짧게.

준비:
    pip3 install uiautomator2
사용법:
    python3 u2_gojapan.py
"""
import uiautomator2 as u2

PACKAGE = "ctrip.english"
URL = "https://kr.trip.com/sale/w/37676/gojapan.html?locale=ko-KR&transparentBar=1&wkp=1"

d = u2.connect()                      # USB로 연결된 폰 (여러 대면 u2.connect("시리얼"))
print("기기:", d.info.get("productName"), d.window_size())

d.app_stop(PACKAGE)
d.open_url(URL)                       # 기본 앱으로 연다. 트립닷컴이 설치돼 있으면 앱에서 열림
d.sleep(4)
print("현재 앱:", d.app_current())

# 글자가 화면에 나타날 때까지 최대 10초 기다린다
if d(textContains="할인").wait(timeout=10):
    print("✅ 할인 관련 글자를 찾았습니다")
else:
    print("⚠️ 글자가 보이지 않습니다 (웹 화면은 글자가 안 잡힐 수 있음)")

d.swipe_ext("up", scale=0.6)          # 화면의 60%만큼 위로 밀기 = 아래 내용 보기
d.screenshot("u2_gojapan.png")
print("캡처 완료: u2_gojapan.png")
