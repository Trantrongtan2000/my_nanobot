# Agent Discovery

Auto-discovery and messaging between nanobot agents on a local network.

## When to use

- Multiple nanobot instances on the same LAN need to find each other
- Agent-to-agent messaging without central broker
- Quick health/availability checks across devices (Pi, Orange Pi, TVBox, Windows host)

## Prerequisites

- Python 3.7+ on each agent node
- UDP port `19999` open for broadcast
- TCP port `19999` open for direct messages
- All nodes on the same subnet

## Setup

1. Copy the `agent-discovery` skill folder to each agent node:
   ```bash
   scp -r skills/agent-discovery user@node:/path/to/skills/
   ```

2. On each node, verify Python can import required modules (stdlib only: `socket`, `threading`, `json`, `time`, `sys`).

## Usage

Run from the skill directory:

```bash
python3 discover.py start    # Broadcast presence + listen for others
python3 discover.py list     # Show discovered agents
python3 discover.py send <ip> <message>  # Send message to agent
```

## Behavior

- **start**: Broadcasts this agent's name and IP every 5 seconds; listens for broadcasts from other agents. Runs until Ctrl+C.
- **list**: Prints currently known agents (name, IP, last seen).
- **send**: Sends a text message to the target agent IP over TCP.

## Output

```
🚀 Bắt đầu Agent Discovery...
   Agent name: nanobot
   Local IP: 192.168.2.21
   Port: 19999

👂 Đang lắng nghe trên port 19999...
📢 Broadcast: nanobot @ 192.168.2.21
```

## Files

- `discover.py` — main script (broadcast + listen + send)
- `config.json` — default config (port, broadcast interval, agent name)
- `SKILL.md` — this file

## Notes

- Default port is `19999`. Change in `config.json` if it conflicts.
- Broadcast uses UDP; messages use TCP.
- On Windows, firewall may prompt for Python network access on first run.
- If nanobot runtime safety guard blocks private IPs, run the script from the local terminal or whitelist `192.168.0.0/16` in the gateway config.
