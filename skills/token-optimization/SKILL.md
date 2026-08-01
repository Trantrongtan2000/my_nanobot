---
name: token-optimization
description: 5-layer token optimization pipeline for nanobot: ctx7 (fresh docs), RTK (output compression), Caveman (narration), ADHD (debug format), Curator (self-learning). Use to reduce context usage and improve response speed.
---

# Token Optimization Pipeline

5 lớp xử lý, áp dụng trực tiếp trong mỗi turn:

## 1. Context7 — Fetch fresh docs trước khi viết code

Khi user hỏi về library/framework/API/CLI tool/cloud service:
```bash
npx ctx7@latest library <name> "<question>"
# chọn ID /org/project từ kết quả
npx ctx7@latest docs <id> "<question>"
```
Dùng docs vừa fetch để trả lời. Không dùng training data. Prefer hơn web search cho lib docs.

Không dùng cho: refactoring, business logic, code review, general programming.

## 2. RTK — Nén command output

Khi chạy bash tool, prefix command với `rtk` nếu support:
```
rtk git log --oneline -5    # thay vì git log
rtk ls -la                  # thay vì ls
rtk read src/file.ts        # thay vì cat
rtk grep "pattern"          # thay vì grep
rtk docker ps               # thay vì docker
rtk gh pr list              # thay vì gh
```
RTK tự động filter/trim/truncate output → context chỉ nhận phần tinh gọn.

## 3. Caveman — Nén internal narration

Tool call narration, plan statements, status updates: viết kiểu caveman (bỏ filler/articles/fragments).
Telegram reply với user: vẫn giữ readability (tiếng Việt, câu hoàn chỉnh).

## 4. ADHD — Format cho debug/troubleshooting

Khi user gặp lỗi, debug, troubleshooting:
- **Lead with next action** — Dòng đầu là lệnh cụ thể làm ngay
- **Number multi-step** — Mỗi step 1 action
- **End with one concrete next step** — 1 việc < 2 phút
- **Suppress tangents** — Xong A mới offer B
- **Matter-of-fact errors** — Cause + fix. Không "Uh oh"
- **No preamble/recap/closers** — Không "Great question", "Hope this helps"

Override khi: user asks "explain" → giải thích đầy đủ (vẫn không preamble/closer).
Destructive action → confirm.

## 5. Curator — Tự học từ lỗi

Như mô tả ở section Self-Improvement Curator. Cron chạy mỗi 6h.
