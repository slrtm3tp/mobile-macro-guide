# 모바일 매크로 A to Z

2026-10-09 기준 · 안드로이드 + ADB + Python 중심 입문 가이드. 예제 스크립트는 [macro.py](macro.py).

## 목차

1. [큰 그림](#1-큰-그림)
2. [준비: 연결까지](#2-준비-연결까지)
3. [ADB 기본 명령](#3-adb-기본-명령)
4. [누를 위치 찾기](#4-누를-위치-찾기)
5. [원하는 화면으로 바로 가기](#5-원하는-화면으로-바로-가기)
6. [Python으로 매크로 짜기](#6-python으로-매크로-짜기)
7. [고급 기법](#7-고급-기법)
8. [더 나은 도구](#8-더-나은-도구)
9. [문제 해결](#9-문제-해결)
10. [주의사항 · 학습 순서 · 치트시트](#10-주의사항--학습-순서--치트시트)

## 1. 큰 그림

모바일 매크로는 사람 대신 폰 화면을 누르고, 밀고, 입력하는 프로그램이에요. 안드로이드라면 **PC에서 ADB로 조종하는 방식**부터 배우는 게 가장 빠르고 확실해요. 이 저장소의 `macro.py`가 바로 이 방식이에요.

| 방식 | 어디서 실행 | 폰 | 난이도 | 잘하는 것 | 한계 |
| --- | --- | --- | --- | --- | --- |
| ADB + Python | PC (Mac) | 안드로이드 | 쉬움 | 탭·스와이프·앱 열기·화면 읽기 전부 | PC와 연결돼 있어야 함 |
| uiautomator2 (Python 라이브러리) | PC | 안드로이드 | 보통 | 글자·ID로 요소 찾기가 훨씬 편함 | 폰에 도우미 앱 설치 필요 |
| Appium | PC | 안드로이드·iOS | 어려움 | 앱 테스트 자동화의 표준 | 설정이 많음 |
| MacroDroid · Tasker · Auto.js | 폰 안 | 안드로이드 | 쉬움~보통 | PC 없이 혼자 실행, 시간·알림 조건 | 복잡한 화면 판단은 약함 |
| 단축어 (Shortcuts) | 폰 안 | iOS | 쉬움 | 앱·URL 열기, 메시지, 설정 | 화면 좌표 탭 불가 |

**추천 학습 순서**: ADB 명령 몇 개 → 좌표로 누르기 → 글자로 찾아 누르기 → URL로 바로 열기 → Python으로 묶기 → 정해진 시각에 자동 실행.

## 2. 준비: 연결까지

adb를 설치하고 폰에서 USB 디버깅을 허용하면 끝이에요. `adb devices`에 `device`라고 뜨면 성공이에요.

1. **adb 설치 (Mac)**: `brew install android-platform-tools`
2. **개발자 옵션 켜기**: 설정 → 휴대전화 정보 → 소프트웨어 정보 → 빌드번호 7번 탭
3. **USB 디버깅 켜기**: 설정 → 개발자 옵션 → USB 디버깅
4. **연결**: 데이터 케이블로 연결 → 폰에 뜨는 "USB 디버깅 허용"에서 **항상 허용** 체크 후 허용
5. **확인**: `adb devices`

| `adb devices` 결과 | 뜻 | 할 일 |
| --- | --- | --- |
| `SERIAL  device` | 연결 성공 | 바로 사용 |
| `unauthorized` | 폰에서 아직 허용 안 함 | 폰 잠금 해제 → 허용. 그래도 안 되면 `adb kill-server` 후 다시 `adb devices` |
| 아무것도 없음 | 케이블·디버깅 문제 | 충전 전용 케이블인지 확인, USB 디버깅 다시 켜기 |
| `offline` | 연결이 꼬임 | 케이블 다시 꽂기, `adb kill-server` |

**무선 연결 (케이블 없이)**: 폰과 Mac이 같은 와이파이에 있어야 해요. 개발자 옵션 → **무선 디버깅** → "페어링 코드로 기기 페어링"에 나오는 IP:포트와 코드를 쓰면 돼요.

```bash
adb pair 192.168.0.12:37123      # 페어링 코드 입력 (처음 한 번)
adb connect 192.168.0.12:41234   # 무선 디버깅 화면 상단의 IP:포트
```

## 3. ADB 기본 명령

매크로의 90%는 아래 명령 몇 개의 조합이에요. 터미널에 하나씩 직접 쳐 보면서 익히세요.

| 하고 싶은 것 | 명령 | 메모 |
| --- | --- | --- |
| 탭 | `adb shell input tap 540 1200` | x, y 픽셀 좌표 |
| 길게 누르기 | `adb shell input swipe 540 1200 540 1200 1000` | 같은 자리를 1000ms 동안 스와이프 |
| 스와이프 | `adb shell input swipe 540 1600 540 600 300` | 시작 x y, 끝 x y, 시간(ms) |
| 글자 입력 | `adb shell input text hello` | 영문·숫자만. 띄어쓰기는 `%s` |
| 키 누르기 | `adb shell input keyevent KEYCODE_BACK` | HOME, BACK, ENTER, APP_SWITCH, POWER |
| 화면 캡처 | `adb exec-out screencap -p > screen.png` | PC에 바로 저장 |
| 화면 녹화 | `adb shell screenrecord /sdcard/a.mp4` | Ctrl+C로 종료 후 `adb pull` |
| 앱 목록 | `adb shell pm list packages -3` | 직접 설치한 앱만 |
| 앱 실행 | `adb shell monkey -p ctrip.english -c android.intent.category.LAUNCHER 1` | 패키지명으로 실행 |
| 주소로 열기 | `adb shell am start -a android.intent.action.VIEW -d "'URL'" 패키지명` | URL 안의 `&` 때문에 작은따옴표로 한 번 더 감싸기 |
| 앱 강제 종료 | `adb shell am force-stop ctrip.english` | 매크로 시작 전 초기화용 |
| 지금 떠 있는 화면 | `adb shell dumpsys activity activities \| grep topResumedActivity` | 어느 앱·화면인지 |
| 화면 해상도 | `adb shell wm size` | 예: 1440x3120 |
| 화면 구조 읽기 | `adb shell uiautomator dump /sdcard/ui.xml` | 4장에서 자세히 |

기기가 여러 대면 모든 명령에 `-s 시리얼번호`를 붙여요. 예: `adb -s SERIAL shell input tap 540 1200`

## 4. 누를 위치 찾기

좌표는 빠르지만 화면이 바뀌면 깨져요. 가능하면 **글자나 ID로 요소를 찾아** 누르는 게 훨씬 튼튼해요.

### 방법 A: 좌표

- **포인터 위치**: 개발자 옵션 → 포인터 위치를 켜면 화면 위쪽에 터치 좌표가 떠요. 가장 쉬움.
- **스크린샷**: `python3 macro.py screenshot` → 이미지 편집기(미리보기 앱)에서 픽셀 위치 확인.
- **주의**: 좌표는 해상도 기준이에요. 다른 폰에서는 좌표를 다시 잡아야 해요. 가로 화면이면 x·y가 바뀌어요.

### 방법 B: 화면 요소 (추천)

```bash
adb shell uiautomator dump /sdcard/ui.xml
adb exec-out cat /sdcard/ui.xml > ui.xml
```

`ui.xml` 안에는 화면의 모든 버튼·글자가 이런 줄로 들어 있어요.

```xml
<node text="이벤트" resource-id="ctrip.english:id/xxx" content-desc="이벤트" clickable="true" bounds="[320,400][560,480]" />
```

| 속성 | 뜻 | 찾기에 쓸 때 |
| --- | --- | --- |
| `text` | 화면에 보이는 글자 | 가장 자주 씀 |
| `content-desc` | 접근성 설명 (아이콘 버튼) | 글자 없는 버튼 |
| `resource-id` | 개발자가 붙인 이름 | 글자가 바뀌어도 안 변함. 단, 앱 업데이트 때 바뀔 수 있음 |
| `bounds` | `[왼쪽,위][오른쪽,아래]` | 가운데 = 누를 좌표 |

`bounds="[320,400][560,480]"`의 가운데는 x = (320+560)/2 = 440, y = (400+480)/2 = 440. `macro.py`의 `tap_text`가 이 계산을 자동으로 해요.

**안 되는 경우**: 배너가 이미지만 있으면 글자가 없어요(트립닷컴 프로모션 배너가 그랬어요). 게임이나 웹뷰 화면은 요소가 거의 안 보일 수 있어요. 이때는 좌표나 7장의 이미지 매칭을 써요.

## 5. 원하는 화면으로 바로 가기

화면을 하나씩 눌러 들어가는 것보다 **그 화면의 주소(URL)로 바로 여는 게** 빠르고 절대 안 틀려요. 매크로를 짤 때 가장 먼저 주소를 찾아보세요.

### 열기 방법 3가지

| 방법 | 명령 | 어디까지 가나 |
| --- | --- | --- |
| 앱 실행 | `monkey -p 패키지명 ...` | 앱 첫 화면 (또는 마지막 화면) |
| 딥링크 | `am start -a android.intent.action.VIEW -d "'myapp://...'"` | 앱 안 특정 화면 |
| 웹 URL + 패키지 | `am start -a android.intent.action.VIEW -d "'https://...'" 패키지명` | 앱이 그 주소를 지원하면 앱 안에서 열림 |

### 숨은 주소 찾는 법

1. **공유 버튼** → 링크 복사. 가장 확실해요.
2. **폰 클립보드에서 꺼내기**: 안드로이드 10부터는 adb로 클립보드를 직접 못 읽어요. 대신 크롬 주소창에 붙여넣고(`keyevent 279` = 붙여넣기) 그 글자를 `uiautomator dump`로 읽어요. Enter는 안 눌러요.
3. **웹 디버깅**: `adb shell cat /proc/net/unix | grep devtools`에 그 앱의 소켓이 있으면 크롬 `chrome://inspect`에서 웹뷰 주소가 보여요. 대부분의 상용 앱(트립닷컴 포함)은 꺼져 있어요.
4. **로그**: `adb logcat`에 주소가 찍히는 앱도 있어요. 운에 달렸어요.

### 실습 사례: 트립닷컴 고재팬

- 처음 시도: 홈 → 프로모션 배너를 넘기며 찾기. 배너가 이미지라 글자가 없고, 자동으로 돌아가서 번호(N/16)도 계속 바뀌어 실패.
- 웹 디버깅: 트립닷컴은 꺼져 있어 실패.
- 성공: 공유 링크를 클립보드에 복사 → 크롬 주소창에 붙여넣어 읽기 → 아래 명령으로 앱 안에서 바로 열림.

```bash
adb shell am start -a android.intent.action.VIEW -d "'https://kr.trip.com/sale/w/37676/gojapan.html?locale=ko-KR&transparentBar=1&wkp=1'" ctrip.english
```

링크 끝의 `&d=...` 같은 추적용 값은 빼도 돼요. 안 열리면 다시 붙여서 시도하세요.

## 6. Python으로 매크로 짜기

Python은 adb 명령을 차례로 실행해 주는 접착제예요. `macro.py`는 **`STEPS` 목록만 고치면 되도록** 만들어져 있어요.

### 핵심 구조

```python
import subprocess, time

def adb(*args):
    # "adb shell input tap 540 1200" 같은 명령을 실행하고 결과를 돌려줌
    return subprocess.run(["adb", *map(str, args)], check=True, capture_output=True).stdout

STEPS = [
    ("open", "https://kr.trip.com/sale/w/37676/gojapan.html?locale=ko-KR", "ctrip.english"),
    ("wait", 3),
    ("tap_text", "할인 혜택 확인"),
]

for step in STEPS:
    run_step(step)   # 동작 이름에 따라 알맞은 adb 명령 실행
```

### macro.py가 알아듣는 동작

| 동작 | 쓰는 법 | 하는 일 |
| --- | --- | --- |
| `tap` | `("tap", 540, 1200)` | 좌표 탭 |
| `swipe` | `("swipe", 540, 1600, 540, 600, 300)` | 스와이프 |
| `text` | `("text", "hello")` | 영문 입력 |
| `key` | `("key", "KEYCODE_BACK")` | 키 입력 |
| `wait` | `("wait", 1.5)` | 초 단위 대기 |
| `launch` | `("launch", "ctrip.english")` | 앱 실행 |
| `open` | `("open", "URL", "패키지명")` | 주소로 바로 열기 |
| `tap_text` | `("tap_text", "이벤트", 10)` | 글자 찾아 탭, 최대 10초 기다림 |

### 잘 짜는 요령

- **고정 대기보다 “나타날 때까지 대기”**: `wait 5`를 여러 번 넣지 말고 `tap_text`처럼 화면에 나타날 때까지 확인하면 빠르고 안정적이에요.
- **시작 상태를 맞추기**: 처음에 `am force-stop`으로 앱을 꺼두면 매번 같은 화면에서 시작해요.
- **실패하면 멈추거나 재시도**: 요소를 못 찾으면 `RuntimeError`가 나요. 반복 매크로라면 `try/except`로 감싸고 다시 시도하세요.
- **사람처럼**: 너무 빠른 반복은 앱이 막을 수 있어요. 동작 사이에 0.3~1초 정도 두세요.

실행: `python3 macro.py` (멈추기는 Ctrl+C). 캡처는 `python3 macro.py screenshot`, 앱 목록은 `python3 macro.py apps`.

## 7. 고급 기법

기본이 익숙해지면 아래 다섯 가지가 매크로를 한 단계 올려줘요.

### 자동으로 돌아가는 배너

배너는 몇 초마다 스스로 넘어가서, 화면을 읽는 사이(1~2초)에 번호가 바뀌어요. 방법은 세 가지예요.

1. **주소로 우회 (최선)**: 5장처럼 배너가 여는 페이지 주소를 찾아 바로 열기.
2. **누른 채로 넘기기**: 스와이프 중에는 자동 회전이 멈추는 앱이 많아요.
3. **이미지로 확인 후 즉시 탭**: 아래 이미지 매칭.

### 이미지 매칭 (OpenCV)

글자가 없는 버튼·배너는 사진으로 찾아요. 누를 부분을 작게 잘라 `button.png`로 저장해 두고, 현재 화면에서 그 위치를 찾아 눌러요.

```python
# pip3 install opencv-python numpy
import cv2, numpy as np

def find_image(template_path, threshold=0.85):
    screen = cv2.imdecode(np.frombuffer(adb("exec-out", "screencap", "-p"), np.uint8), cv2.IMREAD_COLOR)
    tpl = cv2.imread(template_path)
    res = cv2.matchTemplate(screen, tpl, cv2.TM_CCOEFF_NORMED)
    _, score, _, (x, y) = cv2.minMaxLoc(res)
    if score < threshold:
        return None
    h, w = tpl.shape[:2]
    return x + w // 2, y + h // 2
```

같은 해상도에서 자른 이미지여야 잘 맞아요. 다크 모드를 바꾸면 다시 자르세요.

### 정해진 시각에 실행

예: 매주 수요일 10시 정각에 쿠폰 페이지 열기.

- **간단하게 (Python 안에서 기다리기)**: 목표 시각까지 `time.sleep`으로 기다렸다가 실행. Mac이 잠들면 안 돼요.
- **cron (Mac이 켜져 있을 때 자동)**: `crontab -e`에 아래 한 줄. 형식은 `분 시 일 월 요일`, 3 = 수요일.

```bash
0 10 * * 3 cd ~/Desktop/adb-macro && /opt/homebrew/bin/adb devices && python3 macro.py >> macro.log 2>&1
```

- **정각에 누르기**: 시작 1~2분 전에 페이지를 열어 두고, 정각까지 기다렸다가 탭하세요. 앱을 여는 데 몇 초가 걸리기 때문이에요.

### 한글 입력

`input text`는 한글을 못 써요. [ADBKeyboard](https://github.com/senzhk/ADBKeyBoard)를 설치하고 기본 키보드로 바꾼 뒤 이렇게 보내요.

```bash
adb shell am broadcast -a ADB_INPUT_TEXT --es msg '안녕하세요'
```

또는 8장의 uiautomator2의 `d.send_keys("안녕")`을 쓰면 따로 설치할 게 없어요.

### 여러 대 동시에

`adb devices`로 시리얼을 모두 가져와서 기기마다 `adb -s 시리얼 ...`을 실행해요. 동시에 돌리려면 기기마다 Python `threading`으로 나눠요.

## 8. 더 나은 도구

ADB가 익숙해지면 **uiautomator2**와 **scrcpy** 두 개만 추가해도 매크로가 훨씬 편해져요.

| 도구 | 용도 | 설치 | 한 줄 예시 |
| --- | --- | --- | --- |
| [scrcpy](https://github.com/Genymobile/scrcpy) | 폰 화면을 Mac에 띄우고 마우스로 조작 | `brew install scrcpy` | `scrcpy` |
| [uiautomator2](https://github.com/openatx/uiautomator2) | Python으로 글자·ID 찾아 누르기, 한글 입력 | `pip3 install uiautomator2` | `d(text="이벤트").click()` |
| [weditor](https://github.com/alibaba/web-editor) | uiautomator2용 화면 요소 확인기 (브라우저) | `pip3 install weditor` | `weditor` |
| [Appium](https://appium.io) | 안드로이드·iOS 앱 테스트 자동화 표준 | `npm i -g appium` | 개발자용 |
| [MacroDroid](https://www.macrodroid.com) | 폰 안에서 조건 → 동작 매크로 | Play 스토어 | 시간·알림·위치가 조건 |
| Tasker | MacroDroid보다 강력, 더 어려움 | Play 스토어 (유료) | |
| Auto.js 계열 (AutoX.js) | 폰 안에서 JavaScript 매크로 | APK 직접 설치 | 출처 확인 필수 |
| 단축어 (iOS) | 앱·URL 열기, 자동화 조건 | 기본 앱 | URL 열기 → 고재팬 링크 |

### uiautomator2 맛보기

```python
import uiautomator2 as u2

d = u2.connect()                      # USB로 연결된 폰 (처음에 폰에 도우미 앱 자동 설치)
d.open_url("https://kr.trip.com/sale/w/37676/gojapan.html?locale=ko-KR")
d(text="할인 혜택 확인").click(timeout=10)   # 나타날 때까지 기다렸다가 탭
d.swipe_ext("up")                     # 위로 스크롤
d.send_keys("오사카")                  # 한글 입력
d.screenshot("screen.png")
```

macro.py의 기능을 대부분 한 줄로 해주고, 화면 읽기도 훨씬 빨라요. ADB 원리를 이해한 뒤 여기로 넘어가는 걸 추천해요.

### iOS는?

아이폰은 안드로이드처럼 PC에서 화면을 마음대로 누르기 어려워요. 현실적인 선택은 두 가지예요.

- **단축어**: “URL 열기” 동작으로 트립닷컴 고재팬 링크를 열고, 자동화 탭에서 “매주 수요일 9:58” 같은 조건을 걸 수 있어요. 화면 탭은 못 해요.
- **Appium + WebDriverAgent**: 탭까지 되지만 Xcode와 개발자 인증서가 필요해서 입문용으로는 무거워요.

## 9. 문제 해결

막히면 증상을 아래 표에서 찾아보세요. 대부분 연결·위치·따옴표 문제예요.

| 증상 | 원인 | 해결 |
| --- | --- | --- |
| `unauthorized` | 폰에서 허용 안 함 | 폰 잠금 해제 후 허용 → `adb kill-server` → `adb devices` |
| 기기 목록이 비어 있음 | 충전 전용 케이블, USB 디버깅 꺼짐 | 데이터 케이블로 교체, USB 모드를 파일 전송으로 |
| `can't open file '.../macro.py'` | 터미널이 다른 폴더에 있음 | `cd 파일이있는폴더` 후 실행 |
| URL이 중간에서 잘림 | `&`를 폰 셸이 명령 구분자로 읽음 | URL을 `"'...'"`처럼 두 번 감싸기 |
| 캡처가 검은 화면 | 앱이 캡처를 막음 (은행·증권·일부 게임) | 이 앱은 화면 읽기 불가. 좌표로만 가능 |
| `uiautomator dump` 실패 또는 항목이 거의 없음 | 애니메이션 중, 게임·웹뷰 화면 | 잠깐 기다렸다가 다시. 안 되면 이미지 매칭 |
| 글자는 찾았는데 눌러도 반응 없음 | 글자는 누를 수 없는 요소, 위에 다른 창(PIP 등)이 덮음 | 부모 요소(`clickable="true"`)의 bounds 사용, 화살표 치우기 |
| 좌표가 어긋남 | 화면 회전, 다른 해상도 폰 | `adb shell wm size`로 확인 후 다시 잡기 |
| 한글이 안 입력됨 | `input text`는 ASCII만 | ADBKeyboard 또는 uiautomator2 |
| `pm list`에 `SecurityException ... user 150` | 보안 폴더·듀얼 메신저 사용자 | 무시해도 됨. 기본 사용자 앱은 정상 출력 |
| 배너 번호가 계속 바뀌어 못 누름 | 자동 회전 | 주소로 바로 열기 (5장) |

## 10. 주의사항 · 학습 순서 · 치트시트

매크로는 내 폰에서 내가 할 일을 대신하는 데만 쓰세요. 서비스 약관을 어기면 계정이 정지될 수 있어요.

### 주의사항

- **약관**: 게임 자동 사냥, 티켓·한정판 선착순 매크로는 대부분 금지예요. 쿠폰 페이지를 여는 것처럼 사람이 할 행동을 편하게 하는 수준이 안전해요.
- **속도**: 너무 빠르거나 일정한 반복은 봇으로 감지돼요.
- **보안**: USB 디버깅이 켜져 있으면 연결된 PC가 폰을 거의 전부 조작할 수 있어요. 안 쓸 때는 꺼 두고, 모르는 PC의 허용 창은 거절하세요.
- **출처**: APK나 매크로 스크립트는 공식 저장소·스토어에서만 받으세요.
- **로그인·결제는 사람이**: 비밀번호를 스크립트에 적지 마세요.

### 학습 순서

- [ ] 1일차: `adb devices`, `tap`, `swipe`, `keyevent`를 터미널에서 직접 쳐 보기
- [ ] 2일차: 포인터 위치로 좌표 잡고 `macro.py`의 `STEPS` 고쳐 실행하기
- [ ] 3일차: `uiautomator dump` 결과 읽고 `tap_text`로 바꾸기
- [ ] 4일차: 자주 가는 화면의 주소를 찾아 `open`으로 바로 열기
- [ ] 5일차: scrcpy와 uiautomator2 설치해서 같은 매크로 다시 짜기
- [ ] 6일차: cron으로 정해진 시각에 실행, 필요하면 이미지 매칭

### 치트시트

```bash
adb devices                                            # 연결 확인
adb kill-server                                        # 연결 초기화
adb shell wm size                                      # 해상도
adb shell input tap X Y                                # 탭
adb shell input swipe X1 Y1 X2 Y2 MS                   # 스와이프 / 길게 누르기
adb shell input text hello                             # 영문 입력
adb shell input keyevent KEYCODE_BACK                  # 뒤로 (HOME, ENTER, 279=붙여넣기)
adb exec-out screencap -p > screen.png                 # 캡처
adb shell uiautomator dump /sdcard/ui.xml              # 화면 구조
adb exec-out cat /sdcard/ui.xml > ui.xml               # PC로 가져오기
adb shell pm list packages -3                          # 앱 목록
adb shell monkey -p PKG -c android.intent.category.LAUNCHER 1   # 앱 실행
adb shell am start -a android.intent.action.VIEW -d "'URL'" PKG  # 주소로 열기
adb shell am force-stop PKG                            # 앱 종료
adb shell dumpsys activity activities | grep topResumedActivity  # 현재 화면
```
