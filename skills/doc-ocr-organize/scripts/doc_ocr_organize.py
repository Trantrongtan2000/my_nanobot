#!/usr/bin/env python3
"""PDF/image → render pages → OCR → organize with mistral-small-2603.

Pipeline:
  1. If PDF: render each page to PNG (pdftoppm preferred, else PyMuPDF).
  2. If image: use as-is (optionally normalize via Pillow).
  3. OCR via Mistral OCR API (image_url per page, or document_url for whole PDF).
  4. Organize / rewrite OCR markdown with chat model (default mistral-small-2603).

Env:
  MISTRAL_API_KEY[, _2, _3]  — OCR + organize (Mistral cloud)
  OR  ORFREE_API_KEY / NANOBOT_ORFREE_KEY + ORFREE_BASE
      (default http://127.0.0.1:20128/v1) for organize step only via 9router

Usage:
  python3 doc_ocr_organize.py INPUT.pdf [-o OUT_DIR] [--dpi 200]
  python3 doc_ocr_organize.py scan.png --no-organize
  python3 doc_ocr_organize.py doc.pdf --organize-model mistral-small-2603
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import requests

MISTRAL_URL = os.environ.get("MISTRAL_API_URL", "https://api.mistral.ai/v1").rstrip("/")
OCR_MODEL = os.environ.get("MISTRAL_OCR_MODEL", "mistral-ocr-latest")
DEFAULT_ORGANIZE_MODEL = os.environ.get("MISTRAL_ORGANIZE_MODEL", "mistral-small-2603")
ORFREE_BASE = os.environ.get("ORFREE_BASE", "http://127.0.0.1:20128/v1").rstrip("/")

_KEYS = [
    os.environ.get("MISTRAL_API_KEY", ""),
    os.environ.get("MISTRAL_API_KEY_2", ""),
    os.environ.get("MISTRAL_API_KEY_3", ""),
]
_KEYS = [k for k in _KEYS if k and k not in ("your-api-key-here",)]
_key_i = 0


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def next_key() -> str:
    global _key_i
    if not _KEYS:
        raise SystemExit("Missing MISTRAL_API_KEY (and optional MISTRAL_API_KEY_2/3)")
    k = _KEYS[_key_i % len(_KEYS)]
    _key_i += 1
    return k


def current_key() -> str:
    if not _KEYS:
        raise SystemExit("Missing MISTRAL_API_KEY")
    return _KEYS[_key_i % len(_KEYS)]


def b64_file(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def mime_for(path: Path) -> str:
    mt, _ = mimetypes.guess_type(str(path))
    if mt:
        return mt
    ext = path.suffix.lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".tif": "image/tiff",
        ".tiff": "image/tiff",
        ".pdf": "application/pdf",
    }.get(ext, "application/octet-stream")


def render_pdf_to_images(pdf: Path, out_dir: Path, dpi: int = 200) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = out_dir / "page"
    pdftoppm = shutil.which("pdftoppm")
    if pdftoppm:
        cmd = [pdftoppm, "-png", "-r", str(dpi), str(pdf), str(prefix)]
        log(f"[*] pdftoppm: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        pages = sorted(out_dir.glob("page-*.png")) or sorted(out_dir.glob("page*.png"))
        if pages:
            return pages
        raise RuntimeError("pdftoppm ran but produced no PNGs")

    try:
        import fitz  # PyMuPDF
    except ImportError as e:
        raise RuntimeError("Need pdftoppm (poppler-utils) or pymupdf") from e

    log(f"[*] PyMuPDF render dpi={dpi}")
    doc = fitz.open(pdf)
    pages = []
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    for i, page in enumerate(doc, 1):
        pix = page.get_pixmap(matrix=mat, alpha=False)
        p = out_dir / f"page-{i:03d}.png"
        pix.save(str(p))
        pages.append(p)
    doc.close()
    return pages


def normalize_image(src: Path, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / src.name
    if src.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
        if src.resolve() != dest.resolve():
            shutil.copy2(src, dest)
        return dest
    try:
        from PIL import Image
    except ImportError:
        shutil.copy2(src, dest)
        return dest
    img = Image.open(src).convert("RGB")
    dest = out_dir / (src.stem + ".png")
    img.save(dest, "PNG")
    return dest


def mistral_post(path: str, payload: dict, timeout: int = 180) -> dict:
    url = f"{MISTRAL_URL}{path}"
    last_err = None
    attempts = max(1, len(_KEYS))
    for _ in range(attempts):
        key = current_key()
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        log(f"[*] POST {path} key={key[:10]}...")
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=timeout)
        except requests.RequestException as e:
            last_err = e
            next_key()
            continue
        if r.status_code == 200:
            return r.json()
        if r.status_code == 429 and len(_KEYS) > 1:
            log("[!] 429 rate limit — rotate key")
            next_key()
            continue
        raise RuntimeError(f"Mistral {path} HTTP {r.status_code}: {r.text[:500]}")
    raise RuntimeError(f"Mistral request failed: {last_err}")


def ocr_image(path: Path) -> dict:
    data = b64_file(path)
    mt = mime_for(path)
    payload = {
        "model": OCR_MODEL,
        "document": {
            "type": "image_url",
            "image_url": f"data:{mt};base64,{data}",
        },
    }
    return mistral_post("/ocr", payload)


def ocr_pdf_document(path: Path) -> dict:
    """Whole-PDF OCR (faster). Still render images for audit trail when requested."""
    data = b64_file(path)
    payload = {
        "model": OCR_MODEL,
        "document": {
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{data}",
        },
    }
    return mistral_post("/ocr", payload)


def pages_markdown_from_ocr(ocr: dict) -> str:
    pages = ocr.get("pages") or []
    chunks = []
    for i, p in enumerate(pages, 1):
        md = (p.get("markdown") or p.get("text") or "").strip()
        if not md:
            continue
        chunks.append(f"<!-- page {i} -->\n{md}")
    if chunks:
        return "\n\n---\n\n".join(chunks)
    # fallback shapes
    if isinstance(ocr.get("text"), str):
        return ocr["text"]
    return json.dumps(ocr, ensure_ascii=False, indent=2)


def chat_complete(
    messages: list[dict],
    model: str,
    *,
    use_orfree: bool = False,
    temperature: float = 0.1,
    max_tokens: int = 8192,
) -> str:
    if use_orfree:
        base = ORFREE_BASE
        key = (
            os.environ.get("ORFREE_API_KEY")
            or os.environ.get("NANOBOT_ORFREE_KEY")
            or os.environ.get("NINEROUTER_KEY")
            or "sk-local"
        )
        url = f"{base}/chat/completions"
    else:
        key = current_key()
        url = f"{MISTRAL_URL}/chat/completions"

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    log(f"[*] organize model={model} via={'orfree' if use_orfree else 'mistral'}")
    r = requests.post(url, headers=headers, json=payload, timeout=180)
    if r.status_code != 200:
        raise RuntimeError(f"chat HTTP {r.status_code}: {r.text[:500]}")
    data = r.json()
    return data["choices"][0]["message"]["content"]


ORGANIZE_SYSTEM = """Bạn là biên tập viên tài liệu kỹ thuật (ưu tiên biên bản / giấy tờ thiết bị y tế tiếng Việt).
Nhiệm vụ: nhận markdown thô từ OCR và sắp xếp lại cho rõ ràng, đúng cấu trúc.

