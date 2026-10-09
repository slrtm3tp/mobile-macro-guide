# 7장 원하는 화면으로 바로 가기: 딥링크와 URL

---

## 📚 **학습 목표 (Learning Objectives)**

이번 장을 마치면 여러분은 버튼을 여러 번 누르는 대신 주소(URL) 하나로 앱 속 특정 화면을 바로 열 수 있습니다. 인텐트와 딥링크의 개념을 이해하고, 공유 링크·클립보드·웹 디버깅·로그를 이용해 숨어 있는 주소를 찾아내는 방법을 트립닷컴 고재팬 실전 사례로 익히게 됩니다.

---

## 1️⃣ **왜 주소로 여는가?**

트립닷컴 앱에서 "고재팬" 이벤트 페이지에 들어가는 두 가지 방법을 비교해 봅니다.

```
방법 A: 버튼을 차례로 누르기                방법 B: 주소로 바로 열기

 앱 실행                                    am start -d "고재팬 주소" ctrip.english
   ↓ (홈이 아닌 다른 화면이 뜰 수도)                 │
 홈 화면                                           ▼
   ↓ 프로모션 배너 찾기                          고재팬 페이지 (끝!)
   ↓ 배너가 자동으로 넘어감 (16장 중 몇 번째?)
   ↓ 이미지라 글자로 못 찾음
 고재팬 배너 터치 … 실패할 확률 높음

  단계: 4~6개, 실패 지점 많음                  단계: 1개, 거의 실패 없음
```

화면 경로는 앱이 바뀌면 깨지지만, 주소는 그 페이지가 있는 한 그대로 동작합니다. **매크로를 만들 때는 항상 "이 화면의 주소가 있을까?"를 먼저 생각하세요.**

---

## 2️⃣ **인텐트와 딥링크**

### **인텐트 (Intent)**

안드로이드에서 "무엇을 해 달라"는 요청 메시지를 **인텐트**라고 합니다. 카카오톡에서 링크를 누르면 브라우저가 열리는 것도 인텐트 덕분입니다.

```bash
# 기본 구조
adb shell am start -a <동작> -d <데이터(주소)> [패키지명]
```

| 부분 | 의미 | 예 |
| --- | --- | --- |
| `-a` | 동작(action) | `android.intent.action.VIEW` = "이것을 보여 줘" |
| `-d` | 데이터(data), 보통 주소 | `https://...` 또는 `myapp://...` |
| 패키지명 | 어느 앱으로 열지 지정 (생략하면 선택 창이 뜨거나 기본 앱) | `ctrip.english` |

### **딥링크 (Deep Link)**

앱 안의 특정 화면을 가리키는 주소입니다. 두 종류가 있습니다.

| 종류 | 생김새 | 예 |
| --- | --- | --- |
| 앱 전용 주소 (커스텀 스킴) | `앱이름://경로` | `youtube://`, `kakaotalk://` |
| 웹 주소 (앱 링크) | `https://도메인/경로` | `https://kr.trip.com/sale/...` |

웹 주소형은 **앱이 설치되어 있으면 앱에서, 없으면 브라우저에서** 열립니다. 패키지명을 함께 주면 앱으로 열도록 지정할 수 있습니다.

### **예제 1: 여러 가지 주소 열어 보기**

```bash
# 웹페이지를 기본 브라우저로
adb shell am start -a android.intent.action.VIEW -d "https://www.google.com"

# 유튜브 영상을 유튜브 앱으로
adb shell am start -a android.intent.action.VIEW -d "https://www.youtube.com/watch?v=jNQXAC9IVRw" com.google.android.youtube

# 전화 걸기 화면 (번호만 입력된 상태, 실제로 걸지는 않음)
adb shell am start -a android.intent.action.DIAL -d "tel:01012345678"

# 지도에서 위치 검색
adb shell am start -a android.intent.action.VIEW -d "geo:0,0?q=Osaka+Station"

# 설정의 특정 화면
adb shell am start -a android.settings.BLUETOOTH_SETTINGS
```

```
Starting: Intent { act=android.intent.action.VIEW dat=https://www.youtube.com/... pkg=com.google.android.youtube }
```

---

## 3️⃣ **& 문자 함정: 따옴표를 두 번 감싸기**

주소에 `&`가 들어 있으면 문제가 생깁니다.

