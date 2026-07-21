# clanker-dash

SPA for rockctl. **Not** nanobot UI.

```
www/index.html     source of truth
# ship: embed into rockctl then arm-build
../rockctl/scripts/embed_dash.sh www/index.html
```

served as `http://$CLANKER_HOST:8080/`.

settings: host/ports, peer token (generate via rockctl), labauth master session, web UI password gate.
