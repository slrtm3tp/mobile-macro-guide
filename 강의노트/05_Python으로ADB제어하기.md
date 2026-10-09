# 5장 Python으로 ADB 제어하기

---

## 📚 **학습 목표 (Learning Objectives)**

이번 장을 마치면 여러분은 Python의 `subprocess`로 adb 명령을 실행하고 결과를 받아 올 수 있습니다. 또한 오류와 시간 초과를 처리하고, 화면 구조 XML을 Python으로 분석하여 `tap_text("이벤트")`처럼 글자로 버튼을 찾아 누르는 함수를 직접 만들 수 있게 됩니다. 이 장에서 만든 함수들은 `예제코드/adb_helper.py`로 정리되어 이후 모든 장에서 사용합니다.

---

## 1️⃣ **왜 Python인가?**

2장의 셸 스크립트는 명령을 순서대로 실행만 할 수 있습니다. 매크로가 똑똑해지려면 **판단**이 필요합니다.

```
셸 스크립트                         Python

 tap 440 440                       버튼이 있나 확인
 sleep 3                             ├── 있으면 → 가운데 계산 → tap
 tap 720 1200                        └── 없으면 → 2초 더 기다림 → 다시 확인
                                                   └── 10초 지나도 없으면 → 캡처 남기고 중단
```

Python은 조건문, 반복문, 예외 처리, XML 분석을 쉽게 할 수 있어서 매크로에 아주 잘 맞습니다.

---

## 2️⃣ **subprocess로 명령 실행하기**

```python
# 기본 구조
import subprocess

result = subprocess.run(["명령", "인자1", "인자2"], capture_output=True)
```

| 결과 속성 | 의미 |
| --- | --- |
| `result.returncode` | 0이면 성공, 그 외는 실패 |
| `result.stdout` | 명령의 정상 출력 (bytes) |
| `result.stderr` | 오류 메시지 (bytes) |

```python
import subprocess

result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
print("성공 여부:", result.returncode)
print(result.stdout)
```

```
성공 여부: 0
List of devices attached
R5CT1234ABC	device
```

`text=True`를 주면 결과가 bytes 대신 문자열(str)로 나옵니다. 단, 화면 캡처처럼 이미지 데이터를 받을 때는 `text=True`를 빼야 합니다.

### **명령은 리스트로 나누어 전달**

```python
# 좋은 방법: 리스트
subprocess.run(["adb", "shell", "input", "tap", "540", "1200"])

# 피할 방법: 문자열 + shell=True (특수문자에서 사고가 나기 쉬움)
subprocess.run("adb shell input tap 540 1200", shell=True)
```

---

## 3️⃣ **adb() 함수 만들기**

매번 `subprocess.run(["adb", ...])`을 쓰기 번거로우므로 함수로 만듭니다.

```python
import subprocess

def adb(*args):
    """adb 명령을 실행하고 출력(bytes)을 돌려준다."""
    cmd = ["adb"] + [str(a) for a in args]
    result = subprocess.run(cmd, capture_output=True)
    return result.stdout

# 사용
adb("shell", "input", "tap", 540, 1200)
print(adb("shell", "wm", "size").decode())
```

```
Physical size: 1440x3120
```

`*args`는 "인자를 몇 개든 받아서 튜플로 묶는다"는 뜻입니다. `str(a)`로 숫자도 문자열로 바꿔 줍니다.

### **예제 1: 오류와 시간 초과 처리하기**

폰이 끊기거나 명령이 멈추면 매크로 전체가 멈춥니다. 오류를 알아차릴 수 있게 개선합니다.

```python
import subprocess

class AdbError(Exception):
    """adb 명령이 실패했을 때 발생하는 예외."""

def adb(*args, timeout=30):
    cmd = ["adb"] + [str(a) for a in args]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AdbError(f"시간 초과: {' '.join(cmd)}")
    if result.returncode != 0:
        raise AdbError(result.stderr.decode(errors="ignore").strip())
    return result.stdout

# 폰을 뽑은 상태에서 실행해 보기
try:
    adb("shell", "input", "tap", 540, 1200)
except AdbError as e:
    print("실패:", e)
```

```
실패: adb: no devices/emulators found
```

---

## 4️⃣ **자주 쓰는 동작을 함수로**