```bash
# ❌ 잘못된 예
adb shell am start -a android.intent.action.VIEW -d "https://kr.trip.com/sale/w/37676/gojapan.html?locale=ko-KR&transparentBar=1"
```

PC의 터미널은 큰따옴표를 벗겨서 폰에 보내는데, **폰의 셸이 `&`를 "여기서 명령을 끊고 뒤에서 실행하라"로 해석**합니다. 그래서 `locale=ko-KR`까지만 전달되고 뒷부분이 잘립니다.

```
PC 터미널                     폰의 셸이 받은 것
"...?locale=ko-KR&transparentBar=1"
        │ 큰따옴표 벗김
        ▼
 ...?locale=ko-KR & transparentBar=1
                  └─ "&" = 명령 구분자로 해석 → 뒷부분 잘림
```

```bash
# ✅ 올바른 예: 바깥 큰따옴표 + 안쪽 작은따옴표
adb shell am start -a android.intent.action.VIEW -d "'https://kr.trip.com/sale/w/37676/gojapan.html?locale=ko-KR&transparentBar=1&wkp=1'" ctrip.english
```

PC가 바깥 큰따옴표를 벗기고, 폰은 안쪽 작은따옴표 덕분에 주소 전체를 하나로 받습니다. Python에서도 같은 원리로 감쌉니다.

```python
shell(f"am start -a android.intent.action.VIEW -d '{url}' {package}")
```

---

## 4️⃣ **숨어 있는 주소 찾기**

앱 화면에는 주소창이 없으므로 주소를 알아내는 요령이 필요합니다. 쉬운 방법부터 시도합니다.

```
주소 찾기 순서

  ① 공유 버튼 → 링크 복사      ───► 가장 쉽고 확실
       │ 공유 버튼이 없다면
       ▼
  ② 웹 디버깅 (chrome://inspect) ───► 앱이 허용해야 가능
       │ 막혀 있다면
       ▼
  ③ 로그 (adb logcat)           ───► 앱에 따라 주소가 찍힘
       │ 안 찍힌다면
       ▼
  ④ 주소 없이 화면 요소·좌표·이미지로 들어가기
```

### **방법 ① 공유 링크 + 클립보드 읽기**

페이지의 **공유 → 링크 복사**를 누르면 주소가 폰 클립보드에 들어갑니다. 문제는 **안드로이드 10부터 adb로 클립보드를 직접 읽을 수 없다**는 점입니다. 그래서 다음 우회 방법을 씁니다.

```
클립보드 읽기 우회법

  크롬을 about:blank로 열기
        ↓
  주소창 터치 (주소창 resource-id = com.android.chrome:id/url_bar)
        ↓
  KEYCODE_PASTE (279) → 주소창에 클립보드 내용이 붙여넣어짐
        ↓
  uiautomator dump → 주소창의 text 읽기 = 클립보드 내용!
        ↓
  ESC → 이동하지 않고 편집 취소
```

### **예제 2: 클립보드에서 주소 꺼내기**

전체 코드는 [`예제코드/clipboard_url.py`](../예제코드/clipboard_url.py)에 있습니다.

```python
from adb_helper import center, find, key, shell, tap, wait_for

URL_BAR = "com.android.chrome:id/url_bar"

shell("am start -a android.intent.action.VIEW -d about:blank com.android.chrome")
bar = wait_for(rid=URL_BAR, timeout=10)
tap(*center(bar))
key("KEYCODE_MOVE_END")
key("KEYCODE_DEL")
key("KEYCODE_PASTE")
print(find(rid=URL_BAR).get("text"))
key("KEYCODE_ESCAPE")
```

```
https://kr.trip.com/sale/w/37676/gojapan.html?locale=ko-KR&transparentBar=1&wkp=1&d=202610912
```

실제로 트립닷컴 공유 링크를 이 방법으로 읽어 온 결과입니다.

### **방법 ② 웹 디버깅 소켓 확인**

앱 속 웹페이지(웹뷰)는 개발자가 디버깅을 허용했다면 PC 크롬에서 주소를 볼 수 있습니다.

```bash
adb shell cat /proc/net/unix | grep devtools_remote
```

```
... @chrome_devtools_remote
... @webview_devtools_remote_15421
```

`webview_devtools_remote_<번호>`의 번호는 그 웹뷰를 가진 앱의 프로세스 번호입니다. 대상 앱의 번호와 같은지 확인합니다.

```bash
adb shell pidof ctrip.english
# 16789    ← 목록에 webview_devtools_remote_16789가 없음 = 디버깅 막힘
```

