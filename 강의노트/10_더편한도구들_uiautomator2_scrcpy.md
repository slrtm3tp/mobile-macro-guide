# 10장 더 편한 도구들: scrcpy, uiautomator2, 폰 안의 매크로 앱

---

## 📚 **학습 목표 (Learning Objectives)**

이번 장을 마치면 여러분은 scrcpy로 폰 화면을 PC에 띄워 보면서 매크로를 개발할 수 있습니다. 또한 uiautomator2로 지금까지 직접 만든 기능(글자 찾기, 기다리기, 한글 입력)을 한 줄로 처리하고, PC 없이 폰 안에서 도는 MacroDroid·Tasker와 iOS 단축어의 쓰임새를 비교하여 상황에 맞는 도구를 고를 수 있게 됩니다.

---

## 1️⃣ **scrcpy: 폰 화면을 PC에**

scrcpy(스크린 카피)는 폰 화면을 PC 창에 실시간으로 띄우고 마우스·키보드로 조작하게 해 주는 무료 도구입니다. ADB를 이용하므로 앱 설치 없이 동작합니다.

```bash
brew install scrcpy      # Mac
scrcpy                   # 실행
```

```
┌──────── PC ────────┐
│  ┌──────────────┐  │      매크로를 실행하면
│  │  폰 화면 창    │  │ ◄─── 어디를 누르는지 PC에서 바로 보임
│  │  (실시간)     │  │
│  └──────────────┘  │      폰을 손에 들 필요 없음
└────────────────────┘
```

### **자주 쓰는 옵션**

| 옵션 | 의미 |
| --- | --- |
| `-m 1024` (`--max-size`) | 창 크기 제한 (가볍게) |
| `-S` (`--turn-screen-off`) | 폰 화면은 끄고 PC에만 표시 (배터리 절약) |
| `-w` (`--stay-awake`) | 연결 중 폰이 잠들지 않게 |
| `-t` (`--show-touches`) | 터치 위치를 점으로 표시 (매크로 확인에 유용) |
| `--record=demo.mp4` | 화면을 PC에 바로 녹화 (180초 제한 없음) |
| `-s 시리얼` | 여러 기기 중 선택 |

### **예제 1: 매크로 개발용 scrcpy 실행**

```bash
scrcpy -m 1024 -w -t --record=macro_run.mp4
```

터치 표시를 켜고 녹화하면서 다른 터미널에서 매크로를 실행하면, 매크로가 누른 위치가 영상에 점으로 남습니다. 실패한 지점을 찾는 데 아주 유용합니다.

---

## 2️⃣ **uiautomator2 소개**

5장에서 직접 만든 `dump_ui`, `find`, `wait_for`, `tap_text`를 기억하나요? uiautomator2는 이런 기능을 훨씬 빠르고 편하게 제공하는 Python 라이브러리입니다.

```
직접 만든 adb_helper                  uiautomator2

 uiautomator dump (1~2초)             폰 안의 도우미 서비스가 화면을 즉시 조회
 → 파일 복사 → XML 분석                (보통 수백 ms)
 → 찾기 → 가운데 계산 → tap            d(text="이벤트").click()

 한글 입력: ADBKeyboard 설치 필요       d.send_keys("오사카")
```

### **설치와 연결**

```bash
pip3 install uiautomator2
```

```python
import uiautomator2 as u2

d = u2.connect()              # USB 기기 하나일 때
# d = u2.connect("R5CT1234ABC")       # 시리얼 지정
# d = u2.connect("192.168.0.12:41234") # 무선

print(d.info)
```

```
{'currentPackageName': 'com.sec.android.app.launcher', 'displayHeight': 3120, 'displayWidth': 1440, 'productName': '...', 'screenOn': True, ...}
```

처음 연결하면 화면 조회에 필요한 도우미 프로그램이 폰에 자동으로 올라갑니다. (버전에 따라 폰에 설치 허용 창이 뜰 수 있으며, 그때는 허용하세요.)

---

## 3️⃣ **uiautomator2 기본 사용법**

