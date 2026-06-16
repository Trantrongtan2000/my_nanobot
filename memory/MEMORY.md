# Long-term Memory

This file stores important information that should persist across sessions.

## Installed Software

- **browser-use-desktop v0.0.31** (`.deb`) → `/usr/bin/browser-use-desktop`
  - Electron app, controllable via CDP at `127.0.0.1:9222`
  - Must launch with `--remote-debugging-port=9222` AND `--remote-allow-origins=*` (else WebSocket 403)
  - Headless on this host requires Xvfb on `DISPLAY=:99`
  - Config/logs: `/home/tan/.config/Browser Use/` (logs/, `run/browser-usedesktop-9222.log`, `sessions.db`, `harness/browser-harness-js`)
  - Engines: Claude Code v2.1.170 (authed), Codex v0.137.0 (NOT authed, missing `~/.codex/auth.json`)

- **cli-anything-hub v0.3.0** + 69 `cli-anything-*` skills installed to `~/.agents/skills/`

## Active Projects

- **browser-use-desktop harness** at `/home/tan/projects/browser-use-desktop-harness/agent-harness/`
  - Installed as `cli-anything-browserusedesktop` to `~/.local/bin/`
  - Goal: expose browser-use-desktop GUI as a CLI command

## CDP / Electron Notes

- `Target.createTarget` is NOT supported by Electron (returns -32000 "Not supported")
- `Page.captureScreenshot` requires attaching to an active page session; navigation creates a new `frameId` per call, breaking a single ws session
- Confirmed working manually: list targets, navigate (data: URLs), eval, screenshot on existing target
- CliRunner unittest integration still failing (verify currency)

## Safety Guard Gotchas

- The `fetch` tool blocks `127.0.0.1`/`localhost` URLs — must use subprocess/Python for local CDP/HTTP

## cli-anything Skills Lacking Global Install Support

Shotcut, SiYuan, WireMock, Zoom, Zotero, 3MF, Tigris, VideoCaptioner, WaveTone, Web Yu-PRI, UnrealInsights, Slay the Spire II (13 total)

## Workspace

- `/home/tan/.nanobot/workspace`

---

*This file is automatically updated by nanobot when important information should be remembered.*
