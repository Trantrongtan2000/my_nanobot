--- 
title: Leanstral 1.5
status: reviewed
updated: 2026-07-21

Leanstral 1.5 là phiên bản mới nhất của model formal verification từ Mistral AI, được phát hành 2 tháng trước. Đây là model Apache-2.0 miễn phí với 119B tham số tổng và 6B tham số hoạt động, chuyên về chứng minh định lý trong ngôn ngữ Lean 4 và verification code.

## Tính năng chính
- **Số liệu hiệu năng:** 100% miniF2F, 587/672 PutnamBench, 87% FATE-H, 34% FATE-X
- **Tính năng code verification:** Phát hiện 5 bug mới trong 57 repo (ví dụ: overflow trong lib datrs/varinteger)
- **Training pipeline:** Mid-training + supervised fine-tuning + reinforcement learning với CISPO
- **Open source:** Tài nguyên trên Hugging Face + API miễn phí

## Cách cài đặt
1. `pip install mistral-vibe`
2. `/leanstall`
3. `vibe --agent lean`
4. (Tùy chọn) Cài Lean LSP MCP

## Liên quan đến MEIMS
- Có thể áp dụng cho verification logic cảnh báo thiết bị y tế
- Tốc độ tính toán ưu đãi so với phương pháp truyền thống

## Link tham khảo
- [Leanstral 1.5 trên Hugging Face](https://huggingface.co/mistralai/leanstral-1-5)
- [API miễn phí](https://mistral.ai/news/leanstral-1-5/)