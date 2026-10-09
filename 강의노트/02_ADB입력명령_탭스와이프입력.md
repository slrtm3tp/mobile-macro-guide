# 2장 ADB 입력 명령: 탭, 스와이프, 입력, 키

---

## 📚 **학습 목표 (Learning Objectives)**

이번 장을 마치면 여러분은 손가락으로 하던 모든 동작을 ADB 명령으로 바꿀 수 있습니다. 탭, 길게 누르기, 스와이프, 스크롤, 글자 입력, 하드웨어 키 입력을 직접 실행하고, 이 명령들을 이어 붙여 간단한 매크로를 터미널에서 만들어 봅니다.

---

## 1️⃣ **좌표 체계 이해하기**

화면의 모든 위치는 **(x, y) 좌표**로 표현합니다. 왼쪽 위 모서리가 (0, 0)이고, 오른쪽으로 갈수록 x가, 아래로 갈수록 y가 커집니다.

```
화면 좌표 (1440 x 3120 폰, 세로 화면)

 (0,0) ─────────────────────► x (최대 1439)
   │  ┌──────────────────────┐
   │  │ 상태바                │  y ≈ 0 ~ 140
   │  ├──────────────────────┤
   │  │                      │
   │  │      (720, 1560)     │  ← 화면 정중앙
   │  │          ●           │
   │  │                      │
   │  ├──────────────────────┤
   │  │ ◁    ○    ▢  내비바   │  y ≈ 2980 ~ 3120
   ▼  └──────────────────────┘
   y (최대 3119)
```

좌표는 **픽셀 단위**이므로 해상도가 다른 폰에서는 같은 버튼이라도 좌표가 다릅니다. 해상도는 `adb shell wm size`로 확인합니다.

> ⚠️ 가로 화면(영상 전체 화면 등)에서는 가로·세로가 바뀝니다. 1440x3120 폰을 가로로 돌리면 x는 0~3119, y는 0~1439가 됩니다.

---

## 2️⃣ **탭 (tap)**

```bash
# 기본 구조
adb shell input tap <x> <y>
```

```bash
# 화면 정중앙 터치 (1440x3120 기준)
adb shell input tap 720 1560
```

명령을 입력하면 해당 위치를 손가락으로 한 번 짧게 터치한 것과 똑같이 동작합니다.

### **예제 1: 계산기로 2 + 3 계산하기**

계산기 앱을 열고 버튼 좌표를 차례로 터치합니다. (좌표는 폰마다 다르므로 4장에서 배우는 방법으로 직접 확인하세요.)

```bash
# 계산기 실행 (삼성 계산기 패키지명)
adb shell monkey -p com.sec.android.app.popupcalculator -c android.intent.category.LAUNCHER 1
sleep 2

adb shell input tap 720 2350    # 2
sleep 0.5
adb shell input tap 1260 2620   # +
sleep 0.5
adb shell input tap 1080 2350   # 3
sleep 0.5
adb shell input tap 1260 2890   # =
```

`sleep`은 터미널에서 지정한 초만큼 기다리는 명령입니다. 앱이 반응할 시간을 주지 않으면 다음 터치가 씹힐 수 있습니다.

---

## 3️⃣ **스와이프 (swipe)와 길게 누르기**

```bash
# 기본 구조
adb shell input swipe <시작x> <시작y> <끝x> <끝y> [시간ms]
```

시작 위치에서 끝 위치까지 손가락을 끌어가는 동작입니다. 마지막 숫자는 끌어가는 데 걸리는 시간(밀리초)이며, 생략하면 약 300ms입니다.

```
스와이프 방향과 화면 움직임

  손가락 ↑ (아래 → 위)   = 화면 내용이 위로 = 아래쪽 내용 보기 (스크롤 다운)
  손가락 ↓ (위 → 아래)   = 화면 내용이 아래로 = 위쪽 내용 보기 / 새로고침
  손가락 ← (오른쪽 → 왼쪽) = 다음 페이지 / 다음 배너
  손가락 → (왼쪽 → 오른쪽) = 이전 페이지
```