Quy tắc:
- Giữ nguyên mọi số liệu, serial, ngày tháng, tên thiết bị, kết luận — không bịa thêm.
- Sửa lỗi OCR rõ ràng (ký tự lộn, khoảng trắng) khi chắc chắn.
- Dùng markdown: heading ##/###, bảng khi phù hợp, list gạch đầu dòng.
- Giữ thứ tự trang nếu có; đánh dấu rõ nếu nội dung mơ hồ / không đọc được.
- Không thêm lời chào, không giải thích quy trình — chỉ xuất bản markdown đã chỉnh.
- Nếu input đã hợp lý, chỉ chỉnh nhẹ format, không viết lại dài dòng.
"""


def organize_markdown(raw_md: str, model: str, use_orfree: bool, hint: str | None) -> str:
    user = "Sắp xếp lại nội dung OCR sau thành markdown sạch, logic:\n\n"
    if hint:
        user += f"Gợi ý ngữ cảnh: {hint}\n\n"
    user += raw_md
    # cap very long OCR
    if len(user) > 120_000:
        user = user[:120_000] + "\n\n[...truncated...]"
    return chat_complete(
        [
            {"role": "system", "content": ORGANIZE_SYSTEM},
            {"role": "user", "content": user},
        ],
        model=model,
        use_orfree=use_orfree,
    )


def process(
    input_path: Path,
    out_dir: Path,
    *,
    dpi: int,
    organize: bool,
    organize_model: str,
    use_orfree: bool,
    ocr_mode: str,
    hint: str | None,
) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    images_dir = out_dir / "images"
    images_dir.mkdir(exist_ok=True)

    suffix = input_path.suffix.lower()
    is_pdf = suffix == ".pdf"
    image_paths: list[Path] = []

    if is_pdf:
        image_paths = render_pdf_to_images(input_path, images_dir, dpi=dpi)
        log(f"[*] Rendered {len(image_paths)} page image(s)")
    else:
        image_paths = [normalize_image(input_path, images_dir)]
        log(f"[*] Image ready: {image_paths[0]}")

    ocr_raw_path = out_dir / "ocr_raw.json"
    ocr_md_path = out_dir / "ocr_raw.md"
    final_md_path = out_dir / "organized.md"

    if is_pdf and ocr_mode == "document":
        ocr = ocr_pdf_document(input_path)
    elif ocr_mode == "document" and not is_pdf:
        # single image still uses image API
        ocr = ocr_image(image_paths[0])
    else:
        # per-page image OCR then merge
        merged_pages = []
        full = {"pages": merged_pages, "source": "per-image"}
        for i, img in enumerate(image_paths, 1):
            log(f"[*] OCR image {i}/{len(image_paths)}: {img.name}")
            part = ocr_image(img)
            pages = part.get("pages") or []
            if pages:
                for p in pages:
                    p = dict(p)
                    p["_source_image"] = img.name
                    p["_page_index"] = i
                    merged_pages.append(p)
            else:
                md = part.get("markdown") or part.get("text") or ""
                merged_pages.append(
                    {
                        "markdown": md,
                        "_source_image": img.name,
                        "_page_index": i,
                    }
                )
            (out_dir / f"ocr_page_{i:03d}.json").write_text(
                json.dumps(part, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        ocr = full

    ocr_raw_path.write_text(json.dumps(ocr, ensure_ascii=False, indent=2), encoding="utf-8")
    raw_md = pages_markdown_from_ocr(ocr)
    ocr_md_path.write_text(raw_md + "\n", encoding="utf-8")
    log(f"[*] OCR markdown: {len(raw_md)} chars → {ocr_md_path}")

    organized = raw_md
    if organize:
        organized = organize_markdown(raw_md, organize_model, use_orfree, hint)
        final_md_path.write_text(organized.rstrip() + "\n", encoding="utf-8")
        log(f"[*] Organized → {final_md_path}")
    else:
        shutil.copy2(ocr_md_path, final_md_path)

    meta = {
        "input": str(input_path.resolve()),
        "out_dir": str(out_dir.resolve()),
        "images": [str(p) for p in image_paths],
        "ocr_model": OCR_MODEL,
        "organize": organize,
        "organize_model": organize_model if organize else None,
        "organize_via": ("orfree" if use_orfree else "mistral") if organize else None,
        "files": {
            "ocr_raw_json": str(ocr_raw_path),
            "ocr_raw_md": str(ocr_md_path),
            "organized_md": str(final_md_path),
        },
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta


def main() -> int:
    ap = argparse.ArgumentParser(description="PDF/image → OCR → organize (mistral-small-2603)")
    ap.add_argument("input", type=Path, help="PDF or image file")
    ap.add_argument("-o", "--out-dir", type=Path, default=None, help="Output directory")
    ap.add_argument("--dpi", type=int, default=200, help="PDF render DPI (default 200)")
    ap.add_argument(
        "--ocr-mode",
        choices=("document", "images"),
        default="document",
        help="document=whole PDF OCR API; images=OCR each rendered page",
    )
    ap.add_argument("--no-organize", action="store_true", help="Skip organize step")
    ap.add_argument(
        "--organize-model",
        default=DEFAULT_ORGANIZE_MODEL,
        help=f"Chat model for organize (default {DEFAULT_ORGANIZE_MODEL})",
    )
    ap.add_argument(
        "--via-orfree",
        action="store_true",
        help="Run organize via 9router/orfree base (ORFREE_BASE)",
    )
    ap.add_argument("--hint", default=None, help="Optional context for organizer (e.g. biên bản kiểm định)")
    args = ap.parse_args()

    inp = args.input.expanduser().resolve()
    if not inp.is_file():
        log(f"Not a file: {inp}")
        return 2

    out = args.out_dir
    if out is None:
        out = Path.cwd() / f"{inp.stem}_ocr_org"
    out = out.expanduser().resolve()

    try:
        meta = process(
            inp,
            out,
            dpi=args.dpi,
            organize=not args.no_organize,
            organize_model=args.organize_model,
            use_orfree=args.via_orfree,
            ocr_mode=args.ocr_mode,
            hint=args.hint,
        )
    except Exception as e:
        log(f"ERROR: {e}")
        return 1

    print(json.dumps(meta, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
