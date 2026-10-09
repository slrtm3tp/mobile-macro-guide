# 📱 모바일 매크로 A to Z

안드로이드 폰을 PC에서 ADB와 Python으로 자동 조작하는 방법을 처음부터 끝까지 배우는 강의 자료입니다. 각 장은 **학습 목표 → 개념 설명 → 예제 → 핵심 정리 → 실습 과제 → 퀴즈 → 정답 및 해설** 순서로 구성되어 있습니다.

---

## 📚 강의노트

| 장 | 제목 | 주요 내용 |
| --- | --- | --- |
| 1 | [모바일 매크로 소개와 개발 환경 구축](강의노트/01_모바일매크로소개_개발환경구축.md) | 매크로 방식 비교, ADB 구조, 설치, USB·무선 연결 |
| 2 | [ADB 입력 명령: 탭, 스와이프, 입력, 키](강의노트/02_ADB입력명령_탭스와이프입력.md) | 좌표 체계, tap, swipe, 길게 누르기, text, keyevent |
| 3 | [ADB로 앱과 화면 다루기](강의노트/03_ADB앱과화면_실행캡처녹화.md) | 패키지명, 앱 실행·종료, 현재 화면, 캡처, 녹화 |
| 4 | [누를 위치 찾기: 좌표와 화면 요소](강의노트/04_누를위치찾기_좌표와화면요소.md) | 포인터 위치, uiautomator dump, XML 속성, bounds |
| 5 | [Python으로 ADB 제어하기](강의노트/05_Python으로ADB제어하기.md) | subprocess, 예외 처리, XML 분석, tap_text, wait_for |
| 6 | [매크로 스크립트 설계](강의노트/06_매크로스크립트설계.md) | STEPS 구조, 조건 대기, 재시도, 로그, 오류 캡처 |
| 7 | [원하는 화면으로 바로 가기: 딥링크와 URL](강의노트/07_원하는화면바로열기_딥링크와URL.md) | 인텐트, 딥링크, & 함정, 숨은 주소 찾기, 클립보드 |
| 8 | [이미지 매칭: OpenCV로 그림 찾아 누르기](강의노트/08_이미지매칭_OpenCV.md) | 템플릿 매칭, 점수 해석, 자동 회전 배너 |
| 9 | [예약 실행, 여러 기기, 한글 입력](강의노트/09_예약실행_여러기기_한글입력.md) | 정각 실행, cron, launchd, 스레드, ADBKeyboard |
| 10 | [더 편한 도구들](강의노트/10_더편한도구들_uiautomator2_scrcpy.md) | scrcpy, uiautomator2, MacroDroid, iOS 단축어 |
| 11 | [문제 해결과 안전 수칙](강의노트/11_문제해결과안전수칙.md) | 증상별 해결표, 약관, 보안 |
| 12 | [종합 프로젝트: 아침 브리핑 자동화](강의노트/12_종합프로젝트_아침브리핑자동화.md) | 요구사항 → 설계 → 구현 → 기록 → 자동 실행 |

---

## 💻 예제코드

모든 예제는 `예제코드` 폴더 안에서 실행합니다.

```bash
cd 예제코드
python3 adb_helper.py
```

| 파일 | 장 | 설명 |
| --- | --- | --- |
| [macro.py](예제코드/macro.py) | 6 | 혼자서도 동작하는 기본 매크로 (유튜브 영상 바로 열기) |
| [adb_helper.py](예제코드/adb_helper.py) | 5 | 다른 예제가 함께 쓰는 ADB 도우미 함수 모음 |
| [macro_v2.py](예제코드/macro_v2.py) | 6 | 재시도·로그·오류 캡처를 갖춘 매크로 실행기 |
| [clipboard_url.py](예제코드/clipboard_url.py) | 7 | 폰 클립보드의 주소를 크롬 주소창으로 읽어 오기 |
| [image_match.py](예제코드/image_match.py) | 8 | OpenCV 템플릿 만들기·찾기·탭 |
| [scheduled_run.py](예제코드/scheduled_run.py) | 9 | 정해진 시각에 정확히 실행 |
| [u2_example.py](예제코드/u2_example.py) | 10 | uiautomator2로 메뉴 이동·한글 검색 |
| [project_briefing.py](예제코드/project_briefing.py) | 12 | 종합 프로젝트 완성본 (아침 브리핑) |

---

## 🛠️ 준비물

- 안드로이드 폰 (개발자 옵션 → USB 디버깅 켜기)
- Mac 또는 Windows PC
- [Android SDK Platform-Tools](https://developer.android.com/tools/releases/platform-tools) (`brew install android-platform-tools`)
- Python 3.8 이상
- 추가 라이브러리 (8·10장): `pip3 install -r requirements.txt`

---

## ⚠️ 주의

매크로는 내 기기에서, 서비스 약관이 허용하는 범위 안에서만 사용하세요. 게임 자동 사냥, 티켓 선착순 예매, 여러 계정 반복 참여는 대부분의 서비스에서 금지되어 있으며 계정 정지 사유가 됩니다. 자세한 내용은 [11장](강의노트/11_문제해결과안전수칙.md)을 참고하세요.

---

이 수업자료는 Claude를 이용하여 제작되었습니다.
