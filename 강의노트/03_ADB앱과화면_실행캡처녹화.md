# 3장 ADB로 앱과 화면 다루기: 실행, 종료, 캡처, 녹화

---

## 📚 **학습 목표 (Learning Objectives)**

이번 장을 마치면 여러분은 설치된 앱의 패키지명을 찾고, 앱을 실행하고 종료할 수 있습니다. 또한 지금 화면에 어떤 앱이 떠 있는지 알아내고, 화면을 캡처하거나 녹화하여 PC로 가져올 수 있게 됩니다. 이것은 매크로가 "어디서 시작할지"와 "지금 어디에 있는지"를 아는 기본기입니다.

---

## 1️⃣ **패키지명이란?**

안드로이드의 모든 앱은 **패키지명**이라는 고유한 이름을 가집니다. 화면에 보이는 앱 이름은 바뀔 수 있지만, 패키지명은 앱마다 하나뿐이고 바뀌지 않습니다.

| 앱 이름 (화면에 보이는) | 패키지명 |
| --- | --- |
| 크롬 | `com.android.chrome` |
| 유튜브 | `com.google.android.youtube` |
| 설정 | `com.android.settings` |
| 카카오톡 | `com.kakao.talk` |
| 구글 지도 | `com.google.android.apps.maps` |
| 삼성 계산기 | `com.sec.android.app.popupcalculator` |

매크로에서 앱을 실행하거나 종료할 때는 항상 패키지명을 사용합니다.

---

## 2️⃣ **앱 목록과 패키지명 찾기**

```bash
# 모든 앱 (시스템 앱 포함, 수백 개)
adb shell pm list packages

# 내가 설치한 앱만
adb shell pm list packages -3

# 이름에 특정 단어가 들어간 앱 찾기
adb shell pm list packages | grep -i youtube
```

```
package:com.google.android.youtube
package:com.google.android.apps.youtube.music
```

`pm`은 Package Manager(패키지 관리자)의 줄임말입니다.

### **지금 열려 있는 앱의 패키지명 알아내기**

이름으로 찾기 어렵다면, 앱을 화면에 띄워 놓고 아래 명령을 실행하는 것이 가장 확실합니다.

```bash
adb shell dumpsys activity activities | grep topResumedActivity
```

```
topResumedActivity=ActivityRecord{254440182 u0 com.android.chrome/org.chromium.chrome.browser.ChromeTabbedActivity t11778}
```

```
결과 읽는 법

  com.android.chrome / org.chromium.chrome.browser.ChromeTabbedActivity
  └──── 패키지명 ────┘ └──────────── 액티비티(화면) 이름 ────────────┘
```

**액티비티**는 앱 안의 화면 하나하나를 뜻합니다. 같은 앱이라도 홈 화면, 검색 화면, 웹페이지 화면은 서로 다른 액티비티일 수 있습니다.

### **예제 1: 앱 정보 알아보기**

```bash
# 앱 버전
adb shell dumpsys package com.google.android.youtube | grep versionName
#     versionName=x.y.z  (설치된 버전이 표시됨)

# 앱이 설치된 경로
adb shell pm path com.google.android.youtube
# package:/data/app/.../base.apk
```

앱이 업데이트되면 화면 구성이 바뀌어 매크로가 깨질 수 있습니다. 매크로를 만들 때 앱 버전을 기록해 두면 나중에 원인을 찾기 쉽습니다.

---

## 3️⃣ **앱 실행하기**

### **방법 A: monkey (가장 간단)**

```bash
adb shell monkey -p <패키지명> -c android.intent.category.LAUNCHER 1
```

```bash
adb shell monkey -p com.google.android.youtube -c android.intent.category.LAUNCHER 1
```

```
Events injected: 1
## Network stats: elapsed time=40ms ...
```

홈 화면에서 앱 아이콘을 누른 것과 같습니다. 액티비티 이름을 몰라도 됩니다. 원래 `monkey`는 무작위 터치로 앱을 시험하는 도구이지만, 마지막 숫자를 `1`로 주면 "앱 실행" 한 번만 하고 끝납니다.

### **방법 B: am start (화면을 지정해서 실행)**

```bash
adb shell am start -n <패키지명>/<액티비티명>
```

```bash
# 설정 앱의 Wi-Fi 화면을 바로 열기
adb shell am start -a android.settings.WIFI_SETTINGS

# 크롬 실행
adb shell am start -n com.android.chrome/com.google.android.apps.chrome.Main
```

`am`은 Activity Manager(액티비티 관리자)입니다. 웹 주소나 앱 내부 주소로 특정 화면을 여는 방법은 7장에서 자세히 배웁니다.

---

## 4️⃣ **앱 종료하기**

```bash
adb shell am force-stop <패키지명>
```

```bash
adb shell am force-stop com.google.android.youtube
```