번호가 일치하면 PC 크롬에서 `chrome://inspect`를 열어 웹뷰의 주소를 확인할 수 있습니다. 트립닷컴처럼 대부분의 상용 앱은 막혀 있습니다.

### **방법 ③ 로그 뒤지기**

```bash
adb logcat -c                                 # 기존 로그 지우기
# (폰에서 배너를 눌러 페이지 열기)
adb logcat -d | grep -oE 'https?://[^ "]+' | sort -u
```

앱이 주소를 로그에 남긴다면 이 방법으로 찾을 수 있습니다. 앱마다 다르며, 트립닷컴은 남기지 않았습니다.

---

## 5️⃣ **주소 다듬기**

복사한 주소에는 추적용 값이 붙어 있는 경우가 많습니다.

```
https://kr.trip.com/sale/w/37676/gojapan.html?locale=ko-KR&transparentBar=1&wkp=1&d=202610912
└──────────────── 페이지 주소 ────────────────┘└──────────── 쿼리(옵션) ────────────┘

  locale=ko-KR       → 한국어 페이지      (필요)
  transparentBar=1   → 앱 화면 표시 옵션    (있어도 무방)
  wkp=1              → 앱 내부 옵션        (있어도 무방)
  d=202610912        → 날짜·추적용 값      (빼도 됨)
```

뺄 수 있는 값을 하나씩 지워 보며 여전히 같은 페이지가 열리는지 확인합니다. 날짜·추적 값이 붙은 주소는 시간이 지나면 동작이 달라질 수 있으므로 빼는 편이 안전합니다.

### **예제 3: 고재팬 페이지 열기 매크로**

```python
from adb_helper import check_device, current_app, open_url, stop
import time

URL = "https://kr.trip.com/sale/w/37676/gojapan.html?locale=ko-KR&transparentBar=1&wkp=1"
PKG = "ctrip.english"

check_device()
stop(PKG)                 # 깨끗한 상태에서 시작
open_url(URL, PKG)        # 앱 안에서 바로 열기
time.sleep(4)

pkg, activity = current_app()
print("현재 화면:", pkg, activity)
if pkg == PKG and "H5Container" in activity:
    print("✅ 트립닷컴 웹페이지 화면이 열렸습니다")
```

```
현재 화면: ctrip.english com.ctrip.ibu.hybrid.v2.container.TripH5Container
✅ 트립닷컴 웹페이지 화면이 열렸습니다
```

`TripH5Container`는 트립닷컴이 웹페이지(H5)를 보여 줄 때 쓰는 화면입니다. 이 액티비티가 떴다면 주소가 앱 안에서 열린 것입니다.

---

## 6️⃣ **앱 전용 주소 알아내기 (고급)**

앱이 어떤 주소를 받아 주는지는 앱 정보에 적혀 있습니다.

```bash
adb shell dumpsys package ctrip.english | grep -A2 -E "Schemes:|Authorities:" | head -20
```

```
      Schemes:
        "myapp"
        "https"
      Authorities:
        "www.example.com"
```

(위 출력은 형식을 보여 주기 위한 예시입니다. 실제 값은 앱마다 다릅니다.)

`Schemes`는 `myapp://`처럼 앱 전용 주소의 앞부분, `Authorities`는 앱이 가로채는 웹 주소의 도메인입니다. 다만 그 뒤에 어떤 경로를 붙여야 하는지는 나오지 않으므로, 실제로는 공유 링크로 찾는 방법이 가장 확실합니다.

---

## 📝 **핵심 개념 정리**

버튼을 차례로 누르는 대신 주소로 바로 열면 단계가 줄고 실패할 곳이 사라집니다. `am start -a android.intent.action.VIEW -d 주소 패키지명`은 인텐트를 보내 앱 속 화면을 엽니다.

주소에 `&`가 있으면 폰 셸이 명령을 끊으므로 `"'주소'"`처럼 따옴표를 두 번 감쌉니다.

숨은 주소는 공유 링크 복사가 가장 쉽습니다. 안드로이드 10부터는 클립보드를 직접 읽을 수 없으므로 크롬 주소창에 붙여넣어 `uiautomator dump`로 읽습니다. 웹 디버깅과 logcat은 앱이 허용할 때만 쓸 수 있습니다. 찾은 주소에서 추적용 값은 빼고 테스트합니다.

---

