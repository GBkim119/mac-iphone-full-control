# 📱 iPhone → MacBook 완전 제어 프로젝트
> **mac-iphone-full-control** | 아이폰으로 맥북을 AI + 웹앱으로 완전히 원격 제어

---

## 🎯 프로젝트 목표

아이폰 하나로 맥북의 모든 것을 제어한다:
- AI 코딩 에이전트 (Cline + DeepSeek Coder)
- 실시간 맥 제어 웹 대시보드 (볼륨, 앱, 알림, TTS, 스크린샷)
- Open Interpreter로 자연어 → 맥 명령 실행
- 자동 시작 & 텔레그램 알림

---

## 🏗 전체 아키텍처

```
┌─────────────────────────────────────────────────────┐
│                     MacBook                         │
│                                                     │
│  Ollama ──── DeepSeek Coder / Qwen2.5 Coder        │
│    │                                                │
│  Open WebUI (포트 3000) ── mac_toolkit (15가지)     │
│    │                                                │
│  VSCode + Cline ─── AI 코딩 에이전트                │
│    │                                                │
│  Open Interpreter ─── 자연어 → 맥 명령              │
│    │                                                │
│  Flask API 서버 (포트 5001) ── 웹앱 백엔드           │
│                                                     │
└──────────────┬──────────────────────────────────────┘
               │  Tailscale VPN (100.78.249.68)
               │
        ┌──────▼──────┐
        │   iPhone    │
        │             │
        │  Tailscale  │
        │  Termius    │  ← SSH 터미널
        │  Safari →   │  ← 웹 대시보드 (포트 5001)
        │  Open WebUI │  ← AI 채팅 (포트 3000)
        └─────────────┘
```

---

## ✅ 설치 체크리스트

### Phase 0: 기반 완료 (이미 설정됨)

- [x] Ollama 설치
- [x] llama3.1:8b 모델 설치
- [x] Open WebUI v0.8.12 설치 (포트 3000)
- [x] LaunchAgent 자동시작 설정 (`com.openwebui.serve.plist`)
- [x] ngrok HTTP 터널 자동시작 (`com.ngrok.tunnel.plist`)
- [x] Tailscale 설치 (고정 IP: `100.78.249.68`)
- [x] Mac 제어 툴킷 15가지 (Open WebUI에 `mac_full_control` 등록)
- [x] 텔레그램 URL 알림 (`start-ngrok-notify.sh`)
- [x] 아이폰 Tailscale + Termius SSH 접속 설정

---

### Phase 1: AI 모델 업그레이드

- [ ] DeepSeek Coder v2 설치
  ```bash
  ollama pull deepseek-coder-v2
  ```
- [ ] Qwen2.5 Coder 설치
  ```bash
  ollama pull qwen2.5-coder:7b
  ```
- [ ] Open WebUI에서 모델 테스트

---

### Phase 2: 개발 환경 (VSCode + Cline)

- [ ] VSCode 설치 확인
  ```bash
  brew install --cask visual-studio-code
  ```
- [ ] Cline 확장 설치 (VSCode → Extensions → "Cline" 검색)
- [ ] Cline에 Ollama 연동
  - Provider: `Ollama`
  - Base URL: `http://localhost:11434`
  - Model: `deepseek-coder-v2` 또는 `qwen2.5-coder:7b`
- [ ] 테스트: "Hello World Python 파일 만들어줘"

---

### Phase 3: Open Interpreter 설치

- [ ] Python 가상환경 생성
  ```bash
  python3 -m venv ~/ai-env
  source ~/ai-env/bin/activate
  ```
- [ ] Open Interpreter 설치
  ```bash
  pip install open-interpreter
  ```
- [ ] Ollama 연동 설정
  ```bash
  interpreter --model ollama/llama3.1:8b
  ```
- [ ] 테스트: "바탕화면에 hello.txt 만들어줘"
- [ ] Open WebUI 툴로 Interpreter 연동 (선택)

---

### Phase 4: 웹 대시보드 (아이폰 제어 UI)

- [ ] Flask 설치
  ```bash
  source ~/ai-env/bin/activate
  pip install flask flask-cors psutil python-dotenv
  ```
- [ ] `server/mac_control_server.py` 실행
  ```bash
  cd ~/mac-iphone-full-control/server
  bash launch_server.sh
  ```
- [ ] 아이폰에서 접속 테스트
  - Tailscale 연결 후 Safari: `http://100.78.249.68:5001`
- [ ] 인증 토큰 설정 (`.env` 파일)
- [ ] 모든 버튼 동작 확인
  - [ ] 볼륨 슬라이더
  - [ ] 앱 실행 (Safari, Finder, VSCode)
  - [ ] 시스템 정보
  - [ ] 알림 보내기
  - [ ] TTS (텍스트 읽기)
  - [ ] 스크린샷
  - [ ] 잠자기

---

### Phase 5: LaunchAgent 자동화

- [ ] Flask 서버 자동시작 plist 생성
  ```bash
  cp ~/mac-iphone-full-control/server/com.maccontrol.server.plist \
     ~/Library/LaunchAgents/
  launchctl load ~/Library/LaunchAgents/com.maccontrol.server.plist
  ```
- [ ] 텔레그램 알림에 Flask 서버 URL 추가
- [ ] 맥 재시작 후 전체 자동시작 확인

---

### Phase 6: 완성 & 고도화 (선택)

- [ ] 아이폰 홈 화면에 웹앱 단축키 추가 (Safari → 공유 → 홈 화면에 추가)
- [ ] Open WebUI에서 자연어로 맥 제어 ("볼륨 50으로 해줘")
- [ ] Cline으로 코딩 작업 원격 지시
- [ ] 파일 업로드/다운로드 기능 추가

---

## 📱 현재 아이폰 접속 방법

| 용도 | 앱 | 주소 |
|------|-----|------|
| AI 채팅 | Safari | `http://100.78.249.68:3000` |
| 맥 제어 대시보드 | Safari | `http://100.78.249.68:5001` |
| SSH 터미널 | Termius | `100.78.249.68` (port 22) |

> 📌 **Tailscale 앱 먼저 실행** → 연결 확인 후 접속

---

## 📂 레포 구조

```
mac-iphone-full-control/
├── PROJECT_README.md          # 이 파일 (전체 계획 & 체크리스트)
├── .gitignore
├── webapp/
│   └── index.html             # 아이폰용 맥 제어 대시보드
└── server/
    ├── mac_control_server.py  # Flask API 서버 (포트 5001)
    └── launch_server.sh       # 서버 실행 스크립트
```

---

## 🔑 주요 정보

| 항목 | 값 |
|------|-----|
| 맥 Tailscale IP | `100.78.249.68` |
| Open WebUI 포트 | `3000` |
| Flask API 포트 | `5001` |
| Ollama 포트 | `11434` |
| 텔레그램 Chat ID | `6794864269` |
| GitHub 유저 | `GBkim119` |

---

## 🚀 빠른 시작 (설정 완료 후)

```bash
# 1. 텔레그램으로 URL 확인 (자동 전송됨)
# 2. Tailscale 연결
# 3. 아이폰 Safari → http://100.78.249.68:3000 (AI)
# 4. 아이폰 Safari → http://100.78.249.68:5001 (제어판)
```