앱을 완전히 끕니다. 최근 앱 목록에서 밀어서 지우는 것보다 확실합니다.

### **예제 2: 항상 같은 화면에서 시작하기**

매크로가 실패하는 가장 흔한 원인은 **시작 화면이 매번 달라서**입니다. 앱은 마지막에 보던 화면을 기억하기 때문에, 그냥 실행하면 홈이 아닌 다른 화면이 뜰 수 있습니다. (예: 쇼핑 앱을 열었더니 홈 대신 어제 보던 상품 페이지가 먼저 뜨는 경우)

```bash
# 1. 앱을 완전히 종료
adb shell am force-stop com.google.android.youtube
sleep 1

# 2. 다시 실행 → 항상 첫 화면(홈)부터 시작
adb shell monkey -p com.google.android.youtube -c android.intent.category.LAUNCHER 1
sleep 4

# 3. 지금 어떤 화면인지 확인
adb shell dumpsys activity activities | grep topResumedActivity
```

"종료 → 실행 → 확인"은 거의 모든 매크로의 첫 세 줄입니다.

---

## 5️⃣ **화면 캡처 (screencap)**

### **방법 A: 폰에 저장했다가 가져오기**

```bash
adb shell screencap -p /sdcard/screen.png   # 폰에 저장
adb pull /sdcard/screen.png                  # PC로 가져오기
adb shell rm /sdcard/screen.png              # 폰에서 지우기
```

### **방법 B: PC로 바로 저장 (추천)**

```bash
adb exec-out screencap -p > screen.png
```

`exec-out`은 폰의 출력을 그대로 PC로 보내 줍니다. 파일 하나로 끝나서 빠르고 간단합니다.

```
두 방법 비교

  방법 A:  폰 ──저장──► /sdcard/screen.png ──pull──► PC
  방법 B:  폰 ────────── 바로 전송 ─────────────────► PC (screen.png)
```

> ⚠️ 은행, 증권, 일부 게임 앱은 보안을 위해 캡처를 막습니다. 이런 앱은 캡처 결과가 검은 화면으로 나옵니다.

### **예제 3: 시간 이름으로 캡처 저장하기**

여러 번 캡처할 때 파일이 덮어써지지 않도록 시간을 파일 이름에 넣습니다.

```bash
adb exec-out screencap -p > "shot_$(date +%H%M%S).png"
ls shot_*
# shot_124402.png
```

---

## 6️⃣ **화면 녹화 (screenrecord)**

매크로가 어디서 실패하는지 확인할 때 녹화가 매우 유용합니다.

```bash
# 녹화 시작 (최대 180초, Ctrl+C로 중지)
adb shell screenrecord /sdcard/demo.mp4

# PC로 가져오기
adb pull /sdcard/demo.mp4
```

| 옵션 | 의미 | 예시 |
| --- | --- | --- |
| `--time-limit` | 녹화 시간(초), 최대 180 | `--time-limit 30` |
| `--size` | 해상도 | `--size 720x1560` |
| `--bit-rate` | 화질(비트레이트) | `--bit-rate 4000000` |

### **예제 4: 매크로를 실행하면서 녹화하기**

```bash
# 녹화를 백그라운드로 30초 시작
adb shell screenrecord --time-limit 30 /sdcard/macro_test.mp4 &

# 매크로 실행
./search.sh

# 녹화가 끝날 때까지 기다린 뒤 가져오기
wait
adb pull /sdcard/macro_test.mp4
```

명령 끝의 `&`는 "이 명령을 뒤에서 돌리고 바로 다음 줄로 넘어가라"는 뜻입니다. `wait`는 뒤에서 돌던 명령이 끝날 때까지 기다립니다.

---

## 7️⃣ **화면 상태 알아내기**

| 알고 싶은 것 | 명령 | 결과 예시 |
| --- | --- | --- |
| 화면이 켜져 있나? | `adb shell dumpsys power \| grep mWakefulness` | `mWakefulness=Awake` |
| 잠겨 있나? | `adb shell dumpsys window \| grep mDreamingLockscreen` | `mDreamingLockscreen=false` |
| 화면 방향 | `adb shell dumpsys input \| grep SurfaceOrientation` | `SurfaceOrientation: 0` (0=세로, 1·3=가로) |
| 배터리 | `adb shell dumpsys battery \| grep level` | `level: 71` |
| 현재 포커스 창 | `adb shell dumpsys window \| grep mCurrentFocus` | `mCurrentFocus=Window{... com.android.chrome/...}` |

### **예제 5: 화면이 꺼져 있으면 켜기**

```bash
state=$(adb shell dumpsys power | grep -o 'mWakefulness=[A-Za-z]*')
echo "현재 상태: $state"

if [ "$state" != "mWakefulness=Awake" ]; then
  echo "화면을 켭니다"
  adb shell input keyevent KEYCODE_WAKEUP
fi
```