```python
def shell(command):
    """폰 안에서 셸 명령을 실행하고 문자열로 돌려준다."""
    return adb("shell", command).decode(errors="ignore").strip()

def tap(x, y):
    shell(f"input tap {int(x)} {int(y)}")

def swipe(x1, y1, x2, y2, ms=300):
    shell(f"input swipe {x1} {y1} {x2} {y2} {ms}")

def key(code):
    shell(f"input keyevent {code}")

def launch(package):
    shell(f"monkey -p {package} -c android.intent.category.LAUNCHER 1")

def stop(package):
    shell(f"am force-stop {package}")

def screenshot(path="screen.png"):
    with open(path, "wb") as f:
        f.write(adb("exec-out", "screencap", "-p"))
```

### **예제 2: 연결 확인 + 기기 정보 출력**

```python
import subprocess

def devices():
    out = subprocess.run(["adb", "devices"], capture_output=True, text=True).stdout
    rows = [line.split("\t") for line in out.strip().splitlines()[1:] if "\t" in line]
    return rows

found = devices()
if not found:
    print("❌ 연결된 기기가 없습니다")
else:
    for serial, state in found:
        icon = "✅" if state == "device" else "⚠️"
        print(f"{icon} {serial}: {state}")
    print("모델:", shell("getprop ro.product.model"))
    print("해상도:", shell("wm size"))
```

```
✅ R5CT1234ABC: device
모델: SM-S948N
해상도: Physical size: 1440x3120
```

---

## 5️⃣ **XML 분석하기: ElementTree**

4장에서 본 `uiautomator dump` 결과를 Python으로 읽어 봅니다.

```python
import xml.etree.ElementTree as ET

def dump_ui():
    shell("uiautomator dump /sdcard/ui.xml")
    xml_bytes = adb("exec-out", "cat", "/sdcard/ui.xml")
    return ET.fromstring(xml_bytes)

root = dump_ui()
for node in root.iter("node"):          # 모든 <node>를 하나씩
    t = node.get("text")                # 속성 읽기
    if t:
        print(t, node.get("bounds"))
```

```
프로모션 [46,0][323,172]
이벤트 [320,400][560,480]
여행계획 [580,400][800,480]
도쿄 여행을 준비하세요 [60,610][900,680]
...
```

| ElementTree 기능 | 의미 |
| --- | --- |
| `ET.fromstring(xml)` | XML 문자열을 분석해 루트 요소를 만듦 |
| `root.iter("node")` | 모든 하위 `<node>`를 차례로 꺼냄 |
| `node.get("text", "")` | 속성 값 읽기, 없으면 `""` |

### **bounds 가운데 계산 함수**

```python
import re

def center(node):
    x1, y1, x2, y2 = map(int, re.findall(r"\d+", node.get("bounds")))
    return (x1 + x2) // 2, (y1 + y2) // 2

print(center(node))   # bounds="[320,400][560,480]" → (440, 440)
```

`re.findall(r"\d+", ...)`은 문자열에서 숫자 덩어리만 모두 뽑아 줍니다. `"[320,400][560,480]"` → `['320', '400', '560', '480']`.

---

## 6️⃣ **글자로 찾아 누르기: find, wait_for, tap_text**

### **find: 조건에 맞는 요소 찾기**

```python
def find(text=None, desc=None, rid=None):
    root = dump_ui()
    for node in root.iter("node"):
        if text and text not in node.get("text", ""):
            continue
        if desc and desc not in node.get("content-desc", ""):
            continue
        if rid and rid not in node.get("resource-id", ""):
            continue
        return node          # 조건을 모두 만족하는 첫 요소
    return None              # 못 찾음
```

### **wait_for: 나타날 때까지 기다리기**

앱이 화면을 그리는 데는 시간이 걸립니다. 정해진 시간만큼 반복해서 찾아봅니다.

```python
import time

def wait_for(text=None, desc=None, rid=None, timeout=10):
    deadline = time.time() + timeout
    while time.time() < deadline:
        node = find(text=text, desc=desc, rid=rid)
        if node is not None:
            return node
        time.sleep(0.5)
    return None
```

```
wait_for 동작 흐름

  시작 ──► dump & 찾기 ──► 찾았다? ──Yes──► 요소 반환
               ▲               │
               │              No
               │               ▼
           0.5초 대기 ◄── 시간 남았다? ──No──► None 반환
                     Yes
```

