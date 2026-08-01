# Cài đặt croc

Croc là công cụ truyền file an toàn end-to-end. Cài đặt như sau:

- Trên Linux/macOS:
  ```bash
  curl https://getcroc.com | bash
  ```

- Trên Raspberry Pi (arm64):
  ```bash
  curl https://getcroc.com | bash
  ```
  (Kiểm tra bản phát hành hỗ trợ arm64)

- Cài đặt qua Homebrew (nếu có):
  ```bash
  brew install croc
  ```

- Sử dụng:
  ```bash
  croc send [file]
  croc receive [code]
  ```