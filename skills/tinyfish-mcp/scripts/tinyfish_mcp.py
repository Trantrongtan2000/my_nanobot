"""TinyFish stdio MCP server — wraps TinyFish REST API for headless use.

Reads TINYFISH_API_KEY from environment.
Communicates via JSON-RPC 2.0 over stdio (MCP stdio transport).
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

API_KEY = os.environ.get("TINYFISH_API_KEY", "")
REQUEST_TIMEOUT = 150

# ── REST API endpoints ────────────────────────────────────────────────────────

SEARCH_API = "https://api.search.tinyfish.ai/"
FETCH_API = "https://api.fetch.tinyfish.ai/"
AGENT_API = "https://agent.tinyfish.ai/v1/automation"
RUNS_API = "https://agent.tinyfish.ai/v1/runs"

LOG_PREFIX = "[tinyfish-mcp]"


def _log(msg: str) -> None:
    sys.stderr.write(f"{LOG_PREFIX} {msg}\n")
    sys.stderr.flush()


def json_rpc_error(id: Any, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "error": {"code": code, "message": message}, "id": id}


def json_rpc_result(id: Any, result: Any) -> dict:
    return {"jsonrpc": "2.0", "result": result, "id": id}


def _request(method: str, url: str, body: dict | None = None) -> tuple[int, Any]:
    """Make an HTTP request with the API key. Returns (status_code, parsed_body)."""
    headers = {
        "X-API-Key": API_KEY,
    }
    data = None
    full_url = url

    if body:
        if method == "GET":
            query = urllib.parse.urlencode(
                [(k, v) for k, v in body.items() if v is not None]
            )
            sep = "&" if "?" in url else "?"
            full_url = f"{url}{sep}{query}"
        else:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(full_url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            raw = resp.read().decode("utf-8")
            if raw.strip():
                return resp.status, json.loads(raw)
            return resp.status, {}
    except urllib.error.HTTPError as e:
        try:
            err_body = json.loads(e.read().decode("utf-8"))
        except Exception:
            err_body = {"error": str(e)}
        return e.code, err_body
    except urllib.error.URLError as e:
        return 0, {"error": f"URL error: {e.reason}"}
    except Exception as e:
        return 0, {"error": str(e)}


# ── Tool definitions ──────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "tinyfish_search",
        "description": "Search the web and return ranked results. Use this instead of generic WebSearch.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "count": {
                    "type": "integer",
                    "description": "Number of results (1-20)",
                    "default": 5,
                },
                "recency_minutes": {
                    "type": "integer",
                    "description": "Freshness window in minutes",
                },
                "after_date": {
                    "type": "string",
                    "description": "Lower date bound YYYY-MM-DD",
                },
                "before_date": {
                    "type": "string",
                    "description": "Upper date bound YYYY-MM-DD",
                },
                "domain_type": {
                    "type": "string",
                    "enum": ["web", "news", "research_paper"],
                    "description": "Content category",
                    "default": "web",
                },
                "location": {
                    "type": "string",
                    "description": "Country code for geo-targeted results (e.g. US, GB)",
                },
                "language": {
                    "type": "string",
                    "description": "Language code (e.g. en, vi)",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "tinyfish_fetch_content",
        "description": "Fetch and extract content from a URL. Use this instead of WebFetch / curl.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch"},
                "format": {
                    "type": "string",
                    "enum": ["markdown", "html", "json"],
                    "description": "Output format",
                    "default": "markdown",
                },
                "ttl": {
                    "type": "integer",
                    "description": "Cache TTL in seconds (0 = force fresh)",
                    "default": 0,
                },
            },
            "required": ["url"],
        },
    },
    {
        "name": "tinyfish_batch_create",
        "description": "Fetch content from multiple URLs in a single batch.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "urls": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of URLs to fetch (max 10)",
                },
                "format": {
                    "type": "string",
                    "enum": ["markdown", "html", "json"],
                    "description": "Output format",
                    "default": "markdown",
                },
                "ttl": {
                    "type": "integer",
                    "description": "Cache TTL in seconds (0 = force fresh)",
                    "default": 0,
                },
            },
            "required": ["urls"],
        },
    },
    {
        "name": "tinyfish_run_web_automation",
        "description": "Execute a goal on a live website using a headless browser. Returns once the goal is done.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "goal": {"type": "string", "description": "Natural language goal to accomplish"},
                "url": {"type": "string", "description": "Starting URL"},
                "max_steps": {
                    "type": "integer",
                    "description": "Maximum steps",
                    "default": 30,
                },
            },
            "required": ["goal"],
        },
    },
    {
        "name": "tinyfish_list_runs",
        "description": "List recent web automation runs.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "tinyfish_get_run",
        "description": "Get details of a web automation run.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "run_id": {"type": "string", "description": "Run ID"},
            },
            "required": ["run_id"],
        },
    },
    {
        "name": "tinyfish_get_steps",
        "description": "Get all steps of a web automation run.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "run_id": {"type": "string", "description": "Run ID"},
            },
            "required": ["run_id"],
        },
    },
    {
        "name": "tinyfish_cancel_run",
        "description": "Cancel a running web automation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "run_id": {"type": "string", "description": "Run ID"},
            },
            "required": ["run_id"],
        },
    },
]

# ── Protocol handlers ────────────────────────────────────────────────────────


def handle_initialize(msg_id: Any) -> dict:
    return json_rpc_result(
        msg_id,
        {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "tinyfish-mcp", "version": "1.0.0"},
        },
    )


def handle_tools_list(msg_id: Any) -> dict:
    return json_rpc_result(msg_id, {"tools": TOOLS, "nextCursor": None})


def handle_tools_call(msg_id: Any, name: str, args: dict) -> dict:
    try:
        if name == "tinyfish_search":
            return _search(msg_id, args)
        elif name == "tinyfish_fetch_content":
            return _fetch(msg_id, args)
        elif name == "tinyfish_batch_create":
            return _batch_create(msg_id, args)
        elif name == "tinyfish_run_web_automation":
            return _run_agent(msg_id, args)
        elif name == "tinyfish_list_runs":
            return _list_runs(msg_id, args)
        elif name == "tinyfish_get_run":
            return _get_run(msg_id, args)
        elif name == "tinyfish_get_steps":
            return _get_steps(msg_id, args)
        elif name == "tinyfish_cancel_run":
            return _cancel_run(msg_id, args)
        else:
            return json_rpc_error(msg_id, -32601, f"Unknown tool: {name}")
    except Exception as e:
        return json_rpc_error(msg_id, -32603, f"Internal error: {e}")


# ── Tool implementations ─────────────────────────────────────────────────────


def _ok(msg_id: Any, data: Any) -> dict:
    text = json.dumps(data, indent=2, ensure_ascii=False) if not isinstance(data, str) else data
    return json_rpc_result(msg_id, {"content": [{"type": "text", "text": text}]})


def _err(msg_id: Any, data: Any) -> dict:
    text = json.dumps(data, indent=2, ensure_ascii=False) if not isinstance(data, str) else data
    return json_rpc_result(msg_id, {"content": [{"type": "text", "text": text}], "isError": True})


def _search(msg_id: Any, args: dict) -> dict:
    params = {"query": args["query"]}
    if "count" in args:
        params["count"] = args["count"]
    if "recency_minutes" in args:
        params["recency_minutes"] = args["recency_minutes"]
    if "after_date" in args:
        params["after_date"] = args["after_date"]
    if "before_date" in args:
        params["before_date"] = args["before_date"]
    if "domain_type" in args:
        params["domain_type"] = args["domain_type"]
    if "location" in args:
        params["location"] = args["location"]
    if "language" in args:
        params["language"] = args["language"]

    status, data = _request("GET", SEARCH_API, params)
    if status != 200:
        return _err(msg_id, data)
    return _ok(msg_id, data)


def _fetch(msg_id: Any, args: dict) -> dict:
    body: dict[str, Any] = {"urls": [args["url"]]}
    if "format" in args:
        body["format"] = args["format"]
    if "ttl" in args:
        body["ttl"] = args["ttl"]

    status, data = _request("POST", FETCH_API, body)
    if status != 200:
        return _err(msg_id, data)
    return _ok(msg_id, data)


def _batch_create(msg_id: Any, args: dict) -> dict:
    body: dict[str, Any] = {"urls": args["urls"]}
    if "format" in args:
        body["format"] = args["format"]
    if "ttl" in args:
        body["ttl"] = args["ttl"]

    status, data = _request("POST", FETCH_API, body)
    if status != 200:
        return _err(msg_id, data)
    return _ok(msg_id, data)


def _run_agent(msg_id: Any, args: dict) -> dict:
    body: dict[str, Any] = {"goal": args["goal"]}
    if "url" in args:
        body["url"] = args["url"]
    if "max_steps" in args:
        body["max_steps"] = args["max_steps"]

    status, data = _request("POST", f"{AGENT_API}/run", body)
    if status != 200:
        return _err(msg_id, data)
    return _ok(msg_id, data)


def _list_runs(msg_id: Any, args: dict) -> dict:
    status, data = _request("GET", RUNS_API)
    if status != 200:
        return _err(msg_id, data)
    return _ok(msg_id, data)


def _get_run(msg_id: Any, args: dict) -> dict:
    run_id = args["run_id"]
    status, data = _request("GET", f"{RUNS_API}/{run_id}")
    if status != 200:
        return _err(msg_id, data)
    return _ok(msg_id, data)


def _get_steps(msg_id: Any, args: dict) -> dict:
    run_id = args["run_id"]
    status, data = _request("GET", f"{RUNS_API}/{run_id}/steps")
    if status != 200:
        return _err(msg_id, data)
    return _ok(msg_id, data)


def _cancel_run(msg_id: Any, args: dict) -> dict:
    run_id = args["run_id"]
    status, data = _request("POST", f"{RUNS_API}/{run_id}/cancel")
    if status != 200:
        return _err(msg_id, data)
    return _ok(msg_id, data)


# ── Message processing ────────────────────────────────────────────────────────


def send(msg: dict) -> None:
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def process(msg: dict) -> None:
    method = msg.get("method", "")
    msg_id = msg.get("id")
    params = msg.get("params", {})

    if method == "initialize":
        send(handle_initialize(msg_id))
    elif method == "notifications/initialized":
        pass  # no response needed
    elif method == "tools/list":
        send(handle_tools_list(msg_id))
    elif method == "tools/call":
        name = params.get("name", "")
        args = params.get("arguments", {})
        send(handle_tools_call(msg_id, name, args))
    elif msg_id is not None:
        send(json_rpc_error(msg_id, -32601, f"Method not found: {method}"))


def main() -> None:
    if not API_KEY:
        _log("ERROR: TINYFISH_API_KEY environment variable is required.")
        sys.exit(1)

    _log("Starting TinyFish MCP server (stdio)")
    _log(f"Search API: {SEARCH_API}")
    _log(f"Fetch API: {FETCH_API}")
    _log(f"Agent API: {AGENT_API}")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            _log(f"Invalid JSON: {line[:200]}")
            continue
        try:
            process(msg)
        except Exception as e:
            _log(f"Error: {e}")
            if msg.get("id") is not None:
                send(json_rpc_error(msg["id"], -32603, f"Internal error: {e}"))


if __name__ == "__main__":
    main()
