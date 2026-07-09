#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

URL="http://127.0.0.1:8765/index.html"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate

REQ_STAMP=".venv/.requirements.stamp"
if [ ! -f "$REQ_STAMP" ] || [ "requirements.txt" -nt "$REQ_STAMP" ]; then
  python -m pip install --disable-pip-version-check -r requirements.txt
  date > "$REQ_STAMP"
fi

python server/app.py &
SERVER_PID=$!

cleanup() {
  if kill -0 "$SERVER_PID" >/dev/null 2>&1; then
    kill "$SERVER_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

python - <<'PY'
import time
import urllib.request

url = "http://127.0.0.1:8765/api/health"
for _ in range(60):
    try:
        with urllib.request.urlopen(url, timeout=0.5) as resp:
            if resp.status == 200:
                raise SystemExit(0)
    except Exception:
        time.sleep(0.2)
raise SystemExit("本地服务启动超时，请查看终端错误信息。")
PY

if command -v open >/dev/null 2>&1; then
  open "$URL"
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$URL"
else
  echo "请在浏览器打开：$URL"
fi

echo ""
echo "韭菜策略已启动：$URL"
echo "关闭这个终端窗口即可停止本地服务。"
echo ""

wait "$SERVER_PID"
