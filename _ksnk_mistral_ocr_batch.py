# -*- coding: utf-8 -*-
"""Batch Mistral OCR for KSNK main PDFs → wiki/raw/ksnk/ocr + refresh concepts."""
from __future__ import annotations

import base64
import json
import os
import re
import sys
import time
import unicodedata
from datetime import date
from pathlib import Path

import requests

WS = Path.home() / ".nanobot" / "workspace"
WIKI = WS / "wiki"
RAW = WIKI / "raw" / "ksnk"
OCR_DIR = RAW / "ocr"
MANIFEST = OCR_DIR / "manifest.json"
MAINS = RAW / "mains_index.json"
CONCEPTS = WIKI / "concepts"
SYN = WIKI / "synthesis"
TODAY = date.today().isoformat()

MISTRAL_URL = os.environ.get("MISTRAL_API_URL", "https://api.mistral.ai/v1").rstrip("/")
OCR_MODEL = os.environ.get("MISTRAL_OCR_MODEL", "mistral-ocr-latest")

# Prefer document OCR; large PDFs may need page split
MAX_PDF_MB_DIRECT = 45  # safety under typical API limits
MAX_PAGES_FALLBACK = 40
DPI = 160


def load_dotenv():
    env = Path.home() / ".nanobot" / ".env"
    if not env.exists():
        return
    for ln in env.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#") or "=" not in ln:
            continue
        k, v = ln.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


def collect_keys() -> list[str]:
    keys = []
    for name in [
        "MISTRAL_API_KEY",
        "MISTRAL_API_KEY_2",
        "MISTRAL_API_KEY_3",
        "MISTRAL_API_KEY_4",
        "MISTRAL_API_KEY_5",
        "MISTRAL_API_KEY_6",
    ]:
        v = os.environ.get(name, "").strip()
        if v:
            keys.append(v)
    # also numbered beyond
    i = 2
    while True:
        v = os.environ.get(f"MISTRAL_API_KEY_{i}", "").strip()
        if not v:
            if i > 10:
                break
            i += 1
            continue
        if v not in keys:
            keys.append(v)
        i += 1
        if i > 20:
            break
    return keys


class KeyPool:
    def __init__(self, keys: list[str]):
        if not keys:
            raise SystemExit("No MISTRAL_API_KEY*")
        self.keys = keys
        self.i = 0
        self.disabled: set[int] = set()

    def current(self) -> str:
        for _ in range(len(self.keys)):
            if self.i not in self.disabled:
                return self.keys[self.i]
            self.i = (self.i + 1) % len(self.keys)
        raise RuntimeError("All Mistral keys disabled")

    def rotate(self, reason: str = ""):
        print(f"[key] rotate ({reason}) from #{self.i+1}", flush=True)
        self.i = (self.i + 1) % len(self.keys)

    def disable_current(self, reason: str):
        print(f"[key] disable #{self.i+1}: {reason}", flush=True)
        self.disabled.add(self.i)
        self.rotate("after disable")


def slugify(s: str) -> str:
    s = s.lower().strip().replace("đ", "d").replace("Đ", "d")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_")[:80]


def pages_markdown(ocr: dict) -> str:
    pages = ocr.get("pages") or []
    chunks = []
    for i, p in enumerate(pages, 1):
        md = (p.get("markdown") or p.get("text") or "").strip()
        if md:
            chunks.append(f"<!-- page {i} -->\n{md}")
    if chunks:
        return "\n\n---\n\n".join(chunks)
    if isinstance(ocr.get("text"), str):
        return ocr["text"]
    return ""


def ocr_request(pool: KeyPool, payload: dict, timeout: int = 300) -> dict:
    url = f"{MISTRAL_URL}/ocr"
    last = None
    for attempt in range(max(6, len(pool.keys) * 2)):
        key = pool.current()
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=timeout)
        except requests.RequestException as e:
            last = e
            pool.rotate(f"net {type(e).__name__}")
            time.sleep(2)
            continue
        if r.status_code == 200:
            return r.json()
        body = r.text[:400]
        if r.status_code in (401, 403):
            pool.disable_current(f"HTTP {r.status_code}")
            last = RuntimeError(body)
            continue
        if r.status_code == 429:
            pool.rotate("429")
            time.sleep(5)
            last = RuntimeError(body)
            continue
        if r.status_code >= 500:
            pool.rotate(f"HTTP {r.status_code}")
            time.sleep(3)
            last = RuntimeError(body)
            continue
        raise RuntimeError(f"OCR HTTP {r.status_code}: {body}")
    raise RuntimeError(f"OCR failed after retries: {last}")


