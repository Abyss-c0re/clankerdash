# ClankerDash architecture

```
Browser (ClankerDash UI)
    │
    ├─► rockctl HTTP :8080     (offline: status, clean, home, fan, places)
    │
    └─► optional assistant
            ├─ nanobot :8787  (Grok or local backend)
            └─ llama.cpp :8080/v1  (chat only; do not confuse with rockctl port)
```

**Naming rule:** UI chrome, titles, PWA name = **ClankerDash** only. Never brand the dash as “nanobot”.
