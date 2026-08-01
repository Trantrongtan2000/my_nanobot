# Heartbeat Tasks

<!--
Checked periodically by nanobot gateway heartbeat cron.
Only lines under Active Tasks (not HTML comments) run.
Delete completed items — do not keep done checkboxes.
-->

## Active Tasks

- [ ] 9router health: `curl.exe -sf --max-time 5 http://127.0.0.1:20128/v1/models` — if fail, note in reply (LLM down)
- [ ] Nanobot self: `curl.exe -sf --max-time 3 http://127.0.0.1:18790/health` — if fail, note status
- [ ] Disk C: PowerShell `(Get-PSDrive C).Free/1GB` — alert only if free < 10 GB

<!-- Optional when OCR batch is running:
- [ ] OCR batch: check process + manifest progress before restarting
-->
