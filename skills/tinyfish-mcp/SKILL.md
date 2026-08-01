---
name: tinyfish-mcp
description: TinyFish stdio MCP server (JSON-RPC over stdio). Use when the user wants web search, web fetch, batch URL fetch, or headless browser automation via TinyFish APIs. Replaces WebSearch/WebFetch for search & fetch (free), and provides web automation tools (credit-based). Works in headless environments where URL-based MCP + OAuth cannot run.
---

# TinyFish MCP

TinyFish stdio MCP server. Communicates via JSON-RPC over stdio. Reads API key from `TINYFISH_API_KEY` env var.

## Setup

```bash
export TINYFISH_API_KEY="sk-tinyfish-..."
python3 scripts/tinyfish_mcp.py
```

No pip install needed — pure stdlib. Runs as a subprocess; the agent talks to it over stdio JSON-RPC.

## When to use

- **tinyfish_search** — web search, replaces WebSearch
- **tinyfish_fetch_content** — fetch a URL, replaces WebFetch/curl
- **tinyfish_batch_create** — fetch up to 10 URLs at once
- **tinyfish_run_web_automation** — headless browser automation (credit-based)
- **tinyfish_list_runs** — list automation run history
- **tinyfish_get_run** — get one run's details
- **tinyfish_get_steps** — get steps of a run
- **tinyfish_cancel_run** — cancel a running automation

## Notes

- Search & Fetch APIs are free, no credit cost.
- Web Automation costs credits (depends on plan).
- If automation returns an error, do NOT blind-retry. Check run status with `tinyfish_get_run` first.
- Headless environment (no browser) → use stdio MCP wrapper, not URL MCP (OAuth won't work).

## Running from the agent

Launch as a background subprocess and exchange JSON-RPC messages on stdin/stdout. Example invocation pattern:

```python
import subprocess, json
p = subprocess.Popen(
    ["python3", "scripts/tinyfish_mcp.py"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
    env={**os.environ, "TINYFISH_API_KEY": "sk-tinyfish-..."},
    text=True,
)
# send: {"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}
# read a JSON line from stdout
```