```bash
# 아래 내용 보기 (손가락을 아래에서 위로)
adb shell input swipe 720 2400 720 900 300

# 새로고침 (손가락을 위에서 아래로)
adb shell input swipe 720 700 720 2000 300

# 다음 배너 (오른쪽에서 왼쪽으로)
adb shell input swipe 1200 1300 200 1300 250
```

### **길게 누르기 (long press)**

시작과 끝 좌표를 같게 하고 시간을 길게 주면 길게 누르기가 됩니다.

```bash
# (720, 1560)을 1초 동안 누르기
adb shell input swipe 720 1560 720 1560 1000
```

### **빠른 스와이프 vs 느린 스와이프**

시간 값에 따라 결과가 달라집니다.

| 시간(ms) | 결과 | 용도 |
| --- | --- | --- |
| 50 ~ 150 | 휙 던지기 (fling), 관성으로 멀리 스크롤 | 긴 목록 빠르게 넘기기 |
| 250 ~ 500 | 일반 스와이프 | 배너 넘기기, 한 화면 스크롤 |
| 800 이상 | 천천히 끌기, 관성 거의 없음 | 정확한 위치까지 스크롤, 드래그 |

### **예제 2: 목록 끝까지 스크롤하기**

```bash
# 5번 반복해서 아래로 스크롤
for i in 1 2 3 4 5; do
  adb shell input swipe 720 2400 720 900 300
  sleep 1
done
```

Mac/Linux의 `for` 반복문입니다. Windows에서는 5장의 Python 방식을 사용하세요.

---

## 4️⃣ **글자 입력 (text)**

```bash
# 기본 구조
adb shell input text <문자열>
```

**입력창이 선택된(커서가 깜빡이는) 상태**에서 실행해야 합니다. 먼저 입력창을 탭한 뒤 입력합니다.

```bash
adb shell input tap 720 300        # 검색창 터치
sleep 1
adb shell input text "osaka"       # 글자 입력
adb shell input keyevent KEYCODE_ENTER   # 검색 실행
```

### **띄어쓰기와 특수문자**

`input text`는 띄어쓰기를 그대로 받지 못합니다. **공백은 `%s`**로 바꿉니다.

```bash
adb shell input text "hello%sworld"    # hello world
```