### **앱과 화면**

| 기능 | 코드 |
| --- | --- |
| 앱 실행 | `d.app_start("ctrip.english")` |
| 앱 종료 후 실행 | `d.app_start("ctrip.english", stop=True)` |
| 앱 종료 | `d.app_stop("ctrip.english")` |
| 현재 앱 | `d.app_current()` → `{'package': ..., 'activity': ...}` |
| 주소 열기 | `d.open_url("https://...")` |
| 화면 크기 | `d.window_size()` → `(1440, 3120)` |
| 캡처 | `d.screenshot("a.png")` |
| 키 | `d.press("home")`, `d.press("back")`, `d.press("enter")` |

### **요소 찾기 (셀렉터)**

```python
d(text="이벤트")                     # 글자가 정확히 같은 요소
d(textContains="할인")               # 글자를 포함하는 요소
d(description="검색창")              # content-desc
d(resourceId="ctrip.english:id/gio") # resource-id
d(className="android.widget.EditText")  # 입력창
d(text="확인", clickable=True)       # 여러 조건 동시에
```

| 셀렉터 | XML 속성 |
| --- | --- |
| `text`, `textContains`, `textStartsWith` | `text` |
| `description`, `descriptionContains` | `content-desc` |
| `resourceId` | `resource-id` |
| `className` | `class` |
| `clickable`, `scrollable`, `enabled` | 같은 이름 |

### **요소로 할 수 있는 일**

```python
el = d(text="이벤트")

el.exists                   # 지금 있나? (True/False)
el.wait(timeout=10)         # 10초까지 기다리며 나타나면 True
el.click()                  # 가운데 탭
el.click(timeout=10)        # 나타날 때까지 기다렸다가 탭
el.long_click()             # 길게 누르기
el.get_text()               # 글자 읽기
el.info["bounds"]           # 위치 정보
```

### **입력과 제스처**

```python
d(className="android.widget.EditText").click()
d.send_keys("오사카 맛집", clear=True)     # 한글 OK, 기존 내용 지우고 입력
d.press("enter")

d.swipe_ext("up", scale=0.8)              # 화면의 80%만큼 위로 밀기 (아래 보기)
d.swipe_ext("left")                       # 다음 배너
d.swipe(720, 2400, 720, 900, 0.3)         # 좌표 스와이프 (시간은 초 단위!)
d(scrollable=True).scroll.to(text="휴대전화 정보")   # 보일 때까지 스크롤
```

> ⚠️ `d.swipe`의 시간은 **초** 단위입니다. adb의 `input swipe`(밀리초)와 다르니 주의하세요.

---

## 4️⃣ **같은 매크로, 두 가지 버전 비교**

### **예제 2: 설정 → 디스플레이 → 다크 모드 확인**

```python
# adb_helper 버전 (5장)
from adb_helper import *

stop("com.android.settings")
launch("com.android.settings")
tap_text("디스플레이")
if wait_for(text="다크 모드", timeout=5):
    screenshot("display.png")
```

```python
# uiautomator2 버전
import uiautomator2 as u2

d = u2.connect()
d.app_start("com.android.settings", stop=True)
d(text="디스플레이").click(timeout=10)
if d(text="다크 모드").wait(timeout=5):
    d.screenshot("display.png")
```

줄 수는 비슷하지만, uiautomator2는 화면 조회가 빨라 전체 실행 시간이 크게 줄고 한글 입력도 바로 됩니다.

### **예제 3: uiautomator2로 고재팬 열기**

전체 코드는 [`예제코드/u2_gojapan.py`](../예제코드/u2_gojapan.py)에 있습니다.

```python
import uiautomator2 as u2

d = u2.connect()
d.app_stop("ctrip.english")
d.open_url("https://kr.trip.com/sale/w/37676/gojapan.html?locale=ko-KR&transparentBar=1&wkp=1")
d.sleep(4)
print(d.app_current())
d.swipe_ext("up", scale=0.6)
d.screenshot("u2_gojapan.png")
```

