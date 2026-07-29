#!/usr/bin/env bash
# Install ClankerDash static UI on robot (separate from nanobot)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IP="${CLANKER_IP:-${CLANKER_HOST:-}}"
if [ -z "$IP" ]; then
  echo "Set CLANKER_IP or CLANKER_HOST to the robot address" >&2
  exit 1
fi
DEST=/mnt/data/clankerdash
ssh -o BatchMode=yes -o StrictHostKeyChecking=no root@"$IP" "mkdir -p $DEST"
# robots without sftp: use tar over ssh
tar -C "$ROOT/www" -cf - . | ssh -o BatchMode=yes -o StrictHostKeyChecking=no root@"$IP" "tar -C $DEST -xf -"
ssh -o BatchMode=yes -o StrictHostKeyChecking=no root@"$IP" "
  # tiny static server if python available
  if [ -f $DEST/server.pid ]; then kill \$(cat $DEST/server.pid) 2>/dev/null || true; fi
  cd $DEST
  nohup python3 -m http.server 8790 --bind 0.0.0.0 > $DEST/server.log 2>&1 &
  echo \$! > $DEST/server.pid
  echo ClankerDash http://$IP:8790/
"
