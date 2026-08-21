---
name: rclone-mcp
description: Install rclone on Raspberry Pi ARM64 and configure rclone-mcp MCP server in Hermes Agent. Use when user asks to install rclone, setup rclone-mcp, or register MCP tools for cloud storage.
---

# rclone-mcp

## When to use
- Installing rclone on Pi ARM64 without sudo
- Configuring rclone-mcp in Hermes Agent
- User asks "cài rclone", "cấu hình rclone-mcp", "MCP server cho rclone"

## Install rclone on Pi ARM64 (no sudo)

```bash
mkdir -p ~/.local/bin
cd ~/.local/bin
wget -q https://downloads.rclone.org/rclone-current-linux-arm64.zip
unzip -o rclone-current-linux-arm64.zip
cp -f rclone-*/rclone .
chmod +x rclone
rm -rf rclone-*/ rclone-current-linux-arm64.zip
rclone version
```

## Configure Hermes MCP server

Edit `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  rclone:
    command: "npx"
    args: ["-y", "rclone-mcp"]
    env:
      PATH: "/home/tan/.local/bin:/usr/local/bin:/usr/bin:/bin"
    timeout: 120
    connect_timeout: 60
```

## Activate

Restart Hermes Agent. Tools auto-register with prefix `mcp_rclone_*`.

## Verify

```bash
npx rclone-mcp stdio --help
# Should show 56 tools across core, config, operations, sync
```

## Notes
- Version: v1.74.2
- Binary: `/home/tan/.local/bin/rclone`
- Configures 56 MCP tools automatically
- After restart, use tools like `mcp_rclone_list_remotes`, `mcp_rclone_sync`, etc.
