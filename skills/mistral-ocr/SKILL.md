---
name: mistral-ocr
description: Unified skill for extracting text from PDFs, images, scanned documents (Vietnamese/multilingual), Word (.doc/.docx), Excel (.xlsx) using Mistral OCR API (with key rotation & auto-chunking), win32com, and markitdown.
---

# Mistral OCR & Document Processing Workflow

Unified skill to extract text and convert scanned documents (PDF, PNG, JPG), Word documents (`.doc`/`.docx`), and Excel spreadsheets (`.xlsx`) into clean Markdown or structured data.

## Features & Capabilities

1. **Mistral OCR API Integration**:
   - High-accuracy OCR for PDFs & images (especially Vietnamese with full diacritics).
   - Auto-chunking for large PDFs (>5MB or >15 pages) using `pymupdf`.
   - Automatic API Key rotation across `MISTRAL_KEYS` (semicolon-separated env var) handling 429/5xx errors.
   - Clean Markdown output compatible with downstream `markitdown` pipelines.
2. **Unified Document Conversion CLI**:
   - `mdconvert.py`: Auto-routes PDFs/images to Mistral OCR API, and office docs/HTML to native `markitdown`.
3. **Office Documents Support**:
   - Old Word files (`.doc` OLE format) via `win32com` / `olefile`.
   - Excel spreadsheets (`.xlsx`) via `openpyxl`.
   - Filling form tables in Word documents.

---

## Environment & Stack

| Tool / Script | Path / Location | Purpose |
|---|---|---|
| `mdconvert.py` | `C:\Users\tantt\.local\bin\mdconvert.py` | Unified CLI: Auto-routes PDF/image $\rightarrow$ Mistral OCR; else $\rightarrow$ `markitdown` |
| `mistral_ocr.py` | `C:\Users\tantt\.local\bin\mistral_ocr.py` | Low-level wrapper, API key rotation, PDF chunking |
| `pymupdf` (`fitz`) | Python site-packages | PDF page rendering & splitting for chunks |
| `win32com` | Python site-packages | Reading/manipulating legacy `.doc` files on Windows |
| `openpyxl` | Python site-packages | Reading `.xlsx` spreadsheets |

### API Key Configuration
Persist API keys as a semicolon-separated environment variable `MISTRAL_KEYS`:
```powershell
# PowerShell
$keys = 'key1;key2;key3;key4'
[Environment]::SetEnvironmentVariable('MISTRAL_KEYS', $keys, 'User')
```

---

## Usage Guide

### 1. Using Unified CLI (`mdconvert.py`)

```bash
# Single PDF / Image (Auto-routes PDF/image to Mistral OCR)
python C:\Users\tantt\.local\bin\mdconvert.py "C:\path\to\contract.pdf" -o "contract.md"

# URL input (Mistral fetches directly)
python C:\Users\tantt\.local\bin\mdconvert.py "https://arxiv.org/pdf/2401.06781" -o paper.md

# Force specific engine
python C:\Users\tantt\.local\bin\mdconvert.py file.txt --engine markitdown
python C:\Users\tantt\.local\bin\mdconvert.py file.pdf --engine ocr
```

### 2. Using Mistral OCR CLI Directly (`mistral_ocr.py`)

```bash
# Basic OCR to Markdown
python C:\Users\tantt\.local\bin\mistral_ocr.py "scan.png" --markitdown-format -o scan.md

# Manual chunk size for very dense/large PDFs (e.g. 5 pages per chunk)
python C:\Users\tantt\.local\bin\mistral_ocr.py big_contract.pdf --chunk-pages 5 --markitdown-format -o out.md
```

### 3. Batch Processing Folder of PDFs

```powershell
# PowerShell batch conversion
Get-ChildItem "C:\scanned_docs" -Recurse -Filter *.pdf | ForEach-Object {
    $out = $_.FullName -replace '\.pdf$', '.md'
    python C:\Users\tantt\.local\bin\mdconvert.py $_.FullName -o $out
}
```

---

## Python Code Recipes

### Recipe A: Direct API Integration (Urllib / Python stdlib)

```python
import os, base64, json, urllib.request
import fitz  # pymupdf

API_KEY = os.environ.get("MISTRAL_KEYS", "").split(";")[0]
ENDPOINT = "https://api.mistral.ai/v1/ocr"

def ocr_pdf_page(pdf_path, page_idx=0):
    doc = fitz.open(pdf_path)
    page = doc[page_idx]
    pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72), alpha=False)
    b64 = base64.b64encode(pix.tobytes("png")).decode()
    doc.close()

    payload = {
        "model": "mistral-ocr-latest",
        "document": {
            "type": "image_url",
            "image_url": f"data:image/png;base64,{b64}"
        }
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        res = json.loads(resp.read())
        return res.get("pages", [{}])[0].get("markdown", "")
```

### Recipe B: Reading Old Legacy `.doc` Files (Windows `win32com`)

```python
import win32com.client, os

path = r"C:\path\to\legacy_file.doc"
word = win32com.client.Dispatch("Word.Application")
word.Visible = False
doc = word.Documents.Open(os.path.abspath(path))

# Extract text content
text = doc.Content.Text

# Extract tables (Note: win32com indices start at 1)
for table in doc.Tables:
    for r in range(1, table.Rows.Count + 1):
        row_data = [table.Cell(r, c).Range.Text.strip() for c in range(1, table.Columns.Count + 1)]
        print(row_data)

doc.Close(False)
word.Quit()
```

### Recipe C: Processing `.xlsx` Spreadsheets

```python
import openpyxl

wb = openpyxl.load_workbook("path/to/spreadsheet.xlsx")
for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    for row in ws.iter_rows(values_only=True):
        vals = [str(c) if c is not None else "" for c in row]
        if any(v.strip() for v in vals):
            print(vals)
```

---

## Troubleshooting & Key Rules

| Symptom / Error | Cause | Solution |
|---|---|---|
| Output empty (0-2 bytes) | Request size exceeded Mistral limit | Pass `--chunk-pages 5` to process in smaller page batches |
| `HTTP 429` / Rate limit | API Key quota exceeded | Script automatically rotates to next key in `MISTRAL_KEYS` |
| Vietnamese characters broken | Invalid encoding when saving output | Always read/write files with `encoding='utf-8'` |
| `.doc` read error | Distinction between OLE `.doc` vs renamed `.docx` | Check header: `d0cf11e0` (OLE `.doc`) vs `504b0304` (ZIP/`.docx`) |
| Table cells off-by-one | `win32com` index base | `win32com` cell/row indices start at **1** (not 0) |