`&`, `(`, `)`, `;`, `<`, `>`, `|`, `*`, `'`, `"` 같은 문자는 폰의 셸이 특별하게 해석합니다. 앞에 `\`를 붙이거나 작은따옴표로 한 번 더 감싸야 합니다.

```bash
adb shell input text "'a&b'"           # a&b
```

### **한글은 안 됩니다**

`input text`는 영문, 숫자, 일부 기호만 입력할 수 있습니다. 한글 입력은 9장(ADBKeyboard)과 10장(uiautomator2)에서 해결합니다.

---

## 5️⃣ **키 입력 (keyevent)**

```bash
# 기본 구조
adb shell input keyevent <키 이름 또는 번호>
```

물리 버튼이나 시스템 버튼을 누르는 명령입니다.

| 키 이름 | 번호 | 동작 |
| --- | --- | --- |
| `KEYCODE_HOME` | 3 | 홈 화면 |
| `KEYCODE_BACK` | 4 | 뒤로 가기 |
| `KEYCODE_APP_SWITCH` | 187 | 최근 앱 목록 |
| `KEYCODE_ENTER` | 66 | 엔터 (검색, 확인) |
| `KEYCODE_DEL` | 67 | 백스페이스 (한 글자 지우기) |
| `KEYCODE_TAB` | 61 | 다음 입력칸으로 |
| `KEYCODE_PASTE` | 279 | 붙여넣기 |
| `KEYCODE_COPY` | 278 | 복사 |
| `KEYCODE_MOVE_END` | 123 | 커서를 끝으로 |
| `KEYCODE_VOLUME_UP` | 24 | 볼륨 올리기 |
| `KEYCODE_VOLUME_DOWN` | 25 | 볼륨 내리기 |
| `KEYCODE_POWER` | 26 | 전원 버튼 (화면 켜기/끄기) |
| `KEYCODE_WAKEUP` | 224 | 화면 켜기 (이미 켜져 있으면 무시) |

```bash
adb shell input keyevent KEYCODE_HOME   # 이름으로
adb shell input keyevent 3              # 번호로 (같은 동작)
```

### **여러 키를 한 번에**

키 이름을 띄어 쓰면 차례로 누릅니다.

```bash
# 백스페이스 10번 (입력창 비우기)
adb shell input keyevent 67 67 67 67 67 67 67 67 67 67
```

### **예제 3: 화면 깨우고 홈으로 가기**

매크로를 시작하기 전에 폰 상태를 일정하게 맞추는 준비 동작입니다.

```bash
adb shell input keyevent KEYCODE_WAKEUP     # 화면 켜기
sleep 1
adb shell input swipe 720 2600 720 1000 300 # 잠금 화면 밀어서 풀기 (패턴·비밀번호 없을 때)
sleep 1
adb shell input keyevent KEYCODE_HOME       # 홈 화면으로
```

> ⚠️ 비밀번호나 패턴이 걸린 폰은 매크로로 풀지 않는 것이 좋습니다. 비밀번호를 스크립트에 적으면 유출 위험이 있습니다. 매크로를 쓰는 동안에는 `개발자 옵션 → 화면 켜짐 상태 유지(충전 중)`를 켜 두세요.

---

## 6️⃣ **명령을 이어 붙여 첫 매크로 만들기**

지금까지 배운 명령을 순서대로 실행하면 그것이 곧 매크로입니다. 명령을 파일에 저장하면 언제든 다시 실행할 수 있습니다.

### **예제 4: 크롬에서 검색하기 (셸 스크립트)**

`search.sh` 파일을 만들고 아래 내용을 저장합니다.

```bash
#!/bin/bash
# 크롬을 열고 'adb macro'를 검색하는 매크로

echo "1. 크롬 실행"
adb shell monkey -p com.android.chrome -c android.intent.category.LAUNCHER 1
sleep 3

echo "2. 주소창 터치"
adb shell input tap 720 250
sleep 1

echo "3. 검색어 입력"
adb shell input text "adb%smacro"
sleep 0.5

echo "4. 검색 실행"
adb shell input keyevent KEYCODE_ENTER
sleep 3

echo "5. 결과 스크롤"
adb shell input swipe 720 2400 720 900 300

