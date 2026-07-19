# ClankerDash

**Local robot dashboard** for Clanker (lab Roborock). Works **fully offline** for vacuum control.

| | |
|--|--|
| **This app** | ClankerDash — web UI for cleaning, status, map/places |
| **Assistant backend (optional)** | [nanogrok](https://github.com/Abyss-c0re/nanogrok) and/or **llama.cpp** |
| **Robot control** | `rockctl` (miio local) |

**Not named nanogrok.** nanogrok is a separate tool (LLM host). ClankerDash *uses* it as an assistant when online/configured.

## Offline (Valetudo-like basics)

Works **without** Grok / cloud:

| Action | rockctl |
|--------|---------|
| Status | `rockctl status` |
| Start clean | `rockctl start` / `app_start` |
| Pause / stop | `rockctl pause` / `stop` |
| Dock / home | `rockctl home` |
| Spot clean | `rockctl spot` |
| Locate | `rockctl locate` |
| Fan | `rockctl fan quiet\|balanced\|turbo\|max` |
| Consumables | `rockctl consumable` |
| Goto place | `rockctl place go <name>` |
| Demo drive | `rockctl demo work-room` |

HTTP control: `rockctl serve` (typically `:8080`).

## Optional assistant

Settings → backend:

- **None** — pure offline dash (default for vacuum ops)
- **nanogrok** — peer/prompt to local nanogrok (`http://127.0.0.1:8787`)
- **llama.cpp** — OpenAI-compatible local LLM

## Run (lab)

### Host-first (recommended)

Robot image may lack Python. Serve UI on BlackCube; control robot over LAN:

```bash
# on robot: rockctl serve --port 8080
cd ~/Dev/clankerdash && ./scripts/run_host.sh
# open http://127.0.0.1:8790/  (or http://<blackcube-ip>:8790/)
# Settings → rockctl URL = http://192.168.1.88:8080
```

### On-robot static files

`scripts/install_robot.sh` copies UI to `/mnt/data/clankerdash/` for a future tiny static server.

## Run (lab — legacy)

```bash
# robot already has rockctl + optional nanogrok
# serve ClankerDash static UI (example)
cd /home/voldemar/Dev/clankerdash
python3 -m http.server 8790 --directory www
# or install to robot: scripts/install_robot.sh
```

Open `http://192.168.1.88:8790/` (after install on robot).

## Legal

- Independent of Roborock/Xiaomi cloud apps and of xAI/Grok branding  
- Valetudo is a separate open-source project; ClankerDash aims for *similar offline utility*, not a Valetudo fork  
- See nanogrok `LEGAL.md` for assistant backend disclaimers  

## Layout

```
www/          ClankerDash UI
docs/         architecture
scripts/      install to robot
```
