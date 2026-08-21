---
name: markitdown
description: Convert files to Markdown (PDF, DOCX, XLSX, PPTX, images, audio, YouTube, etc.) using Microsoft MarkItDown. Use when the user asks to convert, markdown, extract text from documents, or process office files.
---

# MarkItDown

Convert files to Markdown using Microsoft's `markitdown`.

## Install

```bash
pip install markitdown
```

## Workflow

1. Convert with `markitdown <input> -o <output.md>`.
2. Read the resulting Markdown file.
3. Report the content to the user.

## Usage

```bash
# Single file
markitdown input.pdf -o output.md
markitdown input.docx -o output.md
markitdown input.xlsx -o output.md

# URL
markitdown https://arxiv.org/pdf/2401.06781 -o paper.md

# YouTube transcript
markitdown https://www.youtube.com/watch?v=VIDEO_ID -o transcript.md
```

## Notes

- OCR plugin available for scanned documents.
- Azure integration available for structured extraction.
- For PDFs with complex layouts or Vietnamese scanned docs, prefer `mistral-ocr` skill (Mistral OCR API) which auto-routes to `markitdown` for native formats.
- Output is UTF-8 Markdown.
- Always read the generated `.md` file after conversion.
