from nanobot.core.cloudflare_runtime import CloudflareComputerRuntime

def test_cloudflare_runtime_execution():
    runtime = CloudflareComputerRuntime()
    res = runtime.execute_shell_on_edge("ls -la /workspace")
    assert res["status"] == "success"
    assert res["runtime"] == "@cloudflare/computer"
    assert res["latency_ms"] < 10.0

def test_cloudflare_durable_sync():
    runtime = CloudflareComputerRuntime()
    res = runtime.sync_durable_filesystem("database/devices.db")
    assert res["status"] == "synchronized"
    assert "SQLite" in res["backend"]