### **tap_text: 찾아서 누르기**

```python
def tap_text(text, timeout=10):
    node = wait_for(text=text, timeout=timeout) or wait_for(desc=text, timeout=1)
    if node is None:
        raise AdbError(f"화면에서 '{text}'를 찾지 못했습니다")
    tap(*center(node))
```

`tap(*center(node))`의 `*`는 `(440, 440)` 튜플을 풀어서 `tap(440, 440)`으로 전달합니다.

### **예제 3: 설정 앱에서 "디스플레이" 메뉴 들어가기**

```python
from adb_helper import *

check_device()
stop("com.android.settings")
launch("com.android.settings")

tap_text("디스플레이")          # 화면에 나타날 때까지 기다렸다가 탭
if wait_for(text="다크 모드", timeout=5):
    print("✅ 디스플레이 메뉴에 들어왔습니다")
    screenshot("display.png")
else:
    print("❌ 디스플레이 화면이 아닙니다")
    screenshot("error.png")
```

```
✅ 디스플레이 메뉴에 들어왔습니다
```

메뉴가 화면 아래쪽에 있어도 요소는 XML에 잡히는 경우가 많지만, 화면 밖에 있는 요소는 잡히지 않을 수 있습니다. 그럴 때는 스크롤한 뒤 다시 찾습니다.

### **예제 4: 찾을 때까지 스크롤하기**

```python
def scroll_to_text(text, max_scrolls=8):
    for i in range(max_scrolls):
        node = find(text=text)
        if node is not None:
            return node
        swipe(720, 2400, 720, 1200, 400)   # 한 화면의 절반쯤 아래로
        time.sleep(0.8)
    return None

node = scroll_to_text("휴대전화 정보")
if node is not None:
    tap(*center(node))
```

---

## 7️⃣ **adb_helper.py 모듈로 정리하기**

지금까지 만든 함수를 파일 하나에 모아 두면, 다른 매크로에서 `import`로 바로 쓸 수 있습니다. 완성본은 [`예제코드/adb_helper.py`](../예제코드/adb_helper.py)에 있습니다.

| 함수 | 하는 일 |
| --- | --- |
| `check_device()` | 기기 연결 확인, 문제가 있으면 이유 출력 후 종료 |
| `tap(x, y)` / `swipe(...)` / `long_press(x, y)` | 입력 |
| `key("KEYCODE_BACK")` / `text("hello")` | 키, 영문 입력 |
| `launch(pkg)` / `stop(pkg)` / `open_url(url, pkg)` | 앱 실행·종료·주소 열기 |
| `current_app()` | 지금 화면의 (패키지명, 액티비티) |
| `screenshot(path)` / `screen_size()` | 캡처, 해상도 |
| `dump_ui()` / `find(...)` / `center(node)` | 화면 구조 분석 |
| `wait_for(...)` / `tap_text(text)` | 기다렸다가 찾기, 찾아서 누르기 |
| `scroll_to_text(text)` | 보일 때까지 스크롤하며 찾기 |

```bash
cd 예제코드
python3 adb_helper.py
```

```
기기: [('R5CT1234ABC', 'device')]
해상도: (1440, 3120)
현재 앱: ('ctrip.english', 'com.ctrip.ibu.hybrid.v2.container.TripH5Container')
```

---

## 📝 **핵심 개념 정리**

`subprocess.run(["adb", ...], capture_output=True)`으로 adb 명령을 실행하고 `returncode`, `stdout`, `stderr`로 결과를 확인합니다. 명령은 리스트로 나누어 전달하고, `timeout`과 예외 처리로 멈춤과 오류에 대비합니다.

`xml.etree.ElementTree`로 `uiautomator dump` 결과를 분석합니다. `root.iter("node")`로 모든 요소를 돌며 `text`, `content-desc`, `resource-id`를 비교하고, `bounds`에서 가운데 좌표를 계산합니다.

`wait_for`는 요소가 나타날 때까지 반복해서 찾고, `tap_text`는 찾아서 가운데를 누릅니다. 고정된 `sleep`보다 "나타날 때까지 기다리기"가 빠르고 안정적입니다. 이 함수들을 `adb_helper.py`에 모아 두고 이후 장에서 재사용합니다.