echo "완료!"
```

```bash
chmod +x search.sh    # 실행 권한 주기 (처음 한 번)
./search.sh           # 실행
```

```
1. 크롬 실행
2. 주소창 터치
3. 검색어 입력
4. 검색 실행
5. 결과 스크롤
완료!
```

주소창 좌표(720, 250)는 폰마다 다릅니다. 4장에서 정확한 좌표를 찾는 방법을 배웁니다.

---

## 📝 **핵심 개념 정리**

화면 위치는 왼쪽 위가 (0, 0)인 픽셀 좌표로 표현하며, 해상도와 화면 방향에 따라 달라집니다.

`input tap x y`는 한 번 터치, `input swipe x1 y1 x2 y2 ms`는 끌기입니다. 시작과 끝 좌표를 같게 하고 시간을 길게 주면 길게 누르기가 됩니다. 스와이프 시간이 짧을수록 관성이 커집니다.

`input text`는 영문·숫자만 입력할 수 있고 공백은 `%s`로 씁니다. `input keyevent`로 홈, 뒤로, 엔터, 붙여넣기 같은 시스템 키를 누릅니다.

명령 사이에는 `sleep`으로 앱이 반응할 시간을 주어야 하며, 여러 명령을 파일로 저장하면 그대로 매크로가 됩니다.

---

## 💡 **실습 과제**

### **과제 1: 설정 앱 탐험 매크로**

설정 앱을 열고, 화면을 끝까지 스크롤한 뒤, 다시 맨 위로 돌아오고, 홈으로 나가는 셸 스크립트를 작성하세요.

```
조건:
- 설정 앱 패키지명: com.android.settings
- 아래로 3번 스크롤, 각 스크롤 사이 1초 대기
- 위로 빠르게(100ms) 3번 스크롤
- 마지막에 홈 키
```

### **과제 2: 메모 앱에 영어 문장 쓰기**

메모 앱(예: Samsung Notes)을 열고 새 메모 버튼을 눌러 아래 문장을 입력하세요.

```
Hello ADB!
Today I learned input text.
```

```bash
# 힌트
adb shell input text "Hello%sADB!"
adb shell input keyevent KEYCODE_ENTER   # 줄바꿈
```

---

## ✅ **퀴즈**

### **[초급] 1번**

화면의 (500, 1000) 위치를 한 번 터치하는 명령은?

1. `adb shell input click 500 1000`
2. `adb shell input tap 500 1000`
3. `adb shell tap 500 1000`
4. `adb input tap 500 1000`

### **[초급] 2번**

뒤로 가기 버튼을 누르는 명령은?

1. `adb shell input keyevent KEYCODE_HOME`
2. `adb shell input keyevent KEYCODE_BACK`
3. `adb shell input back`
4. `adb shell input keyevent 3`

### **[중급] 3번**

다음 명령의 동작으로 옳은 것은?

```bash
adb shell input swipe 600 1500 600 1500 2000
```

1. 위로 스크롤
2. 아래로 스크롤
3. (600, 1500)을 2초 동안 길게 누름
4. 아무 일도 일어나지 않음

### **[중급] 4번**

`hello world`를 입력하는 올바른 명령은?

1. `adb shell input text "hello world"`
2. `adb shell input text "hello%sworld"`
3. `adb shell input text "hello_world"`
4. `adb shell input text hello world`

### **[고급] 5번**

긴 상품 목록을 화면 몇 개 분량씩 빠르게 넘기고 싶다. 가장 알맞은 명령은?

1. `adb shell input swipe 720 2400 720 900 80`
2. `adb shell input swipe 720 900 720 2400 80`
3. `adb shell input swipe 720 2400 720 900 2000`
4. `adb shell input tap 720 2400`

---

## 🔑 **퀴즈 정답 및 해설**

**1번 정답: 2**
터치 명령은 `adb shell input tap x y`입니다. `shell`은 폰 안에서 명령을 실행하라는 뜻이고, `input`은 입력을 흉내 내는 폰의 프로그램입니다.

**2번 정답: 2**
`KEYCODE_BACK`(번호 4)이 뒤로 가기입니다. `KEYCODE_HOME`과 번호 3은 홈 버튼입니다.

**3번 정답: 3**
시작과 끝 좌표가 같으므로 손가락이 움직이지 않고, 2000ms(2초) 동안 누르고 있는 길게 누르기가 됩니다.

**4번 정답: 2**
`input text`에서 공백은 `%s`로 적어야 합니다. 4번처럼 쓰면 `hello`만 입력되거나 오류가 납니다.

**5번 정답: 1**
아래 내용을 보려면 손가락을 아래(2400)에서 위(900)로 움직입니다. 시간을 80ms로 짧게 주면 휙 던지기가 되어 관성으로 여러 화면이 넘어갑니다. 2번은 방향이 반대이고, 3번은 너무 느려서 한 화면만 움직입니다.

---

## 🎯 **다음 장 예고**

다음 장에서는 앱과 화면을 다루는 명령을 배웁니다. 설치된 앱 목록 보기, 앱 실행과 종료, 지금 떠 있는 화면 알아내기, 화면 캡처와 녹화까지 매크로의 "눈"과 "시동 버튼"을 갖추게 됩니다!

---

이 수업자료는 Claude를 이용하여 제작되었습니다.
