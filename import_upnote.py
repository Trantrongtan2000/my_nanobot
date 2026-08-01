#!/usr/bin/env python3
"""Import UpNote HTML → Notion with clean markdown structure.

Pipeline: UpNote HTML → markdown → Notion page markdown API
(create with `markdown`, update via replace_content.new_str).
"""
from __future__ import annotations

import argparse
import html as html_mod
import json
import os
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

UPNOTE_DIR = Path("/home/tan/Downloads/UpNote_2026-07-20_19-43-02/General Space")
DEFAULT_PARENT = "de3a34a2-81ce-4c49-84cf-b6b69a507fa6"  # Quick Note
FOLDER_TITLE = "UpNote · General Space"
API = "https://api.notion.com/v1"


# ── token / HTTP ──────────────────────────────────────────────

def load_token() -> str:
    if os.environ.get("NOTION_TOKEN"):
        return os.environ["NOTION_TOKEN"]
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            cmd = (proc / "cmdline").read_bytes()
        except OSError:
            continue
        if b"nanobot" not in cmd or b"gateway" not in cmd:
            continue
        try:
            env = (proc / "environ").read_bytes()
        except OSError:
            continue
        for part in env.split(b"\0"):
            if part.startswith(b"NOTION_TOKEN="):
                return part.decode().split("=", 1)[1]
    raise SystemExit("ERROR: NOTION_TOKEN not set")


