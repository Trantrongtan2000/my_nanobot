# -*- coding: utf-8 -*-
import json
import shutil
from pathlib import Path

out = Path.home() / ".nanobot" / "workspace" / "_ksnk_ocr_check.txt"
lines = []

cfg = Path.home() / ".nanobot" / "config.json"
t = cfg.read_text(encoding="utf-8") if cfg.exists() else ""
lines.append(f"config_exists={cfg.exists()} mistral_in_text={'mistral' in t.lower()}")

try:
    data = json.loads(t)

    def walk(o, p=""):
        if isinstance(o, dict):
            for k, v in o.items():
                path = f"{p}.{k}" if p else k
                if "mistral" in k.lower() or "ocr" in k.lower() or "api_key" in k.lower():
                    lines.append(f"cfg {path} type={type(v).__name__} set={bool(v) if not isinstance(v, (dict, list)) else 'container'}")
                walk(v, path)
        elif isinstance(o, list):
            for i, v in enumerate(o[:30]):
                walk(v, f"{p}[{i}]")

    walk(data)
except Exception as e:
    lines.append(f"json_err={e}")

for p in [
    Path.home() / ".nanobot" / ".env",
    Path.home() / ".nanobot" / "workspace" / ".env",
    Path.home() / ".env",
    Path.home() / ".nanobot" / "env",
]:
    lines.append(f"envfile {p} exists={p.exists()}")
    if p.exists():
        tt = p.read_text(encoding="utf-8", errors="replace")
        lines.append(
            f"  has_mistral={any('MISTRAL' in ln.upper() for ln in tt.splitlines())}"
        )

for c in ["tesseract", "magick", "pdftoppm", "gswin64c"]:
    lines.append(f"bin {c}={shutil.which(c)}")

root = Path.home() / "Downloads" / "New folder (3)"
q7root = None
for d in root.iterdir():
    if d.is_dir() and "7" in d.name:
        q7root = d
lines.append(f"q7root={q7root}")
if q7root:
    for p in sorted(q7root.rglob("*")):
        if p.is_file() and not p.name.startswith("~$") and p.name.lower() != "thumbs.db":
            lines.append(f"{p.suffix}\t{p.stat().st_size//1024}\t{p.relative_to(root)}")

# sample extract quality
ex = Path.home() / ".nanobot" / "workspace" / "wiki" / "raw" / "ksnk" / "extracts"
ok = weak = 0
for f in ex.glob("*.md"):
    body = f.read_text(encoding="utf-8")
    if "```" in body:
        chunk = body.split("```", 2)[1]
    else:
        chunk = body
    # strip fence lang
    if chunk.startswith("\n"):
        chunk = chunk[1:]
    letters = sum(ch.isalpha() for ch in chunk)
    if letters > 200:
        ok += 1
    else:
        weak += 1
lines.append(f"extract_ok_alpha>200={ok} weak={weak} total={ok+weak}")

out.write_text("\n".join(lines), encoding="utf-8")
print(f"wrote {out} lines={len(lines)}")