---

## 💡 **실습 과제**

### **과제 1: 화면 글자 사전 만들기**

현재 화면의 모든 `text`와 `content-desc`를 가운데 좌표와 함께 표로 출력하는 프로그램을 작성하세요.

```
출력 예:
번호  글자                 좌표
1     프로모션              (184, 86)
2     이벤트                (440, 440)
...
```

### **과제 2: 설정에서 휴대전화 정보 읽기**

설정 앱을 열고 "휴대전화 정보"를 찾아 들어간 뒤, 화면에서 "모델명" 아래에 있는 글자를 읽어 출력하세요.

```python
# 힌트
from adb_helper import *

launch("com.android.settings")
node = scroll_to_text("휴대전화 정보")     # 예제 4의 함수 (adb_helper에도 있음)
tap(*center(node))
wait_for(text="모델", timeout=5)
root = dump_ui()
texts = [n.get("text") for n in root.iter("node") if n.get("text")]
i = next(i for i, t in enumerate(texts) if "모델" in t)
print("모델명:", texts[i + 1])
```

---

## ✅ **퀴즈**

### **[초급] 1번**

`subprocess.run`의 결과에서 명령이 성공했음을 나타내는 값은?

1. `result.returncode == 0`
2. `result.returncode == 1`
3. `result.stdout == ""`
4. `result.stderr == "OK"`

### **[초급] 2번**

다음 코드의 출력은?

```python
import re
print(re.findall(r"\d+", "[10,20][30,40]"))
```

1. `['10,20', '30,40']`
2. `['10', '20', '30', '40']`
3. `[10, 20, 30, 40]`
4. `['[10,20]', '[30,40]']`

### **[중급] 3번**

화면 캡처를 받을 때 `subprocess.run`에서 빼야 하는 옵션은?

1. `capture_output=True`
2. `timeout=30`
3. `text=True`
4. 리스트 형태의 명령

### **[중급] 4번**

`wait_for(text="완료", timeout=10)`가 `None`을 돌려주는 경우는?

1. 0.5초 만에 "완료"를 찾았을 때
2. 10초 동안 반복해서 찾았지만 "완료"가 없었을 때
3. "완료"가 두 개 있을 때
4. "완료 버튼"이라는 글자가 있을 때

### **[고급] 5번**

다음 코드에서 `tap(*center(node))`가 하는 일은?

```python
node = find(text="이벤트")   # bounds="[300,100][500,200]"
tap(*center(node))
```

1. `tap((400, 150))`을 호출하여 오류가 난다
2. `tap(400, 150)`을 호출한다
3. `tap(300, 100)`을 호출한다
4. `tap(500, 200)`을 호출한다

---

## 🔑 **퀴즈 정답 및 해설**

**1번 정답: 1**
프로그램은 성공하면 종료 코드 0을 돌려줍니다. 0이 아니면 실패이며, 이유는 `stderr`에 담깁니다.

**2번 정답: 2**
`\d+`는 "숫자가 하나 이상 연속된 부분"입니다. 결과는 문자열 리스트이므로 계산하려면 `int`로 바꿔야 합니다.

**3번 정답: 3**
화면 캡처는 PNG 이미지(바이너리)입니다. `text=True`를 주면 글자로 바꾸려다 데이터가 깨지거나 오류가 납니다.

**4번 정답: 2**
`wait_for`는 시간 안에 찾으면 요소를, 끝까지 못 찾으면 `None`을 돌려줍니다. "완료 버튼"은 "완료"를 포함하므로 찾은 것으로 봅니다.

**5번 정답: 2**
`center(node)`는 `((300+500)//2, (100+200)//2)` = `(400, 150)`을 돌려주고, `*`가 튜플을 풀어서 `tap(400, 150)`으로 전달합니다.

---

## 🎯 **다음 장 예고**

다음 장에서는 이 함수들을 조립해 진짜 매크로 스크립트를 설계합니다. 동작 목록(STEPS)으로 매크로를 표현하는 방법, 실패했을 때 재시도와 기록 남기기, 반복 실행까지 배우며 `macro.py`를 처음부터 완성해 봅니다!

---

이 수업자료는 Claude를 이용하여 제작되었습니다.
