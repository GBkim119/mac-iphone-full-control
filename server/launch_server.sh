#!/bin/bash
# Mac Control Flask 서버 실행 스크립트

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

# .env 파일 로드
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

AUTH_TOKEN="${AUTH_TOKEN:-mac-control-secret-2024}"
PORT="${PORT:-5001}"

# Python 가상환경 확인
VENV="$HOME/ai-env"
if [ -d "$VENV" ]; then
    source "$VENV/bin/activate"
else
    echo "⚠️  가상환경이 없습니다. 아래 명령어로 설치하세요:"
    echo "    python3 -m venv ~/ai-env"
    echo "    source ~/ai-env/bin/activate"
    echo "    pip install flask flask-cors psutil python-dotenv"
    exit 1
fi

# 의존성 확인
python3 -c "import flask" 2>/dev/null || {
    echo "Flask 설치 중..."
    pip install flask flask-cors psutil python-dotenv
}

echo "========================================="
echo "  Mac Control Server"
echo "  포트: $PORT"
echo "  토큰: $AUTH_TOKEN"
echo "  아이폰 접속: http://100.78.249.68:$PORT"
echo "========================================="

AUTH_TOKEN="$AUTH_TOKEN" PORT="$PORT" python3 "$SCRIPT_DIR/mac_control_server.py"
