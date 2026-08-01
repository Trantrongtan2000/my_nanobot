---
name: cli-anything-harness
description: Build a CLI harness for a GUI app using the cli-anything framework. Use when the user asks to "wrap <gui app> as a CLI", "create a cli-anything harness for <product>", or when extending the existing pattern (e.g. browser-use-desktop → cli-anything-browserusedesktop).
---

# cli-anything-harness

Build a CLI wrapper around a GUI/Electron app using the cli-anything framework. The harness exposes the GUI as a scriptable command while keeping a real binary (not a mock) for tests.

## When to use

- Wrapping an Electron/CDP-controllable app as a CLI
- Adding a new `cli-anything-<product>` skill alongside the existing 70+ in `~/.agents/skills/`
- Reusing the browser-use-desktop harness as a template (see "Template" below)

## Standard package layout

```
cli_anything/<product>/
├── core/
│   ├── process.py     # spawn / kill the binary, manage lifecycle
│   ├── cdp.py         # CDP client (navigate, eval, screenshot)
│   └── state.py       # session state, config, env overrides
├── utils/
│   ├── format.py      # output formatting (table/json/quiet)
│   └── repl_skin.py   # interactive REPL banner/prompt
├── tests/
│   ├── test_unit.py   # argparse, state, format
│   └── test_e2e.py    # launches real binary under Xvfb
├── skills/
│   └── SKILL.md       # user-facing skill description
└── <PRODUCT>.md       # top-level overview doc
```

Top-level install target: `~/.local/bin/cli-anything-<product>`.

## Core workflow

1. **Pick the binary** and confirm it has a headless / CDP-friendly mode. For Electron apps: launch with `--remote-debugging-port=9222` AND `--remote-allow-origins=*` (latter is mandatory — without it the WebSocket returns 403).
2. **Design the command surface** — one subcommand per GUI capability (e.g. `navigate`, `eval`, `screenshot`, `tabs`, `cookies`). Keep verbs narrow; full interactive flows (login, 2FA, forms) belong to the AI agent, not the CLI.
3. **Implement `process.py`** — subprocess lifecycle (Popen + PID file + SIGTERM/SIGKILL fallback + lock file to prevent double-launch).
4. **Implement `cdp.py`** — minimal WebSocket CDP client. Critical patterns:
   - Monotonic message IDs: `time.time_ns() // 1_000_000` (avoids `time.time()` flakiness under load)
   - `Target.attachToTarget` with `flatten: true` returns a `sessionId` — **store it** and include it in subsequent payloads for routing
   - After `Page.navigate`, **wait for `Page.loadEventFired`** before issuing `Page.*` calls (e.g. screenshot) or you'll get `Not attached to an active page` (-32000)
   - `Target.createTarget` is **not exposed externally** by Electron — make the CLI's `cdp create` command a no-op (attach to existing target only)
5. **Implement `state.py`** — env overrides (e.g. `XTEST_DISPLAY` for the Xvfb display), config paths, machine-id-derived defaults.
6. **Write tests**:
   - Unit (no binary): argparse parsing, formatters, state defaults
   - E2e: launch real binary under Xvfb on `DISPLAY=:99` (overridable via `XTEST_DISPLAY`), hit real CDP, assert screenshot bytes / eval result
7. **Validate locally** with `python -m pytest cli_anything/<product>/tests/` and the e2e harness before publishing.
8. **Install** the top-level entry point to `~/.local/bin/cli-anything-<product>` and the skill to `~/.agents/skills/cli-anything-<product>/SKILL.md`.

## Gotchas (learned the hard way)

- Electron rejects WebSocket connections from non-`http://localhost` origins — `--remote-allow-origins=*` is non-negotiable
- A single WebSocket session breaks across navigations because `frameId` changes — either attach per navigation or use the `sessionId` from `Target.attachToTarget flatten:true`
- `time.time()` collides as a message ID under test parallelism — use ns / 1e6
- The `fetch` tool blocks `127.0.0.1`/`localhost` URLs — write CDP/HTTP probes via subprocess/Python, not `fetch`
- The 13 skills lacking global install support (Shotcut, SiYuan, WireMock, Zoom, Zotero, 3MF, Tigris, VideoCaptioner, WaveTone, Web Yu-PRI, UnrealInsights, Slay the Spire II) all fail the same `pyproject.toml`/entry-point check — don't waste time debugging per-case

## Output format

The CLI follows the standard cli-anything contract:

```
$ cli-anything-<product> <verb> [--flag value ...]
[stdout JSON or human-readable table, mode-dependent]
[exit code 0 on success, non-zero on error]
```

Global flags: `--json` (machine-readable), `--quiet` (errors only), `--display :N` (Xvfb override).

## Example (browser-use-desktop)

Reference implementation at `/home/tan/projects/browser-use-desktop-harness/agent-harness/`. Surface: `navigate <url>`, `eval <js>`, `screenshot <path>`, `tabs`, `cookies`, `version`. 15/15 tests green as of 2026-06-16 (9 unit + 6 e2e against the real `.deb` under Xvfb).

## Related skills

- `long-goal` — for multi-session goals that span many harness builds
- `memory` — persist binary paths, CDP gotchas, and the harness convention here
- `cli-anything-hub` — upstream registry / installer (read-only from the harness's perspective)