def ocr_pdf_direct(pool: KeyPool, pdf: Path) -> dict:
    b64 = base64.b64encode(pdf.read_bytes()).decode("ascii")
    payload = {
        "model": OCR_MODEL,
        "document": {
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{b64}",
        },
    }
    return ocr_request(pool, payload, timeout=600)


def ocr_pdf_pages(pool: KeyPool, pdf: Path, max_pages: int = MAX_PAGES_FALLBACK) -> dict:
    import fitz

    doc = fitz.open(pdf)
    n = min(doc.page_count, max_pages)
    zoom = DPI / 72.0
    mat = fitz.Matrix(zoom, zoom)
    all_pages = []
    for i in range(n):
        pix = doc.load_page(i).get_pixmap(matrix=mat, alpha=False)
        png = pix.tobytes("png")
        b64 = base64.b64encode(png).decode("ascii")
        payload = {
            "model": OCR_MODEL,
            "document": {
                "type": "image_url",
                "image_url": f"data:image/png;base64,{b64}",
            },
        }
        print(f"  page {i+1}/{n}", flush=True)
        data = ocr_request(pool, payload, timeout=180)
        pages = data.get("pages") or []
        if pages:
            all_pages.extend(pages)
        elif data.get("text"):
            all_pages.append({"markdown": data["text"]})
        time.sleep(0.3)
    doc.close()
    return {"pages": all_pages}


def summarize(text: str) -> dict:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.startswith("<!--")]
    body = "\n".join(lines)
    purpose = scope = ""
    for key in ["Mục đích", "MỤC ĐÍCH", "1. Mục đích"]:
        if key.lower() in body.lower():
            idx = body.lower().find(key.lower())
            chunk = body[idx : idx + 600]
            m = re.search(
                r"mục đích[:\s]*(.+?)(?:\n\s*(?:\d+\.|ii\.|2\.|phạm vi|đối tượng)|$)",
                chunk,
                re.S | re.I,
            )
            if m:
                purpose = re.sub(r"\s+", " ", m.group(1)).strip(" :.-")[:500]
            break
    for key in ["Phạm vi", "PHẠM VI", "2. Phạm vi"]:
        if key.lower() in body.lower():
            idx = body.lower().find(key.lower())
            chunk = body[idx : idx + 500]
            m = re.search(
                r"phạm vi(?: áp dụng)?[:\s]*(.+?)(?:\n\s*(?:\d+\.|iii\.|3\.|tài liệu|định nghĩa)|$)",
                chunk,
                re.S | re.I,
            )
            if m:
                scope = re.sub(r"\s+", " ", m.group(1)).strip(" :.-")[:500]
            break
    steps = []
    for ln in lines:
        if re.match(r"^(\d+[\.\)]\s+|[-•]\s+)", ln) and len(ln) > 12:
            steps.append(ln[:220])
        if len(steps) >= 15:
            break
    refs = sorted(
        set(
            re.findall(
                r"(?:Thông tư|Nghị định|Quyết định|Luật|ISO|CDC|WHO|TT\s*/|NĐ\s*)[^\n]{0,80}",
                body,
                flags=re.I,
            )
        )
    )[:20]
    return {
        "purpose": purpose,
        "scope": scope,
        "steps": steps,
        "refs": refs,
        "chars": len(text),
        "has_text": len(text) > 200,
    }


def prefer_q7_qtvh(records: list[dict]) -> list[dict]:
    """Dedupe by code: prefer q7 + qtvh path."""

    def score(r):
        s = 0
        rel = r.get("rel", "").lower()
        if r.get("site") == "q7":
            s += 100
        if "qtvh" in rel:
            s += 50
        if "qtkt" in rel:
            s -= 30
        s += min(r.get("size_kb", 0) / 1000, 20)
        return s

    by = {}
    for r in records:
        code = r.get("code") or r["rel"]
        # normalize
        key = re.sub(r"^TA[25]\.", "", code.upper()).replace("QD", "QĐ")
        if key not in by or score(r) > score(by[key]):
            by[key] = r
    # process q7 first then others
    items = list(by.values())
    items.sort(key=lambda r: (0 if r.get("site") == "q7" else 1, r.get("code") or ""))
    return items


def load_manifest() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {"version": 1, "items": {}}


def save_manifest(m: dict):
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")


def out_name(rec: dict) -> str:
    return f"{rec['site']}_{slugify(rec['code'])}_{slugify(rec['title'])[:40]}.md"


