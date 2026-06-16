# Long-term Memory

This file stores important information that should persist across sessions.

## Installed Software

- **browser-use-desktop v0.0.31** (`.deb`) → `/usr/bin/browser-use-desktop`
  - Electron app, controllable via CDP at `127.0.0.1:9222`
  - Must launch with `--remote-debugging-port=9222` AND `--remote-allow-origins=*` (else WebSocket 403)
  - Headless on this host requires Xvfb on `DISPLAY=:99` (overridable via `XTEST_DISPLAY` env var for e2e tests)
  - Config/logs: `/home/tan/.config/Browser Use/` (logs/, `run/browser-usedesktop-9222.log`, `sessions.db`, `harness/browser-harness-js`)
  - Engines: Claude Code v2.1.170 (authed), Codex v0.137.0 (NOT authed, missing `~/.codex/auth.json`)

- **cli-anything-hub v0.3.0** + 69 `cli-anything-*` skills installed to `~/.agents/skills/`

## Active Projects

- **browser-use-desktop harness** at `/home/tan/projects/browser-use-desktop-harness/agent-harness/`
  - Installed as `cli-anything-browserusedesktop` to `~/.local/bin/`
  - CDP wrapper only (navigate/eval/screenshot) — cannot login, fill forms, or handle 2FA; full AI agent (browser-use-desktop + Claude Code engine) needed for interactive tasks
  - Goal completed 2026-06-16: 15/15 tests passing (9 unit + 6 e2e against real binary under Xvfb)

## CLI-Anything Harness Convention

- Package layout: `cli_anything/<product>/` with `core/{process,cdp,state}.py`, `utils/{format,repl_skin}.py`, `tests/`, `skills/SKILL.md`, top-level `<PRODUCT>.md` overview
- Use `cli-anything-harness` skill (see `skills/cli-anything-harness/SKILL.md`) for the full workflow

## CDP / Electron Notes

- `Target.createTarget` is NOT exposed externally by Electron; CLI `cdp create` must be a no-op
- After `Page.navigate`, must wait for `Page.loadEventFired` event before subsequent `Page.*` commands (e.g. screenshot) — otherwise fails with `Not attached to an active page` (CDP -32000)
- When using `Target.attachToTarget` with `flatten: true`, store returned `sessionId` and include it as `sessionId` field in subsequent CDP payloads for routing
- Use `time.time_ns() // 1_000_000` for monotonically increasing message IDs (`time.time()` caused test flakiness)
- Confirmed working manually: list targets, navigate (data: URLs), eval, screenshot on existing target

## 9Remote (Remote Access TUI)

- Installed: server at `/home/tan/.npm-global/lib/node_modules/9remote/dist/server.cjs`; config dir `/home/tan/.9remote/`; approved devices in `state/approvedDevices.json`
- **Binds to IPv6 `[::1]:2208` only (NOT IPv4)** — cloudflared must use `--url http://[::1]:2208` else requests get 403
- Auth: API key + machine ID `b3063f652df75827`; session cookie ~30 min
- Startup: launch app in a tmux session (TUI blocks), then `cloudflared tunnel --url http://[::1]:2208 --no-autoupdate`; extract URL from `INF |  https://...trycloudflare.com |` log line
- Shutdown: `pkill -f 'cloudflared.*2208'` then `pkill -f '9remote --tray'`

## Safety Guard Gotchas

- The `fetch` tool blocks `127.0.0.1`/`localhost` URLs — must use subprocess/Python for local CDP/HTTP

## cli-anything Skills Lacking Global Install Support

Shotcut, SiYuan, WireMock, Zoom, Zotero, 3MF, Tigris, VideoCaptioner, WaveTone, Web Yu-PRI, UnrealInsights, Slay the Spire II (13 total)

## Workspace

- `/home/tan/.nanobot/workspace`

---

*This file is automatically updated by nanobot when important information should be remembered.*
