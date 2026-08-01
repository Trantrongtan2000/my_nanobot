# Skill: decimen-optical-transfer

## Mô tả
Dự án mã nguồn mở truyền file giữa hai thiết bị không cần mạng, sử dụng QR code động + mã hóa fountain (Luby transform). Chỉ cần màn hình (sender) và camera (receiver).

## Cài đặt & Chạy
```bash
cd /home/tan/.nanobot/workspace/decimen-optical-transfer
npm install
npm run dev
```
- Sender: `https://localhost:5173/send/` (hoặc `https://lvh.me:5173/send/`)
- Receiver: `https://localhost:5173/receive/` (hoặc `https://lvh.me:5173/receive/`)

**Lưu ý:** Yêu cầu HTTPS vì receiver dùng `getUserMedia`. Vite có `@vitejs/plugin-basic-ssl` tự tạo cert tự ký. Trên điện thoại: chấp nhận cảnh báo cert một lần.

## Cấu trúc chính
```
shared/
  fountain.ts    # LT encoder/decoder (core logic)
  protocol.ts    # Header 20 byte, splitmix32 RNG
send/
  main.ts        # Sender: đọc file → encode → render QR loop
receive/
  main.ts        # Receiver: camera → zxing-wasm worker → decode
  worker.ts      # WASM barcode detector
```

## Các tham số quan trọng (Settings panel)
| Tham số | Mặc định | Ghi chú |
|---------|----------|---------|
| Payload size | 512 KB / 2 MB | Chọn trong sender |
| TX FPS | 24 | Mỗi frame cần ≥2 chu kỳ refresh màn hình |
| Bytes/frame | 1465 (QR v27) | 2953 (v40) nhanh hơn nếu decode được |
| QR ECC | L (min) | Frame disposal + fountain layer xử lý lỗi |

## Tích hợp vào MEIMS/QLTB
- **Use case**: Truyền file cấu hình, firmware, log thiết bị y tế giữa máy cách ly (air-gapped) và thiết bị di động
- **Triển khai trên Pi**: Build static (`npm run build`) → serve qua nginx + cert Let's Encrypt
- **Tốc độ thực tế**: ~129 KB/s (2 MB ảnh), có thể đạt 128-186 KB/s với frame dày hơn, 120 fps sender

## Các vấn đề đã biết & Workaround
1. **Math.log khác nhau giữa JS engines** → dùng `dlog()` deterministic trong `fountain.ts`
2. **iOS camera frame rate** → dùng `{exact: 60}` thay vì `{ideal: 60}`, đọc lại `getSettings()`
3. **requestVideoFrameCallback zombie loop** → dùng generation counter khi stop/start camera
4. **Progress bar** → theo dõi frames collected, KHÔNG phải blocks solved (LT peeling back-loads)

## Dự án tương tự (tham khảo)
- `mohankumarelec/airgapped-qr-code-transfer` — sequential chunking
- `divan/txqr` — Go implementation, write-up tốt về fountain coding
- `sz3/libcimbar` — custom color codes, mật độ cao hơn QR

## Lệnh nhanh
```bash
# Dev (HTTPS auto)
npm run dev

# Build production
npm run build
# Output: dist/ (static files, serve bằng nginx)

# Preview build
npm run preview
```

## Khi nào dùng skill này
- Cần truyền file không có mạng giữa 2 thiết bị
- Môi trường air-gapped (bệnh viện, phòng sạch, thiết bị y tế cách ly)
- Không muốn cài app, chỉ dùng trình duyệt
- File nhỏ-vừa (<10 MB), ưu tiên đơn giản hơn tốc độ cực đại