## 💡 **실습 과제**

### **과제 1: 주소 모음 매크로**

자주 보는 페이지 3곳(예: 날씨, 뉴스, 쇼핑 장바구니)의 주소를 찾아, 5초 간격으로 차례로 열고 각각 캡처하는 매크로를 만드세요.

```
조건:
- 주소와 패키지명은 리스트로 관리
- 각 페이지는 열기 전에 해당 앱을 force-stop
- 캡처 파일 이름에 순번 넣기
```

### **과제 2: 링크 정리기**

`clipboard_url.py`를 고쳐서 읽어 온 주소에서 `utm_`으로 시작하는 값과 `d=` 값을 자동으로 제거하고 출력하세요.

```python
# 힌트
from urllib.parse import urlsplit, parse_qsl, urlencode, urlunsplit

parts = urlsplit(url)
query = [(k, v) for k, v in parse_qsl(parts.query) if not k.startswith("utm_") and k != "d"]
clean = urlunsplit(parts._replace(query=urlencode(query)))
```

---

## ✅ **퀴즈**

### **[초급] 1번**

`am start`에서 `-d` 옵션에 들어가는 것은?

1. 앱의 버전
2. 열 주소(데이터)
3. 기기 시리얼 번호
4. 대기 시간

### **[초급] 2번**

다음 중 앱 전용 주소(커스텀 스킴)의 형태는?

1. `https://www.youtube.com`
2. `youtube://`
3. `www.youtube.com`
4. `youtube.com/watch`

### **[중급] 3번**

다음 명령을 실행했더니 `locale=ko-KR`까지만 열렸다. 원인은?

```bash
adb shell am start -a android.intent.action.VIEW -d "https://a.com/p?locale=ko-KR&x=1"
```

1. 주소가 너무 길어서
2. 폰의 셸이 `&`를 명령 구분자로 해석해서
3. 패키지명을 쓰지 않아서
4. `-a` 값이 틀려서

### **[중급] 4번**

안드로이드 10 이상에서 폰 클립보드의 주소를 adb로 알아내는 방법으로 옳은 것은?

1. `adb shell clipboard get`
2. `adb pull /sdcard/clipboard.txt`
3. 크롬 주소창에 붙여넣은 뒤 화면 구조를 읽는다
4. 불가능하다

### **[고급] 5번**

`adb shell cat /proc/net/unix | grep devtools`의 결과에 `webview_devtools_remote_31270`만 있고, `adb shell pidof ctrip.english`의 결과가 `16789`일 때 옳은 해석은?

1. 트립닷컴의 웹뷰를 chrome://inspect로 볼 수 있다
2. 트립닷컴은 웹뷰 디버깅이 허용되어 있지 않다
3. 트립닷컴이 실행 중이 아니다
4. 폰을 재부팅해야 한다

---

## 🔑 **퀴즈 정답 및 해설**

**1번 정답: 2**
`-d`는 data의 약자로, 열고 싶은 주소가 들어갑니다. `-a`는 동작(action)입니다.

**2번 정답: 2**
`이름://` 형태가 앱 전용 주소입니다. `https://`로 시작하는 주소는 웹 주소이며, 앱이 가로채도록 설정되어 있으면 앱에서 열립니다.

**3번 정답: 2**
PC 터미널이 큰따옴표를 벗긴 뒤 폰의 셸이 `&`에서 명령을 끊습니다. `"'주소'"`처럼 작은따옴표로 한 번 더 감싸야 합니다.

**4번 정답: 3**
안드로이드 10부터 백그라운드에서 클립보드를 읽는 것이 막혀 있습니다. 화면에 보이는 입력창에 붙여넣은 뒤 그 글자를 읽는 방식으로 우회합니다.

**5번 정답: 2**
웹뷰 디버깅 소켓 이름 끝의 번호는 프로세스 번호입니다. 트립닷컴(16789)의 소켓이 없으므로 디버깅이 허용되지 않은 것입니다. 31270은 다른 앱의 소켓입니다.

---

## 🎯 **다음 장 예고**

다음 장에서는 글자도 주소도 없는 화면을 공략합니다. OpenCV로 스크린샷 속에서 버튼 그림을 찾아 누르는 이미지 매칭을 배우고, 자동으로 넘어가는 배너처럼 까다로운 화면을 다루는 방법을 익힙니다!

---

이 수업자료는 Claude를 이용하여 제작되었습니다.