def write_ocr_md(rec: dict, md: str, meta: dict, method: str) -> Path:
    OCR_DIR.mkdir(parents=True, exist_ok=True)
    path = OCR_DIR / out_name(rec)
    body = "\n".join(
        [
            "---",
            "type: source",
            f'title: "OCR {rec["code"]} — {rec["title"]}"',
            "status: draft",
            f"updated: {TODAY}",
            f'sources: ["{rec["rel"]}"]',
            "tags: [ksnk, mistral-ocr]",
            "---",
            "",
            f"# OCR {rec['code']} — {rec['title']}",
            "",
            f"- Site: {rec['site']}",
            f"- Source: `{rec['abs']}`",
            f"- Relative: `{rec['rel']}`",
            f"- Method: {method}",
            f"- Model: {OCR_MODEL}",
            f"- Chars: {meta['chars']}",
            "",
            "## Tóm tắt heuristic",
            "",
            f"- **Mục đích:** {meta['purpose'] or '_(chưa trích)_'}",
            f"- **Phạm vi:** {meta['scope'] or '_(chưa trích)_'}",
            "",
            "## Markdown OCR",
            "",
            md if md.strip() else "_[empty]_",
            "",
        ]
    )
    path.write_text(body, encoding="utf-8")
    return path


def update_concept(rec: dict, ocr_rel: str, md: str, meta: dict):
    key = re.sub(r"^TA[25]\.", "", rec["code"].upper()).replace("QD", "QĐ")
    # find concept
    hits = list(CONCEPTS.glob(f"*{slugify(key)}*.md"))
    if not hits:
        hits = list(CONCEPTS.glob("ksnk_*.md"))
        hits = [h for h in hits if key.replace(".", "_").lower() in h.name.lower() or key.lower() in h.read_text(encoding="utf-8")]
    if not hits:
        print(f"  [warn] no concept for {key}", flush=True)
        return
    # pick best match
    cf = hits[0]
    for h in hits:
        t = h.read_text(encoding="utf-8")
        if f"`{key}`" in t or rec["code"] in t:
            cf = h
            break
    text = cf.read_text(encoding="utf-8")
    marker = "## OCR Mistral (PDF chính)"
    if marker in text:
        pre = text.split(marker)[0].rstrip()
        # keep attachments section if after? attachments usually after summary
        # if OCR was in middle, drop until next ## Đính kèm or end
        rest = text.split(marker, 1)[1]
        if "## Đính kèm" in rest:
            rest = "## Đính kèm" + rest.split("## Đính kèm", 1)[1]
        elif "\n## " in rest[5:]:
            # find next top section after first line
            m = re.search(r"\n## ", rest)
            rest = rest[m.start() + 1 :] if m else ""
        else:
            rest = ""
        text = pre + "\n\n" + (rest if rest.startswith("##") else rest)
    section = [
        "",
        marker,
        "",
        f"- File OCR: `{ocr_rel}`",
        f"- Cập nhật: {TODAY}",
        "",
    ]
    if meta.get("purpose"):
        section += [f"**Mục đích (OCR):** {meta['purpose']}", ""]
    if meta.get("scope"):
        section += [f"**Phạm vi (OCR):** {meta['scope']}", ""]
    if meta.get("steps"):
        section += ["**Mục/bước gợi ý:**", ""]
        for st in meta["steps"][:12]:
            section.append(f"- {st}")
        section.append("")
    if meta.get("refs"):
        section += ["**Căn cứ nhắc trong OCR:**", ""]
        for rf in meta["refs"][:12]:
            section.append(f"- {rf}")
        section.append("")
    # embed truncated OCR
    section += ["### Trích OCR (rút gọn)", "", "```markdown", md[:6000], "```", ""]
    # insert after first ## Tóm tắt block if present, else before ## Đính kèm, else append
    if "## Đính kèm BK/BM/PL" in text:
        text = text.replace(
            "## Đính kèm BK/BM/PL",
            "\n".join(section) + "\n## Đính kèm BK/BM/PL",
            1,
        )
    else:
        text = text.rstrip() + "\n" + "\n".join(section) + "\n"
    # fix empty purpose note if we now have purpose
    if meta.get("purpose"):
        text = text.replace(
            "*Chưa trích được mục đích rõ (PDF scan/OCR yếu hoặc layout phức tạp). Xem extract thô.*",
            f"**Mục đích (từ OCR):** {meta['purpose']}",
        )
    cf.write_text(text, encoding="utf-8")
    print(f"  concept <- {cf.name}", flush=True)


