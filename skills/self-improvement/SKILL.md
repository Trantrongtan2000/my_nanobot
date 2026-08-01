---
name: self-improvement
description: Self-improvement curator and entity verification workflow. Error logging, root cause analysis, skill evolution, and wiki entity verification. Use after tool failures, user corrections, or creating new wiki entities.
---

# Self-Improvement & Entity Verification

## Self-Improvement Curator (Idle-Guarded)

Cơ chế tự cải tiến chạy ngầm, chỉ kích hoạt khi agent idle để tránh treo:

- **Cron**: `self_improve_cron.py` chạy mỗi 6h qua system crontab
- **Idle guard**: chỉ chạy nếu không có activity > 1 giờ
- **Interval guard**: chỉ chạy nếu cách lần chạy trước > 6 giờ
- **Auto-reflect**: tự động reflect trên unresolved errors (tối đa 5 lỗi/lần)
- **Consolidate**: tự động archive lỗi > 14 ngày chưa resolve
- **Dry-run mặc định**: thêm `--run` để execute thật

Khi đang trong conversation, agent KHÔNG được chạy curator. Việc này chỉ do cron xử lý.

Nếu user yêu cầu "tự cải tiến" / "self-improve" / "curator":
```bash
python3 /home/tan/.nanobot/workspace/self_improve_cron.py --run --consolidate --force
```

## Error Handling

- No excessive apology. State what happened + next step.
- Tool fail → alternate approach silently.
- Do not ask the user to do what tools can do.
- Do not repeat the same failed approach twice.
- **Every tool failure must be reflected**: immediately run `python3 /home/tan/.nanobot/workspace/nanobot_self_improve.py auto "<error message>"` to log + analyze root cause. Apply suggested fix if pattern-matched.
- **User correction is also an error signal**: if user corrects your output, log it: `nanobot_self_improve.py log --error "<correction>" --context "<what you did>" --source user`.

## Entity Verification Workflow

Sau khi tạo/cập nhật entity wiki, **bắt buộc** chạy verification:

1. **Chạy verify_entity.py** trên file entity mới:
   ```bash
   python3 /home/tan/.nanobot/workspace/verify_entity.py wiki/entities/<file>.md
   ```
2. **Nếu có lỗi/warning**: Ghi nhận vào `nanobot_self_improve.py`:
   ```bash
   python3 /home/tan/.nanobot/workspace/nanobot_self_improve.py auto "<error message>"
   ```
3. **Áp dụng cải tiến** nếu cần:
   ```bash
   python3 /home/tan/.nanobot/workspace/nanobot_self_improve.py apply --error_id <id> --improvement "<fix>"
   ```
4. **Cập nhật entity** dựa trên kết quả verification.
5. **Chạy lại verify** cho đến khi pass.

Quy tắc:
- Không bao giờ tạo entity mà không chạy verify.
- Mỗi lỗi phải được ghi nhận để học tập.
- Cải tiến được áp dụng ngay lập tức vào workflow.
- Báo cáo định kỳ qua `nanobot_self_improve.py report`.
