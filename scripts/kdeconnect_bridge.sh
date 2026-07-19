#!/usr/bin/env bash
# Minimal KDE Connect notification bridge for ClankerDash (host-side).
# Pair devices with kdeconnect-app / kdeconnect-cli first.
set -euo pipefail
PORT="${KDE_BRIDGE_PORT:-8791}"
CLI="$(command -v kdeconnect-cli || true)"
if [ -z "$CLI" ]; then
  echo "kdeconnect-cli not found" >&2
  exit 1
fi

# ultra-minimal HTTP with python
exec python3 - <<'PY'
import json, os, subprocess, re
from http.server import BaseHTTPRequestHandler, HTTPServer

CLI = "kdeconnect-cli"
PORT = int(os.environ.get("KDE_BRIDGE_PORT", "8791"))

def run(args):
    try:
        out = subprocess.check_output([CLI] + args, stderr=subprocess.STDOUT, text=True, timeout=15)
        return 0, out
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output or str(e)
    except Exception as e:
        return 1, str(e)

class H(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()
    def do_GET(self):
        if self.path.startswith("/list"):
            rc, out = run(["-a", "--list-available"])
            if rc != 0:
                rc, out = run(["--list-devices"])
            body = out.encode()
            self.send_response(200); self._cors()
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
        else:
            self.send_response(404); self.end_headers()
    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n).decode() if n else "{}"
        try:
            j = json.loads(raw)
        except Exception:
            j = {}
        if self.path.startswith("/notify"):
            msg = (j.get("message") or "ClankerDash").strip()
            dev = (j.get("device") or "").strip()
            args = ["--ping-msg", msg]
            # prefer share/notification style
            # kdeconnect-cli --device-id ID --ping-msg "text"
            # or --name
            if dev:
                if re.fullmatch(r"[0-9a-fA-F_:-]+", dev) and len(dev) > 8:
                    args = ["-d", dev, "--ping-msg", msg]
                else:
                    args = ["-n", dev, "--ping-msg", msg]
            else:
                # all available
                rc, listing = run(["-a", "--list-available"])
                if rc != 0:
                    rc, listing = run(["--list-devices"])
                # try broadcast ping without device if supported
                args = ["--ping-msg", msg]
            rc, out = run(args)
            # fallback: notify each id in listing
            if rc != 0 and not dev:
                ids = re.findall(r"([0-9a-f]{8,}(?:[-_][0-9a-f]+)*)", listing, flags=re.I)
                outs = []
                for i in ids[:8]:
                    r2, o2 = run(["-d", i, "--ping-msg", msg])
                    outs.append(f"{i}: {o2.strip()}")
                out = "\n".join(outs) or out
                rc = 0 if outs else rc
            body = (out or ("ok" if rc == 0 else "fail")).encode()
            self.send_response(200 if rc == 0 else 500); self._cors()
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
        else:
            self.send_response(404); self.end_headers()
    def log_message(self, *a):
        pass

print(f"ClankerDash KDE Connect bridge on :{PORT} (pair devices in KDE Connect first)", flush=True)
HTTPServer(("0.0.0.0", PORT), H).serve_forever()
PY