def main():
    load_dotenv()
    # also accept keys passed only in this process via already-set env from parent
    keys = collect_keys()
    print(f"keys={len(keys)} model={OCR_MODEL}", flush=True)
    pool = KeyPool(keys)

    records = json.loads(MAINS.read_text(encoding="utf-8"))
    # only weak / all mains — OCR preferred set
    todo = prefer_q7_qtvh(records)
    # optional CLI filter: --q7-only --limit N --codes QT.02,QT.05
    args = sys.argv[1:]
    q7_only = "--q7-only" in args
    limit = None
    codes_filter = None
    if "--limit" in args:
        limit = int(args[args.index("--limit") + 1])
    if "--codes" in args:
        codes_filter = [
            c.strip().upper() for c in args[args.index("--codes") + 1].split(",") if c.strip()
        ]
    if q7_only:
        todo = [r for r in todo if r.get("site") == "q7"]
    if codes_filter:
        def match(r):
            c = r.get("code", "").upper()
            return any(f in c for f in codes_filter)

        todo = [r for r in todo if match(r)]
    if limit:
        todo = todo[:limit]

    manifest = load_manifest()
    items = manifest.setdefault("items", {})

    ok = fail = skip = 0
    for idx, rec in enumerate(todo, 1):
        code = rec["code"]
        abs_path = Path(rec["abs"])
        mid = f"{rec['site']}:{code}:{rec['rel']}"
        print(f"\n[{idx}/{len(todo)}] {code} {rec['size_kb']}KB", flush=True)
        if not abs_path.exists():
            print("  MISSING file", flush=True)
            fail += 1
            continue
        prev = items.get(mid)
        if prev and prev.get("status") == "ok" and Path(WS / "wiki" / prev.get("ocr_rel", "")).exists():
            print("  skip done", flush=True)
            skip += 1
            continue

        mb = abs_path.stat().st_size / 1e6
        method = "document_url"
        try:
            if mb <= MAX_PDF_MB_DIRECT:
                try:
                    data = ocr_pdf_direct(pool, abs_path)
                except Exception as e:
                    print(f"  direct fail: {e}; fallback pages", flush=True)
                    method = "pages_png"
                    data = ocr_pdf_pages(pool, abs_path)
            else:
                method = "pages_png"
                data = ocr_pdf_pages(pool, abs_path)
            md = pages_markdown(data)
            meta = summarize(md)
            if not meta["has_text"]:
                raise RuntimeError("OCR empty/weak")
            path = write_ocr_md(rec, md, meta, method)
            ocr_rel = f"raw/ksnk/ocr/{path.name}"
            update_concept(rec, ocr_rel, md, meta)
            items[mid] = {
                "status": "ok",
                "code": code,
                "site": rec["site"],
                "ocr_rel": ocr_rel,
                "method": method,
                "chars": meta["chars"],
                "updated": TODAY,
            }
            ok += 1
            save_manifest(manifest)
            print(f"  OK chars={meta['chars']} method={method}", flush=True)
        except Exception as e:
            items[mid] = {
                "status": "fail",
                "code": code,
                "error": str(e)[:300],
                "updated": TODAY,
            }
            save_manifest(manifest)
            fail += 1
            print(f"  FAIL {e}", flush=True)
            time.sleep(1)

    # hub note
    hub = SYN / "ksnk_quy_trinh_hub.md"
    if hub.exists():
        ht = hub.read_text(encoding="utf-8")
        note = (
            f"\n## OCR Mistral ({TODAY})\n\n"
            f"- Manifest: `raw/ksnk/ocr/manifest.json`\n"
            f"- Batch result: ok={ok} skip={skip} fail={fail} (this run)\n"
            f"- Model: `{OCR_MODEL}`\n"
        )
        if "## OCR Mistral" in ht:
            # replace section roughly
            ht = re.sub(
                r"\n## OCR Mistral \([^\)]*\)\n.*?(?=\n## |\Z)",
                note + "\n",
                ht,
                count=1,
                flags=re.S,
            )
        else:
            ht = ht.rstrip() + "\n" + note + "\n"
        hub.write_text(ht, encoding="utf-8")

    log_path = WIKI / "log.md"
    log = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    log += (
        f"\n## {TODAY} — Mistral OCR KSNK\n"
        f"- ok={ok} skip={skip} fail={fail}\n"
        f"- out: `raw/ksnk/ocr/`\n"
        f"- model: {OCR_MODEL}\n"
    )
    log_path.write_text(log, encoding="utf-8")

    print(json.dumps({"ok": ok, "skip": skip, "fail": fail, "todo": len(todo)}), flush=True)


if __name__ == "__main__":
    main()
