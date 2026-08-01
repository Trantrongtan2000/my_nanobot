---
name: code-agent-rules
description: Code agent workflow — understand, plan, implement, verify. Surgical scope, root-cause fixes, existing conventions. Use when writing or modifying code.
---

# Code Agent Rules

## Workflow

Understand → Plan → Implement → Verify.

## Principles

- Surgical scope: minimal diffs, no gold-plating, no unrequested refactoring or surrounding cleanup.
- Diagnose before retry: inspect full error output before attempting a fix. Never retry blindly; don't abandon after one fail without diagnosis.
- Match existing project conventions. Never assume library availability.
- Prefer edit over create. Prefer repo patterns over new abstractions.
- Evidence before claim done: run linter/tests or read back modified file before declaring task completed. If you can't verify, say so.
- Comments: only constraints the code cannot show — never narrate the next line or PR justification.
- Bug fix = root cause. Grep every caller of touched functions.
- Never invent or guess URLs. Only use URLs from user, tools, or high confidence.
- Never commit secrets. Don't skip hooks / force-push unless user explicitly asks.

## Project Anchors

- MEIMS modules: QT.04 Commissioning, QT.05 Incident, QT.06 Maintenance, QT.07 Disposal, QT.08 Transfer, Auth/RACI.
- OCR batch BV Q7: large PDF corpus + `mistral_pdf_to_md`; check progress/manifest before restarting batches.
- Do not invent inventory counts, PO numbers, or regulatory status.
