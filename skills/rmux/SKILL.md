---
name: rmux
description: Build and use rmux (Rust tmux-like multiplexer) on Raspberry Pi ARM64 with low RAM. Use when user asks to install rmux, run long tasks in background, or avoid blocking Hermes agent.
---

# rmux

## When to use
- Running long tasks (build, apt upgrade) without blocking Hermes agent
- Need tmux-like session management on Pi/ARM64
- User asks "dùng rmux", "chạy task trong rmux", or "tìm hiểu rmux"

## Install on Pi ARM64 (1GB RAM)

```bash
# Preferred: install from crates.io (no source build needed)
cargo install rmux
```

**Fallback: build from source** (use if crates.io binary unavailable or needs patching)

```bash
# 1. Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"

# 2. Ensure swap ≥2GB (Pi 3 1GB RAM OOMs without it)
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile

# 3. Prepare real-filesystem build dir (Pi /tmp is tmpfs ~923MB — will fill)
mkdir -p $HOME/tmp-rust

# 4. Clone rmux
cd $HOME/tmp-rust && git clone https://github.com/Helvesec/rmux.git
cd rmux

# 5. Build with low-RAM optimizations
export TMPDIR=$HOME/tmp-rust
export CARGO_TARGET_DIR=$HOME/tmp-rust/target
export CARGO_BUILD_JOBS=1
mkdir -p $TMPDIR

# Disable LTO in Cargo.toml if OOM
sed -i '/lto = "fat"/d' Cargo.toml
sed -i '/codegen-units = 1/d' Cargo.toml

cargo build -p rmux
cp target/debug/rmux ~/.cargo/bin/
```

## Basic usage

```bash
# Create detached session
rmux new <name>

# Send command
rmux send-keys -t <name>:0.0 "<command>" C-m

# Capture output
rmux capture-pane -t <name>:0.0 -p

# Kill session
rmux kill-session -t <name>
```

Aliases: `rmux a -t <name>` = `rmux attach -t <name>`

## Fire-and-forget pattern

```bash
SESSION="myjob"
rmux new "$SESSION"
rmux send-keys -t "$SESSION":0.0 "sudo apt update && sudo apt upgrade -y" C-m

# Check later
rmux capture-pane -t "$SESSION":0.0 -p | tail -20

# Cleanup
rmux kill-session -t "$SESSION"
```

## Background watcher (non-blocking for Hermes)

```bash
SESSION="myjob"
rmux new "$SESSION"
rmux send-keys -t "$SESSION":0.0 "long_running_command" C-m

# Watcher: khi session kết thúc thì capture output ra file
(
    while rmux has-session -t "$SESSION" 2>/dev/null; do
        sleep ${POLL:-5}
    done
    OUT_DIR=/tmp/rmux_task
    mkdir -p "$OUT_DIR"
    rmux capture-pane -t "$SESSION":0.0 -p > "$OUT_DIR/${SESSION}_out.txt"
    echo "RMUX task '$SESSION' finished. Output: $OUT_DIR/${SESSION}_out.txt"
) &
```

- Dùng khi cần chạy task dài mà không muốn block Hermes agent.
- Watcher chạy background, tự động lưu output khi session xong.

## Notes
 - Binary size: 182MB (dev profile)
 - Source: https://github.com/Helvesec/rmux
 - Crates.io: `cargo install rmux` preferred over source build
 - On Pi 3 1GB RAM: swap ≥2GB, CARGO_BUILD_JOBS=1, disable LTO, put TMPDIR/CARGO_TARGET_DIR on real filesystem (Pi `/tmp` is tmpfs ~923MB)
 - Build time: ~11 min on Pi 3 ARM64 1GB RAM with optimizations above
 - Release build may OOM without increasing swap; debug build works with the optimizations above
 - Verified: build succeeded (exit code 0) with above settings
