#!/usr/bin/env python3
"""
Heavy map→3D worker for ClankerDash.

Run on BlackCube or Groot (PVE) — NOT on the vacuum.

  python3 map_3d_worker.py --port 9877

POST /v1/export
  body: multipart or JSON { "format": "obj"|"ply", "map_b64": "...", "meta": {...} }
  OR raw binary with ?format=obj&ox=&oy=&w=&h=&off=

GET  /v1/health
"""
from __future__ import annotations

import argparse
import base64
import json
import struct
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


def rrslam_dims(data: bytes):
    if len(data) < 50 or data[:6] != b"RRSLAM":
        return None
    w, h = struct.unpack_from("<II", data, 0x16)
    off = 46
    if w < 32 or h < 32 or w > 4096 or h > 4096:
        return None
    if off + w * h > len(data):
        pix = w * h
        if len(data) > pix:
            off = len(data) - pix
        else:
            return None
    return w, h, off


def export_3d(data: bytes, fmt: str, meta: dict | None = None) -> bytes:
    meta = meta or {}
    dims = rrslam_dims(data)
    if not dims:
        raise ValueError("not RRSLAM or bad dims")
    w, h, off = dims
    if meta.get("width"):
        w = int(meta["width"])
    if meta.get("height"):
        h = int(meta["height"])
    if meta.get("data_offset") is not None:
        off = int(meta["data_offset"])
    res = int(meta.get("resolution_mm") or 50)
    wall_h = int(meta.get("wall_h_mm") or 1200)
    ox = int((meta.get("origin_mm") or {}).get("x") or 0)
    oy = int((meta.get("origin_mm") or {}).get("y") or 0)
    charger = meta.get("charger") or {}
    pix = data[off : off + w * h]
    if len(pix) < w * h:
        raise ValueError("truncated pixel data")

    fmt = (fmt or "obj").lower()
    if fmt == "ply":
        lines = [
            "ply",
            "format ascii 1.0",
            "comment ClankerDash 3D export (mm) — generated on heavy worker",
            f"comment origin {ox} {oy} res {res}",
        ]
        pts = []
        for y in range(h):
            for x in range(w):
                v = pix[y * w + x]
                X = ox + x * res
                Y = oy - y * res
                if v == 0x00:
                    pts.append(f"{X:.1f} {Y:.1f} 0 40 44 52")
                    pts.append(f"{X:.1f} {Y:.1f} {wall_h} 40 44 52")
                elif v == 0x80 and ((x + y) & 3) == 0:
                    pts.append(f"{X:.1f} {Y:.1f} 0 210 215 220")
                elif 1 <= v <= 20:
                    pts.append(f"{X:.1f} {Y:.1f} 20 70 130 255")
        if charger.get("x") is not None:
            pts.append(f"{int(charger['x'])} {int(charger['y'])} 50 61 220 151")
        lines += [
            f"element vertex {len(pts)}",
            "property float x",
            "property float y",
            "property float z",
            "property uchar red",
            "property uchar green",
            "property uchar blue",
            "end_header",
        ]
        lines.extend(pts)
        return ("\n".join(lines) + "\n").encode()

    # OBJ mesh — surface walls only + floor plane
    out = [
        "# ClankerDash RRSLAM 3D (mm) — heavy worker",
        f"# origin {ox} {oy} res {res} wall_h {wall_h}",
        "o clanker_map",
    ]
    vidx = 1
    minx, miny, maxx, maxy = w, h, 0, 0
    has_free = False
    for y in range(h):
        for x in range(w):
            if pix[y * w + x] == 0x80:
                has_free = True
                minx, maxx = min(minx, x), max(maxx, x)
                miny, maxy = min(miny, y), max(maxy, y)
    if has_free:
        x0, x1 = ox + minx * res, ox + (maxx + 1) * res
        y0, y1 = oy - (maxy + 1) * res, oy - miny * res
        out += [
            f"v {x0:.1f} {y0:.1f} 0",
            f"v {x1:.1f} {y0:.1f} 0",
            f"v {x1:.1f} {y1:.1f} 0",
            f"v {x0:.1f} {y1:.1f} 0",
            f"f {vidx} {vidx+1} {vidx+2} {vidx+3}",
        ]
        vidx += 4
    for y in range(h):
        for x in range(w):
            if pix[y * w + x] != 0x00:
                continue
            edge = False
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if nx < 0 or ny < 0 or nx >= w or ny >= h or pix[ny * w + nx] == 0x80:
                        edge = True
                        break
                if edge:
                    break
            if not edge:
                continue
            x0, x1 = ox + x * res, ox + (x + 1) * res
            y0, y1 = oy - (y + 1) * res, oy - y * res
            z1 = wall_h
            out += [
                f"v {x0:.1f} {y0:.1f} 0",
                f"v {x1:.1f} {y0:.1f} 0",
                f"v {x1:.1f} {y1:.1f} 0",
                f"v {x0:.1f} {y1:.1f} 0",
                f"v {x0:.1f} {y0:.1f} {z1}",
                f"v {x1:.1f} {y0:.1f} {z1}",
                f"v {x1:.1f} {y1:.1f} {z1}",
                f"v {x0:.1f} {y1:.1f} {z1}",
            ]
            a = vidx
            out += [
                f"f {a} {a+1} {a+2} {a+3}",
                f"f {a+4} {a+7} {a+6} {a+5}",
                f"f {a} {a+4} {a+5} {a+1}",
                f"f {a+1} {a+5} {a+6} {a+2}",
                f"f {a+2} {a+6} {a+7} {a+3}",
                f"f {a+3} {a+7} {a+4} {a}",
            ]
            vidx += 8
    return ("\n".join(out) + "\n").encode()


class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if urlparse(self.path).path in ("/", "/v1/health"):
            body = json.dumps(
                {"ok": True, "service": "clanker-map-3d-worker", "role": "heavy-offload", "host": "blackcube-or-groot"}
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self._cors()
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(404)

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/v1/export":
            self.send_error(404)
            return
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n) if n else b""
        ctype = self.headers.get("Content-Type", "")
        fmt = "obj"
        meta = {}
        data = None
        q = parse_qs(urlparse(self.path).query)
        if "format" in q:
            fmt = q["format"][0]
        if "application/json" in ctype:
            j = json.loads(raw.decode() or "{}")
            fmt = j.get("format") or fmt
            meta = j.get("meta") or {}
            data = base64.b64decode(j["map_b64"])
        else:
            data = raw
            if self.headers.get("X-Map-Meta"):
                try:
                    meta = json.loads(self.headers.get("X-Map-Meta"))
                except Exception:
                    pass
        try:
            out = export_3d(data, fmt, meta)
        except Exception as e:
            body = json.dumps({"ok": False, "error": str(e)}).encode()
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self._cors()
            self.end_headers()
            self.wfile.write(body)
            return
        fname = f"clanker_map.{fmt}"
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Disposition", f'attachment; filename="{fname}"')
        self.send_header("Content-Length", str(len(out)))
        self._cors()
        self.end_headers()
        self.wfile.write(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=9877)
    ap.add_argument("--bind", default="0.0.0.0")
    args = ap.parse_args()
    print(f"map 3d worker (heavy) on http://{args.bind}:{args.port}", file=sys.stderr)
    print("Run on BlackCube or Groot — not on the vacuum.", file=sys.stderr)
    ThreadingHTTPServer((args.bind, args.port), H).serve_forever()


if __name__ == "__main__":
    main()
