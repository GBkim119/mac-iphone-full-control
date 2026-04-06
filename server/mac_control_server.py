"""
Mac Control API Server
포트 5001에서 실행 - 아이폰 웹 대시보드와 연동
"""

import subprocess
import os
import datetime
import json
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io

app = Flask(__name__, static_folder=None)
CORS(app)

WEBAPP_PATH = os.path.join(os.path.dirname(__file__), '..', 'webapp', 'index.html')


@app.route('/')
def index():
    if os.path.exists(WEBAPP_PATH):
        with open(WEBAPP_PATH, 'r') as f:
            return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}
    return '<h1>Mac Control Server</h1><p>webapp/index.html not found</p>', 200

# 인증 토큰 (.env 파일 또는 환경변수에서 읽기)
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "mac-control-secret-2024")


def require_auth(f):
    """Bearer 토큰 인증 데코레이터"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if auth != f"Bearer {AUTH_TOKEN}":
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


def run_cmd(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return (r.stdout + r.stderr).strip()
    except Exception as e:
        return str(e)


# ─────────────────────────────────────────────
# 헬스 체크 (인증 불필요)
# ─────────────────────────────────────────────

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "Mac Control Server"})


# ─────────────────────────────────────────────
# 볼륨
# ─────────────────────────────────────────────

@app.route("/api/volume", methods=["POST"])
@require_auth
def set_volume():
    data = request.json or {}
    level = max(0, min(100, int(data.get("level", 50))))
    result = run_cmd(f"osascript -e 'set volume output volume {level}'")
    return jsonify({"ok": True, "level": level, "result": result})


@app.route("/api/mute", methods=["POST"])
@require_auth
def mute():
    run_cmd("osascript -e 'set volume with output muted'")
    return jsonify({"ok": True, "muted": True})


@app.route("/api/unmute", methods=["POST"])
@require_auth
def unmute():
    run_cmd("osascript -e 'set volume without output muted'")
    return jsonify({"ok": True, "muted": False})


# ─────────────────────────────────────────────
# 앱 제어
# ─────────────────────────────────────────────

@app.route("/api/app/open", methods=["POST"])
@require_auth
def open_app():
    data = request.json or {}
    name = data.get("name", "")
    if not name:
        return jsonify({"error": "app name required"}), 400
    result = run_cmd(f'open -a "{name}"')
    return jsonify({"ok": True, "app": name, "result": result})


@app.route("/api/app/close", methods=["POST"])
@require_auth
def close_app():
    data = request.json or {}
    name = data.get("name", "")
    result = run_cmd(f"osascript -e 'quit app \"{name}\"'")
    return jsonify({"ok": True, "app": name, "result": result})


# ─────────────────────────────────────────────
# 시스템 정보
# ─────────────────────────────────────────────

@app.route("/api/system")
@require_auth
def system_info():
    battery = run_cmd("pmset -g batt | grep -oE '[0-9]+%' | head -1")
    disk = run_cmd("df -h / | tail -1 | awk '{print $3\"/\"$2\" (\"$5\")'\"}")
    mem = run_cmd("top -l 1 -n 0 | grep PhysMem | awk '{print $2\" used, \"$6\" unused\"}'")
    uptime = run_cmd("uptime | awk -F',' '{print $1}' | awk '{print $3, $4}'")
    ip = run_cmd("ifconfig | grep 'inet ' | grep -v 127.0.0.1 | head -1 | awk '{print $2}'")

    return jsonify({
        "battery": battery or "정보 없음",
        "disk": disk or "정보 없음",
        "memory": mem or "정보 없음",
        "uptime": uptime or "정보 없음",
        "local_ip": ip or "정보 없음",
        "tailscale_ip": "100.78.249.68"
    })


# ─────────────────────────────────────────────
# 알림 & TTS
# ─────────────────────────────────────────────

@app.route("/api/notify", methods=["POST"])
@require_auth
def notify():
    data = request.json or {}
    title = data.get("title", "알림")
    message = data.get("message", "")
    script = f'display notification "{message}" with title "{title}"'
    run_cmd(f"osascript -e '{script}'")
    return jsonify({"ok": True})


@app.route("/api/speak", methods=["POST"])
@require_auth
def speak():
    data = request.json or {}
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "text required"}), 400
    run_cmd(f'say "{text}"', timeout=60)
    return jsonify({"ok": True, "text": text})


# ─────────────────────────────────────────────
# 시스템 제어
# ─────────────────────────────────────────────

@app.route("/api/sleep", methods=["POST"])
@require_auth
def sleep_mac():
    run_cmd("pmset sleepnow")
    return jsonify({"ok": True, "action": "sleep"})


@app.route("/api/url", methods=["POST"])
@require_auth
def open_url():
    data = request.json or {}
    url = data.get("url", "")
    if not url:
        return jsonify({"error": "url required"}), 400
    run_cmd(f'open "{url}"')
    return jsonify({"ok": True, "url": url})


# ─────────────────────────────────────────────
# 클립보드
# ─────────────────────────────────────────────

@app.route("/api/clipboard", methods=["GET"])
@require_auth
def get_clipboard():
    content = run_cmd("pbpaste")
    return jsonify({"ok": True, "content": content})


@app.route("/api/clipboard", methods=["POST"])
@require_auth
def set_clipboard():
    data = request.json or {}
    text = data.get("text", "")
    run_cmd(f"echo '{text}' | pbcopy")
    return jsonify({"ok": True})


# ─────────────────────────────────────────────
# 스크린샷
# ─────────────────────────────────────────────

@app.route("/api/screenshot")
@require_auth
def screenshot():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"/tmp/screenshot_{ts}.png"
    run_cmd(f"screencapture -x {path}")

    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read()
        os.remove(path)
        return app.response_class(data, mimetype="image/png")
    return jsonify({"error": "스크린샷 실패"}), 500


# ─────────────────────────────────────────────
# 터미널 명령 실행
# ─────────────────────────────────────────────

@app.route("/api/command", methods=["POST"])
@require_auth
def run_command():
    data = request.json or {}
    cmd = data.get("command", "")
    if not cmd:
        return jsonify({"error": "command required"}), 400
    # 위험한 명령어 차단
    blocked = ["rm -rf", "sudo rm", "format", "diskutil eraseDisk"]
    for b in blocked:
        if b in cmd:
            return jsonify({"error": f"차단된 명령어: {b}"}), 403
    result = run_cmd(cmd)
    return jsonify({"ok": True, "result": result})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print(f"Mac Control Server 시작 - 포트 {port}")
    print(f"인증 토큰: {AUTH_TOKEN}")
    print(f"아이폰 접속: http://100.78.249.68:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
