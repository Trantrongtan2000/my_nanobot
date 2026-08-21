# Hướng Dẫn Thiết Lập Nanobot 2 Máy (PC + Termux)

## Tổng Quan

- **PC**: chạy nanobot bot A (`@culi_tinyclaw_bot`), LLM orfree + TinyFish MCP
- **Phone (Termux)**: chạy nanobot bot B, LLM gì tùy (orfree/ollama)
- **Telegram group**: add cả 2 bot, `groupPolicy: "mention"` → mỗi bot trả lời khi @tag

---

## 1. Cài Đặt Termux

```bash
pkg update && pkg upgrade -y
pkg install python git -y
pip install nanobot-ai
```

## 2. Cấu Hình

Tạo file `~/.nanobot/config.json` với nội dung sau:

```json
{
  "providers": {
    "orfree": {
      "apiKey": "${ORFREE_API_KEY}",
      "apiBase": "http://<DIA_CHI_IP_PC>:20128/v1"
    }
  },
  "modelPresets": {
    "primary": {
      "label": "orfree",
      "provider": "orfree",
      "model": "orfree",
      "maxTokens": 8192,
      "contextWindowTokens": 200000,
      "temperature": 0.1
    }
  },
  "agents": {
    "defaults": {
      "modelPreset": "primary",
      "maxConcurrentSubagents": 2
    }
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "[REDACTED]",
      "groupPolicy": "mention",
      "allowFrom": ["*"]
    }
  }
}
```

> **Giải thích**:
> - `groupPolicy: "mention"` — bot chỉ reply khi được @tag trong group
> - `allowFrom: ["*"]` — cho phép tất cả user (bỏ pairing)
> - Thay `<DIA_CHI_IP_PC>` bằng IP thật của máy PC (VD `192.168.1.100`)
> - Thay token bot thật vào `TELEGRAM_BOT_TOKEN`

## 3. Chạy

```bash
export TELEGRAM_BOT_TOKEN='<token_cua_bot_B>'
export ORFREE_API_KEY='[REDACTED_SECRET]'

rm -f ~/.nanobot/run/gateway.json
nohup nanobot gateway >> ~/.nanobot/logs/gateway.log 2>&1 &

# Kiểm tra
sleep 5
tail -10 ~/.nanobot/logs/gateway.log
nanobot channels status
```

> **Giải thích**:
> - `TELEGRAM_BOT_TOKEN`: token lấy từ @BotFather trên Telegram (tạo bot B mới)
> - `ORFREE_API_KEY`: key của LLM orfree (dùng chung với PC)
> - `rm -f .../run/gateway.json`: xóa state cũ nếu gateway trước bị crash
> - `nohup ... &`: chạy nền, không tắt khi đóng terminal

## 4. Tạo Telegram Group

1. Mở Telegram → New Group
2. Thêm **cả 2 bot** vào group
3. Trong group:
   - Gửi `@bot_A <lệnh>` — bot PC trả lời
   - Gửi `@bot_B <lệnh>` — bot phone trả lời
4. Nếu chưa approve: gửi `/pairing approve <code>` trong DM với từng bot

## 5. Kiểm Tra

```bash
nanobot status
nanobot channels status
```

Output kỳ vọng:
- `Config: ✓`
- `Telegram: ✓`
- Health endpoint: `http://127.0.0.1:18790/health` → `{"status": "ok"}`

## 6. Cấp Quyền (nếu cần)

Nếu bot chưa được approve trong group:

```bash
# Gửi tin nhắn DM tới bot -> nó gửi pairing code
# Approve mã đó:
nanobot pairing approve <CODE>
```

Hoặc bỏ hẳn pairing: thêm `"allowFrom": ["*"]` vào config (như trên).

## 7. Thay LLM Riêng Cho Bot B

Thay vì dùng orfree của PC, bot B có thể dùng Ollama:

```json
{
  "providers": {
    "ollama": {
      "apiBase": "http://localhost:11434"
    }
  },
  "modelPresets": {
    "primary": {
      "provider": "ollama",
      "model": "qwen3.5:9b"
    }
  }
}
```

## 8. Important Notes

- `TELEGRAM_BOT_TOKEN` — mỗi bot 1 token riêng
- `ORFREE_API_KEY` — dùng chung key nếu cùng dùng orfree
- `groupPolicy: "mention"` — tránh 2 bot reply chồng chéo
- Mỗi port `18790` gateway riêng, port khác không ảnh hưởng gì
- Cần `allowFrom: ["*"]` hoặc pairing approve trước khi group hoạt động
