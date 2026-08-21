# Heartbeat Tasks (Cron Monitored)

- [ ] 9router health: `curl -sf --max-time 5 http://127.0.0.1:20128/api/health`
- [ ] Disk space: `df -h / | tail -1` (alert if use% ≥ 85%)
- [ ] Gateway health: `curl -sf --max-time 3 http://127.0.0.1:18790/health`
