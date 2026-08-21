# 🌐 Hướng Dẫn Triển Khai Nanobot Lên Cloudflare Computer

Dự án Nanobot hiện đã tích hợp sẵn runtime **`@cloudflare/computer`** và **Cloudflare Workers** giúp bạn có thể chạy Agent 24/7 trên Edge toàn cầu với chi phí **gần như 0 đồng**.

---

## 📦 Cấu trúc Thư mục Cloudflare
```text
cloudflare/
├── wrangler.toml       # Cấu hình Cloudflare Worker, Durable Objects và SQLite
├── package.json        # Dependencies (@cloudflare/computer)
└── src/
    └── index.ts        # Worker Handler, Telegram Webhook & V8 Isolate Engine
```

---

## 🚀 Các Bước Deploy Nhanh (Chỉ 2 phút)

### Bước 1: Cài đặt công cụ Wrangler của Cloudflare
```bash
npm install -g wrangler
```

### Bước 2: Đăng nhập Cloudflare
```bash
wrangler login
```

### Bước 3: Deploy lên mạng lưới Cloudflare
```bash
cd cloudflare
wrangler deploy
```

Sau khi deploy thành công, bạn sẽ nhận được một URL webhook (ví dụ: `https://nanobot-computer.<your-subdomain>.workers.dev`).

### Bước 4: Đặt Webhook cho Telegram Bot
```bash
curl -F "url=https://nanobot-computer.<your-subdomain>.workers.dev/telegram/webhook" \
  https://api.telegram.org/bot<YOUR_TELEGRAM_BOT_TOKEN>/setWebhook
```

🎉 Giờ đây Nanobot sẽ trực 24/7 trên Cloudflare với độ trễ phản hồi tính bằng mili-giây!
