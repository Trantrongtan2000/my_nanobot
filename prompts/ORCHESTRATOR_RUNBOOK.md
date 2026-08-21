# ORCHESTRATOR & AGENT PIPELINE RUNBOOK

## Pipeline Thứ Tự Thực Thi Chuẩn:
```text
Role 3 (Security & Audit)
   ↓
Role 1 (Architecture & Inventory)
   ↓
Role 2 (OCR & 9Router Infrastructure)
   ↓
Automated Test Suite
   ↓
Final Integration & Release
```

## Tiêu Chuẩn Nghiệm Thu Cốt Lõi:
```text
NO CLAIM WITHOUT EVIDENCE

"Implemented"
    ↓
code exists
    ↓
import succeeds
    ↓
unit test passes
    ↓
integration/smoke test passes
    ↓
runtime path verified
    ↓
only then mark DONE
```
