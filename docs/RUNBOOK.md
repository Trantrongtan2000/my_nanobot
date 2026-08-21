# RUNBOOK: OPERATION & INCIDENT RESPONSE

## 1. Health Checks
- Local SQLite Database: `sqlite3 database/devices.db "SELECT count(*) FROM devices;"`
- 9Router Gateway: `curl -sf http://127.0.0.1:20128/api/health`
- Telegram Webhook Status: `curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo`

## 2. Incident Playbook
- **SQLite Lock:** Switch to read-only WAL mode (`PRAGMA journal_mode=WAL;`).
- **9Router Down:** Nanobot automatically activates local fallback reasoning and buffers queued requests.
- **High-Impact Mutation:** Actions tagged `ActionRiskLevel.HIGH` or `CRITICAL` require interactive human confirmation.