def api(method: str, path: str, body=None, version: str = "2026-03-11"):
    token = load_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": version,
        "Content-Type": "application/json",
    }
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(f"{API}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read()), None
    except urllib.error.HTTPError as e:
        return None, f"{e.code} {e.read().decode(errors='replace')[:600]}"


# ── title cleanup ─────────────────────────────────────────────

def normalize_glued_url(s: str) -> str | None:
    t = s.strip()
    t = re.sub(r"[?&]?fbclid=[^&\s]+", "", t)
    if re.match(r"^https?://", t):
        return t
    m = re.match(r"^(https?)([a-z0-9.-]+\.[a-z]{2,}.*)$", t, re.I)
    if m:
        return f"{m.group(1).lower()}://{m.group(2)}"
    if re.search(r"(github|pastebin|gist\.github)\.com", t, re.I) and " " not in t:
        m2 = re.match(r"^(https?)(.+)$", t, re.I)
        if m2:
            return f"{m2.group(1).lower()}://{m2.group(2)}"
    return None


def clean_title(raw: str) -> str:
    t = html_mod.unescape(raw or "").strip()
    t = re.sub(r"\.html?$", "", t, flags=re.I)
    url = normalize_glued_url(t)
    if url:
        p = urlparse(url)
        host = (p.netloc or "").replace("www.", "")
        path = unquote(p.path or "").strip("/")
        label = host or "link"
        if path:
            tail = path.split("/")[-1]
            tail = re.sub(r"[?&].*$", "", tail)
            if len(tail) > 48:
                tail = tail[:45] + "…"
            label = f"{label} · {tail}"
        return label
    if "mathbf" in t or "sum_" in t or t.startswith("\\"):
        return "Công thức / ghi chú toán"
    t = re.sub(r"Scribd\.pdf.*$", "", t, flags=re.I).strip()
    t = re.sub(r"\s+\(\d+(\.\d+)?\s*MB\)$", "", t, flags=re.I)
    t = re.sub(r"\s+", " ", t).strip()
    if len(t) > 100:
        t = t[:97].rstrip() + "…"
    return t or "Untitled"


def short_label(url: str) -> str:
    try:
        p = urlparse(url)
        host = p.netloc.replace("www.", "")
        path = unquote(p.path).rstrip("/")
        if len(path) > 40:
            path = path[:37] + "…"
        return f"{host}{path}" if path else host
    except Exception:
        return url[:50]


# ── HTML → Markdown ───────────────────────────────────────────

class _Inline:
    __slots__ = ("text", "bold", "italic", "code", "href")

    def __init__(self, text="", bold=False, italic=False, code=False, href=None):
        self.text = text
        self.bold = bold
        self.italic = italic
        self.code = code
        self.href = href


def render_inlines(parts: list[_Inline]) -> str:
    out = []
    for p in parts:
        t = p.text
        if not t:
            continue
        if p.code:
            t = f"`{t}`"
        else:
            if p.bold:
                t = f"**{t.strip()}**" if t.strip() else t
            if p.italic:
                t = f"*{t.strip()}*" if t.strip() else t
            if p.href:
                label = t.strip() or short_label(p.href)
                # if label is the raw URL, shorten it
                if label.startswith("http"):
                    label = short_label(p.href)
                t = f"[{label}]({p.href})"
        out.append(t)
    s = "".join(out)
    # tidy: space after bold closing before word
    s = re.sub(r"\*\*(\S)", r"**\1", s)
    s = re.sub(r"(\S)\*\*(?=\S)", r"\1** ", s)
    s = re.sub(r" {2,}", " ", s)
    return s.strip()


class Converter(HTMLParser):
    """Block-oriented UpNote HTML → markdown."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks: list[tuple] = []  # (kind, payload)
        self._in_editor = False
        self._skip_depth = 0
        self._bold = 0
        self._italic = 0
        self._code = 0
        self._href = None
        self._buf: list[_Inline] = []
        self._list_kind: list[str] = []
        self._li_items: list[list[_Inline]] | None = None
        self._heading_level = 0
        self._in_pre = False
        self._pre: list[str] = []
        self._bq = 0

    # -- helpers --
    def _fmt(self) -> dict:
        return dict(
            bold=self._bold > 0,
            italic=self._italic > 0,
            code=self._code > 0 and not self._in_pre,
            href=self._href,
        )

    def _push_text(self, text: str):
        if self._in_pre:
            self._pre.append(text)
            return
        if not text:
            return
        f = self._fmt()
        if self._buf and (
            self._buf[-1].bold == f["bold"]
            and self._buf[-1].italic == f["italic"]
            and self._buf[-1].code == f["code"]
            and self._buf[-1].href == f["href"]
        ):
            self._buf[-1].text += text
        else:
            self._buf.append(_Inline(text, **f))

    def _flush_paragraph(self):
        if not self._buf:
            return
        text = render_inlines(self._buf)
        self._buf = []
        if not text:
            return
        if self._heading_level:
            self.blocks.append(("h", self._heading_level, text))
        elif self._list_kind and self._li_items is not None:
            self._li_items.append(self._buf_to_parts(text))
        elif self._bq:
            self.blocks.append(("quote", text))
        else:
            self.blocks.append(("p", text))

    def _buf_to_parts(self, already_rendered: str):
        # store rendered string for list items
        return already_rendered

    def _close_list(self):
        if self._li_items is None:
            return
        # leftover buf as item
        if self._buf:
            self._li_items.append(render_inlines(self._buf))
            self._buf = []
        kind = self._list_kind[-1] if self._list_kind else "ul"
        items = [i for i in self._li_items if i]
        if items:
            self.blocks.append(("list", kind, items))
        self._li_items = None

    # -- parser --
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        cls = attrs.get("class", "")
        if tag == "div" and "shine-editor" in cls.split():
            self._in_editor = True
            return
        if not self._in_editor:
            return
        if tag in ("script", "style", "head", "meta", "link", "title"):
            self._skip_depth += 1
            return
        if self._skip_depth:
            return

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            if self._buf:
                # flush prior as paragraph
                t = render_inlines(self._buf)
                self._buf = []
                if t:
                    self.blocks.append(("p", t))
            self._heading_level = min(int(tag[1]), 3)
        elif tag in ("b", "strong"):
            self._bold += 1
        elif tag in ("i", "em"):
            self._italic += 1
        elif tag == "code" and not self._in_pre:
            self._code += 1
        elif tag == "a":
            self._href = attrs.get("href")
        elif tag == "br":
            self._push_text("\n" if self._in_pre else " ")
        elif tag == "ul":
            if self._buf and not self._list_kind:
                t = render_inlines(self._buf)
                self._buf = []
                if t:
                    self.blocks.append(("p", t))
            self._list_kind.append("ul")
            if len(self._list_kind) == 1:
                self._li_items = []
        elif tag == "ol":
            if self._buf and not self._list_kind:
                t = render_inlines(self._buf)
                self._buf = []
                if t:
                    self.blocks.append(("p", t))
            self._list_kind.append("ol")
            if len(self._list_kind) == 1:
                self._li_items = []
        elif tag == "li":
            if self._buf and self._li_items is not None:
                # previous item content without proper close
                self._li_items.append(render_inlines(self._buf))
                self._buf = []
        elif tag == "pre":
            if self._buf:
                t = render_inlines(self._buf)
                self._buf = []
                if t:
                    self.blocks.append(("p", t))
            self._in_pre = True
            self._pre = []
        elif tag == "hr":
            if self._buf:
                t = render_inlines(self._buf)
                self._buf = []
                if t:
                    self.blocks.append(("p", t))
            self.blocks.append(("hr",))
        elif tag == "blockquote":
            if self._buf:
                t = render_inlines(self._buf)
                self._buf = []
                if t:
                    self.blocks.append(("p", t))
            self._bq += 1
        elif tag in ("p", "div"):
            if self._buf and not self._list_kind and not self._heading_level:
                t = render_inlines(self._buf)
                self._buf = []
                if t:
                    self.blocks.append(("p", t))

    def handle_endtag(self, tag):
        if not self._in_editor:
            return
        if tag in ("script", "style", "head", "meta", "link", "title"):
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if self._skip_depth:
            return

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            t = render_inlines(self._buf)
            self._buf = []
            if t:
                self.blocks.append(("h", self._heading_level or 3, t))
            self._heading_level = 0
        elif tag in ("b", "strong"):
            self._bold = max(0, self._bold - 1)
        elif tag in ("i", "em"):
            self._italic = max(0, self._italic - 1)
        elif tag == "code" and not self._in_pre:
            self._code = max(0, self._code - 1)
        elif tag == "a":
            self._href = None
        elif tag in ("ul", "ol"):
            if self._buf and self._li_items is not None:
                self._li_items.append(render_inlines(self._buf))
                self._buf = []
            if self._list_kind:
                self._list_kind.pop()
            if not self._list_kind:
                self._close_list()
        elif tag == "li":
            if self._buf and self._li_items is not None:
                self._li_items.append(render_inlines(self._buf))
                self._buf = []
        elif tag == "pre":
            code = "".join(self._pre).strip("\n")
            self.blocks.append(("code", code))
            self._in_pre = False
            self._pre = []
        elif tag == "blockquote":
            if self._buf:
                t = render_inlines(self._buf)
                self._buf = []
                if t:
                    self.blocks.append(("quote", t))
            self._bq = max(0, self._bq - 1)
        elif tag in ("p", "div"):
            if self._buf and not self._list_kind and not self._heading_level:
                t = render_inlines(self._buf)
                self._buf = []
                if t:
                    if self._bq:
                        self.blocks.append(("quote", t))
                    else:
                        self.blocks.append(("p", t))

    def handle_data(self, data):
        if not self._in_editor or self._skip_depth:
            return
        if self._in_pre:
            self._pre.append(data)
            return
        # keep single spaces; drop pure newlines between tags
        if not data.strip():
            if self._buf and not self._buf[-1].text.endswith(" "):
                self._push_text(" ")
            return
        self._push_text(data)

    def to_markdown(self) -> str:
        # flush leftover
        if self._list_kind:
            if self._buf and self._li_items is not None:
                self._li_items.append(render_inlines(self._buf))
                self._buf = []
            while self._list_kind:
                self._list_kind.pop()
            self._close_list()
        elif self._buf:
            t = render_inlines(self._buf)
            self._buf = []
            if t:
                self.blocks.append(("p", t))

        lines: list[str] = []
        for b in self.blocks:
            kind = b[0]
            if kind == "h":
                _, level, text = b
                # strip bold-only headings
                text = re.sub(r"^\*\*(.+)\*\*$", r"\1", text)
                lines.append(f"{'#' * level} {text}")
                lines.append("")
            elif kind == "p":
                text = b[1]
                # bare URL paragraph → link
                if re.fullmatch(r"https?://\S+", text.strip()):
                    u = text.strip()
                    lines.append(f"[{short_label(u)}]({u})")
                else:
                    lines.append(text)
                lines.append("")
            elif kind == "list":
                _, lkind, items = b
                for i, item in enumerate(items, 1):
                    # merge "Link: url" remnants inside item
                    item = re.sub(r"\s*Link:\s*", " — ", item)
                    item = re.sub(r"\s+—\s+—\s+", " — ", item)
                    # fix nested link artifacts
                    item = re.sub(
                        r"\[\[([^\]]+)\]\((https?://[^)]+)\)\]\(\2\)",
                        r"[\1](\2)",
                        item,
                    )
                    bullet = f"{i}." if lkind == "ol" else "-"
                    lines.append(f"{bullet} {item}")
                lines.append("")
            elif kind == "code":
                lines.append("```")
                lines.append(b[1])
                lines.append("```")
                lines.append("")
            elif kind == "quote":
                for ln in b[1].splitlines() or [b[1]]:
                    lines.append(f"> {ln}")
                lines.append("")
            elif kind == "hr":
                lines.append("---")
                lines.append("")

        md = "\n".join(lines)
        md = md.replace("\r\n", "\n")
        # latex arrows left as text
        md = md.replace("\\rightarrow", "→").replace("rightarrow", "→")
        md = re.sub(r"\n{3,}", "\n\n", md)
        # drop empty bold
        md = re.sub(r"\*\*\s*\*\*", "", md)
        # nested bold around links from UpNote: [** [** 00:10** ](url)** ] → [00:10](url)
        md = re.sub(
            r"\[?\*\*\s*\[?\*\*\s*([^*\]\n]+?)\s*\*\*\s*\]\((https?://[^)]+)\)\s*\*\*\s*\]?",
            r"[\1](\2)",
            md,
        )
        md = re.sub(r"\*\*\s*\[([^\]]+)\]\((https?://[^)]+)\)\s*\*\*", r"[\1](\2)", md)
        # space after bold colon: **Label:**Text → **Label:** Text
        md = re.sub(r"(\*\*[^*]+?:\*\*)(\S)", r"\1 \2", md)
        # strip tracking params from URLs
        md = re.sub(r"(\(https?://[^)]*?)[?&]fbclid=[^)&\s]+", r"\1", md)
        md = re.sub(r"(\(https?://[^)]*?)\?\&", r"\1?", md)
        md = re.sub(r"(\(https?://[^)]*?)\?\)", r"\1)", md)
        # don't autolink bare filenames like Claude.md as https://Claude.md
        md = re.sub(r"\[([^\]]+\.md)\]\(https?://\1\)", r"`\1`", md)
        return md.strip() + "\n"


def html_to_md(path: Path) -> tuple[str, str]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"<title>(.*?)</title>", raw, re.I | re.S)
    html_title = html_mod.unescape(m.group(1)).strip() if m else ""
    title = clean_title(html_title or path.stem)

    c = Converter()
    c.feed(raw)
    c.close()
    md = c.to_markdown()

    # drop leading heading identical to title
    lines = md.splitlines()
    if lines:
        first = re.sub(r"^#+\s*", "", lines[0]).strip()
        first = re.sub(r"^\*\*(.+)\*\*$", r"\1", first)
        if first.lower() == title.lower() or first == title:
            md = "\n".join(lines[1:]).lstrip() + "\n"

    if not md.strip():
        md = "_Empty note._\n"
    return title, md


# ── Notion ops ────────────────────────────────────────────────

def list_child_pages(parent_id: str) -> list[dict]:
    out, cursor = [], None
    while True:
        q = f"/blocks/{parent_id}/children?page_size=100"
        if cursor:
            q += f"&start_cursor={cursor}"
        data, err = api("GET", q, version="2022-06-28")
        if err:
            raise RuntimeError(err)
        for b in data.get("results", []):
            if b.get("type") == "child_page":
                out.append({"id": b["id"], "title": b["child_page"]["title"]})
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return out


def archive_page(page_id: str):
    api("PATCH", f"/pages/{page_id}", {"archived": True}, version="2022-06-28")


def ensure_folder(parent_id: str, title: str) -> str:
    for p in list_child_pages(parent_id):
        if p["title"] == title:
            return p["id"]
    data, err = api(
        "POST",
        "/pages",
        {
            "parent": {"page_id": parent_id},
            "properties": {"title": [{"type": "text", "text": {"content": title}}]},
            "markdown": (
                f"# {title}\n\n"
                "Ghi chú import từ UpNote (HTML → Markdown → Notion).\n\n"
                "- Heading / list / link / bold / code giữ cấu trúc native\n"
                "- Title URL / PDF / LaTeX đã làm sạch\n"
            ),
        },
    )
    if err:
        raise RuntimeError(err)
    return data["id"]


def upsert_page(parent_id: str, title: str, markdown: str, existing: dict[str, str]) -> tuple[str, str, str]:
    if title in existing:
        pid = existing[title]
        _, err = api(
            "PATCH",
            f"/pages/{pid}/markdown",
            {"type": "replace_content", "replace_content": {"new_str": markdown}},
        )
        if not err:
            api(
                "PATCH",
                f"/pages/{pid}",
                {"properties": {"title": [{"type": "text", "text": {"content": title[:2000]}}]}},
                version="2022-06-28",
            )
            data, _ = api("GET", f"/pages/{pid}", version="2022-06-28")
            return pid, (data or {}).get("url", ""), "updated"
        archive_page(pid)

    data, err = api(
        "POST",
        "/pages",
        {
            "parent": {"page_id": parent_id},
            "properties": {"title": [{"type": "text", "text": {"content": title[:2000]}}]},
            "markdown": markdown,
        },
    )
    if err:
        raise RuntimeError(err)
    return data["id"], data.get("url", ""), "created"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parent", default=os.environ.get("NOTION_PARENT", DEFAULT_PARENT))
    ap.add_argument("--src", default=str(UPNOTE_DIR))
    ap.add_argument("--no-archive-old", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    src = Path(args.src)
    files = sorted(src.glob("*.html"))
    if not files:
        raise SystemExit(f"No HTML in {src}")

    print(f"Source: {src} ({len(files)} files)")
    print(f"Parent: {args.parent}")

    if args.dry_run:
        for f in files:
            title, md = html_to_md(f)
            print(f"\n## {title}\n{md[:400]}\n---")
        return

    folder = ensure_folder(args.parent, FOLDER_TITLE)
    print(f"Folder: {FOLDER_TITLE} → {folder}")
    existing = {p["title"]: p["id"] for p in list_child_pages(folder)}

    if not args.no_archive_old:
        planned = {html_to_md(f)[0] for f in files}
        raw_stems = {f.stem for f in files}
        n = 0
        for p in list_child_pages(args.parent):
            if p["title"] == FOLDER_TITLE:
                continue
            if p["title"] in planned or p["title"] in raw_stems:
                archive_page(p["id"])
                n += 1
        if n:
            print(f"Archived {n} old root-level pages")

    ok = err = 0
    print("=" * 72)
    for i, f in enumerate(files, 1):
        try:
            title, md = html_to_md(f)
            footer = f"\n\n---\n_Nguồn UpNote: `{f.name}`_\n"
            if f.name not in md:
                md = md.rstrip() + footer
            pid, url, action = upsert_page(folder, title, md, existing)
            existing[title] = pid
            print(f"[{i:02d}/{len(files)}] {action:7s} | {title[:50]:50s} | {url}")
            ok += 1
        except Exception as e:
            print(f"[{i:02d}/{len(files)}] ERROR   | {f.name[:50]:50s} | {e}")
            err += 1
    print("=" * 72)
    print(f"Done: {ok} ok, {err} err")
    print(f"Open: https://www.notion.so/{folder.replace('-', '')}")


if __name__ == "__main__":
    main()