```
{'package': 'ctrip.english', 'activity': 'com.ctrip.ibu.hybrid.v2.container.TripH5Container', ...}
```

`open_url`은 패키지를 지정하지 않으므로, 앱 선택 창이 뜨거나 브라우저로 열리면 7장의 `am start ... ctrip.english` 방식을 `d.shell(...)`로 실행하세요.

```python
d.shell(f"am start -a android.intent.action.VIEW -d '{URL}' ctrip.english")
```

---

## 5️⃣ **화면 요소 확인 도구**

XML을 직접 읽는 대신, 브라우저에서 화면을 보며 요소를 클릭해 속성을 확인할 수 있는 도구가 있습니다.

```bash
pip3 install uiautodev
uiautodev
```

브라우저가 열리면 기기를 선택하고, 화면에서 버튼을 클릭하면 `text`, `resourceId`, `bounds`와 함께 uiautomator2 코드가 표시됩니다. (예전 강의 자료에서 보이는 `weditor`의 후속 도구입니다.)

---

## 6️⃣ **폰 안에서 도는 매크로 앱**

PC 없이 폰 혼자 매크로를 돌리고 싶을 때 씁니다.

### **MacroDroid (안드로이드)**

"**트리거 → 액션 → 제약 조건**" 세 칸을 채우는 방식입니다.

```
예) 매주 수요일 9시 58분에 고재팬 페이지 열기

  트리거   : 요일/시간 → 수요일 09:58
  액션     : 웹사이트 열기 → https://kr.trip.com/sale/w/37676/gojapan.html?locale=ko-KR
             (또는 "인텐트 보내기"로 패키지 ctrip.english 지정)
  제약 조건 : Wi-Fi 연결됨
```

화면 탭(UI 상호작용) 액션도 있지만, 사용하려면 MacroDroid에 **접근성 권한**을 주어야 합니다. 접근성 권한은 화면 내용을 읽고 조작할 수 있는 강한 권한이므로 신뢰할 수 있는 앱에만 주세요.

### **Tasker (안드로이드, 유료)**

MacroDroid보다 기능이 많고 변수·조건문·반복을 쓸 수 있어 프로그래밍에 가깝습니다. 대신 배우기 어렵습니다.

### **단축어 (iOS)**

아이폰은 ADB 같은 방식으로 화면을 조작할 수 없습니다. 대신 단축어 앱의 **자동화**로 시각·장소·앱 실행 같은 조건에 따라 동작을 실행합니다.

```
단축어 앱 → 자동화 → 새로운 자동화 → 특정 시간
  시간: 오전 9:58 / 반복: 매주 수요일
  "즉시 실행" 선택 (실행 전에 묻지 않기)
  동작 추가: URL 열기 → https://kr.trip.com/sale/w/37676/gojapan.html?locale=ko-KR
```

화면의 특정 위치를 탭하는 동작은 없으므로, 주소로 열 수 있는 화면까지만 자동화할 수 있습니다.

---

## 7️⃣ **도구 고르기**

| 하고 싶은 것 | 추천 도구 |
| --- | --- |
| 원리 이해, 무엇이든 직접 제어 | ADB + Python (1~9장) |
| 글자로 찾아 누르기를 빠르고 편하게, 한글 입력 | uiautomator2 |
| 폰 화면 보면서 개발, 녹화 | scrcpy |
| PC 없이 시간·알림 조건으로 간단한 동작 | MacroDroid |
| 아이폰에서 특정 시각에 페이지 열기 | 단축어 |
| 안드로이드·iOS 앱을 같은 코드로 테스트 | Appium |

---

## 📝 **핵심 개념 정리**

scrcpy는 폰 화면을 PC에 띄우고 조작·녹화하는 도구로, `-t`(터치 표시)와 `--record`를 켜면 매크로가 누른 위치를 영상으로 확인할 수 있습니다.

uiautomator2는 폰 안의 도우미 서비스를 이용해 화면 요소를 빠르게 찾습니다. `d(text=...)`, `d(textContains=...)`, `d(resourceId=...)` 같은 셀렉터로 요소를 고르고 `.click(timeout=)`, `.wait(timeout=)`, `.exists`로 다룹니다. `send_keys`로 한글을 바로 입력할 수 있고, `d.swipe`의 시간은 초 단위입니다.

