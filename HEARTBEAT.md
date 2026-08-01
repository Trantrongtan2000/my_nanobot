# Heartbeat Tasks

<!--
Checked periodically by nanobot gateway heartbeat cron.
Only lines under Active Tasks (not HTML comments) run.
Delete completed items — do not keep done checkboxes.
-->

## Active Tasks

<!--
- [ ] 9router health: `curl -sf --max-time 5 http://127.0.0.1:20128/api/health` — if fail, note in reply and try `systemctl --user status 9router --no-pager | head -15`
- [ ] Disk: `df -h / | tail -1` — alert only if use% ≥ 85
- [ ] Nanobot self: `curl -sf --max-time 3 http://127.0.0.1:18790/health` — if fail, note status
-->

<!-- Optional when OCR batch is running:
- [ ] OCR batch: check if mistral_pdf_to_md / OCR work dir process alive; report progress from manifest if path known
-->
