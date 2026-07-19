# Minimal KDE Connect protocol (ClankerDash)

## Goal
Send short notifications to phones/desktops the user has **already paired** in KDE Connect.

## Components
1. **Settings UI** — device id/name (optional) + test message  
2. **Host bridge** — `scripts/kdeconnect_bridge.sh` listens on **:8791**  
3. **kdeconnect-cli** — must be installed and devices paired on the host

## Run
```bash
# terminal 1: dashboard
./scripts/run_host.sh

# terminal 2: notify bridge
./scripts/kdeconnect_bridge.sh
```

## API (host-local)
- `GET  http://127.0.0.1:8791/list` — list devices  
- `POST http://127.0.0.1:8791/notify` `{"device":"","message":"ClankerDash ping"}`  

Empty `device` = best-effort all / default ping.

## Pairing
User pairs in the normal KDE Connect app (phone ↔ BlackCube). ClankerDash does not implement pairing crypto — only notify.