MacroDroid·Tasker는 PC 없이 폰 안에서 트리거와 액션으로 매크로를 돌리고, iOS 단축어는 화면 탭은 못 하지만 시각에 맞춰 URL을 여는 자동화를 할 수 있습니다.

---

## 💡 **실습 과제**

### **과제 1: adb_helper 매크로를 uiautomator2로 옮기기**

6장의 `macro_v2.py`에서 `run_step`의 각 동작을 uiautomator2 코드로 바꾼 `macro_u2.py`를 만들고, 두 버전의 전체 실행 시간을 비교하세요.

```python
# 힌트
import time
start = time.time()
...  # 매크로 실행
print(f"걸린 시간: {time.time() - start:.1f}초")
```

### **과제 2: 한글 검색 자동화**

uiautomator2로 크롬을 열고 검색창에 "오사카 날씨"를 입력해 검색한 뒤, 결과 화면에서 "°" 기호가 들어간 첫 글자를 읽어 출력하세요.

```python
# 힌트
d(textContains="°").get_text()
```

---

## ✅ **퀴즈**

### **[초급] 1번**

폰 화면을 PC 창에 띄우고 마우스로 조작하게 해 주는 도구는?

1. uiautomator2
2. scrcpy
3. MacroDroid
4. OpenCV

### **[초급] 2번**

uiautomator2에서 "할인"이라는 글자를 포함하는 요소를 고르는 코드는?

1. `d(text="할인")`
2. `d(textContains="할인")`
3. `d.find("할인")`
4. `d("할인")`

### **[중급] 3번**

다음 두 명령의 스와이프 시간이 같으려면 `?`에 들어갈 값은?

```
adb shell input swipe 720 2400 720 900 300
d.swipe(720, 2400, 720, 900, ?)
```

1. 300
2. 30
3. 3
4. 0.3

### **[중급] 4번**

uiautomator2의 `d(text="확인").click(timeout=10)`의 동작으로 옳은 것은?

1. 10번 누른다
2. 10초 뒤에 누른다
3. "확인"이 나타날 때까지 최대 10초 기다렸다가 누른다
4. 10초 동안 길게 누른다

### **[고급] 5번**

iOS 단축어 자동화로 할 수 **없는** 것은?

1. 매주 수요일 9시 58분에 실행하기
2. 특정 URL 열기
3. 앱 실행하기
4. 앱 화면의 특정 좌표를 탭하기

---

## 🔑 **퀴즈 정답 및 해설**

**1번 정답: 2**
scrcpy는 ADB를 이용해 폰 화면을 PC로 보여 주고 입력을 보냅니다. 폰에 앱을 설치할 필요가 없습니다.

**2번 정답: 2**
`textContains`는 포함 검색, `text`는 정확히 일치하는 검색입니다.

**3번 정답: 4**
adb의 `input swipe`는 밀리초(300ms), uiautomator2의 `d.swipe`는 초 단위이므로 0.3초입니다.

**4번 정답: 3**
`timeout`은 요소가 나타나기를 기다리는 최대 시간입니다. 나타나는 즉시 누르고, 10초 안에 안 나타나면 오류가 납니다.

**5번 정답: 4**
iOS는 보안 정책상 다른 앱의 화면을 좌표로 탭하는 자동화를 허용하지 않습니다. 시각에 맞춰 URL이나 앱을 여는 것은 가능합니다.

---

## 🎯 **다음 장 예고**

다음 장에서는 매크로를 만들며 만나는 문제들을 한곳에 모아 해결합니다. 연결 오류부터 검은 화면, 좌표 어긋남까지 증상별 해결법을 정리하고, 계정 정지 없이 안전하게 매크로를 쓰기 위한 약관과 보안 수칙을 배웁니다!

---

이 수업자료는 Claude를 이용하여 제작되었습니다.
