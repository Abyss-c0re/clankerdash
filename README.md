# clanker-dash (ClankerDash)

Offline SPA for **rockctl**. **Not** the nanobot chat UI ([nanobot-wrapper](https://github.com/Abyss-c0re/nanobot-wrapper)).

**Not affiliated with Roborock, Xiaomi, or Valetudo.**

```
www/index.html     source of truth
# ship: embed into rockctl then arm-build
../rockctl/scripts/embed_dash.sh www/index.html
```

Served as `http://$CLANKER_HOST:8080/` when embedded in rockctl, or via
`scripts/run_host.sh` for local development.

Settings: host/ports, peer token (generate via rockctl), labauth master session, web UI password gate.

## Related

| Repo | Role |
|------|------|
| [rockctl](https://github.com/Abyss-c0re/rockctl) | miio CLI + HTTP that embeds this SPA |
| [nanobot](https://github.com/Abyss-c0re/nanobot) | optional assistant peer |
| [nanobot-wrapper](https://github.com/Abyss-c0re/nanobot-wrapper) | optional chat UI for nanobot |

## License

**Cubechain License** — [LICENSE](LICENSE). See also [LEGAL.md](LEGAL.md).
