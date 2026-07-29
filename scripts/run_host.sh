#!/usr/bin/env bash
# Serve ClankerDash on the lab PC; point Settings → rockctl at the robot.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${PORT:-8790}"
ROBOT="${CLANKER_HOST:-ROBOT_HOST}"
echo "ClankerDash http://127.0.0.1:$PORT/"
echo "Settings → rockctl URL: http://${ROBOT}:8080  (rockctl serve on robot)"
echo "Assistant optional: nanobot http://${ROBOT}:8787"
cd "$ROOT/www" && exec python3 -m http.server "$PORT" --bind 0.0.0.0