```
현재 상태: mWakefulness=Asleep
화면을 켭니다
```

---

## 📝 **핵심 개념 정리**

안드로이드 앱은 고유한 패키지명을 가지며, `pm list packages`로 목록을 보고 `dumpsys activity activities | grep topResumedActivity`로 지금 떠 있는 앱과 화면(액티비티)을 알 수 있습니다.

앱 실행은 `monkey -p 패키지명 -c android.intent.category.LAUNCHER 1`, 종료는 `am force-stop 패키지명`입니다. 매크로는 "종료 → 실행 → 확인"으로 시작해야 매번 같은 화면에서 출발합니다.

화면 캡처는 `adb exec-out screencap -p > 파일.png`로 PC에 바로 저장하고, 녹화는 `screenrecord`로 최대 180초까지 할 수 있습니다. `dumpsys`로 화면 켜짐, 방향, 배터리 같은 상태도 확인할 수 있습니다.

---

## 💡 **실습 과제**

### **과제 1: 앱 3개 순서대로 열고 캡처하기**

내가 자주 쓰는 앱 3개를 골라 패키지명을 찾고, 하나씩 실행해서 3초 뒤 캡처하는 셸 스크립트를 작성하세요.

```
조건:
- 각 앱은 force-stop 후 실행
- 캡처 파일 이름: app1.png, app2.png, app3.png
- 마지막에 홈 키
```

### **과제 2: 현재 화면 감시기**

1초마다 현재 앱의 패키지명을 출력하는 스크립트를 작성하고, 폰에서 앱을 이리저리 바꿔 보세요.

```bash
# 힌트
while true; do
  adb shell dumpsys activity activities | grep topResumedActivity | grep -oE 'u0 [^/]+' 
  sleep 1
done
```

---

## ✅ **퀴즈**

### **[초급] 1번**

내가 설치한 앱(시스템 앱 제외)의 목록만 보는 명령은?

1. `adb shell pm list packages`
2. `adb shell pm list packages -3`
3. `adb shell pm list apps`
4. `adb list packages`

### **[초급] 2번**

PC에 `screen.png`로 화면을 바로 저장하는 명령은?

1. `adb shell screencap screen.png`
2. `adb exec-out screencap -p > screen.png`
3. `adb screenshot screen.png`
4. `adb pull screencap`

### **[중급] 3번**

다음 결과에서 패키지명은?

```
topResumedActivity=ActivityRecord{1234 u0 com.kakao.talk/.activity.main.MainActivity t52}
```

1. `com.kakao.talk`
2. `.activity.main.MainActivity`
3. `u0`
4. `MainActivity`

### **[중급] 4번**

앱을 실행했는데 홈이 아니라 전에 보던 이벤트 페이지가 떴다. 매번 홈에서 시작하려면?

1. 앱을 두 번 실행한다
2. 실행 전에 `am force-stop`으로 앱을 완전히 종료한다
3. 폰을 재부팅한다
4. `input keyevent KEYCODE_HOME`을 누른다

### **[고급] 5번**

`adb shell screenrecord`에 대한 설명으로 틀린 것은?

1. 기본적으로 최대 180초까지 녹화된다
2. `--time-limit`으로 녹화 시간을 정할 수 있다
3. 녹화 파일은 PC에 바로 저장된다
4. Ctrl+C로 녹화를 멈출 수 있다

---

## 🔑 **퀴즈 정답 및 해설**

**1번 정답: 2**
`-3` 옵션은 서드파티(third-party), 즉 사용자가 설치한 앱만 보여 줍니다.

**2번 정답: 2**
`exec-out`은 폰 명령의 출력을 그대로 PC로 보내고, `>`가 그것을 파일로 저장합니다. `-p`는 PNG 형식이라는 뜻입니다.

**3번 정답: 1**
`/` 앞이 패키지명, 뒤가 액티비티 이름입니다. 액티비티가 `.`으로 시작하면 패키지명이 생략된 것입니다.

**4번 정답: 2**
앱은 마지막 화면을 기억합니다. `am force-stop`으로 완전히 종료한 뒤 실행하면 처음 화면부터 시작합니다. 4번은 앱 밖으로 나가는 것이라 다시 열면 같은 이벤트 페이지가 뜹니다.

**5번 정답: 3**
`screenrecord`는 폰 안(예: `/sdcard/demo.mp4`)에 저장합니다. PC로 가져오려면 `adb pull`이 필요합니다.

---

## 🎯 **다음 장 예고**

다음 장에서는 "어디를 눌러야 하는지" 찾는 방법을 배웁니다. 포인터 위치로 좌표를 알아내는 방법과, 화면 구조(XML)를 읽어서 글자로 버튼을 찾는 방법을 비교하며 튼튼한 매크로의 비밀을 알아봅니다!

---

이 수업자료는 Claude를 이용하여 제작되었습니다.
