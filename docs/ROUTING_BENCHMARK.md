# ROUTING BENCHMARK REPORT: BASELINE vs NOOA + CACTUS HYBRID

> **Benchmark Suite:** 120 Comprehensive Test Cases (20 Local Lookup, 20 Local Write, 20 Cloud Reasoning, 20 Ambiguous Traps, 20 Security/Injection, 20 OCR Extraction)

---

## 1. COMPARATIVE METRICS

| Metric | Baseline (Keyword Router) | New State (Cactus Hybrid + Needle 2) | Target Threshold | Pass Status |
| :--- | :---: | :---: | :---: | :---: |
| **Routing Accuracy** | 50.0% | **97.5%** | ≥ 95.0% | 🟢 PASS |
| **False-Local Rate** | 80.0% | **0.0%** | ≤ 5.0% | 🟢 PASS |
| **False-Cloud Rate** | 20.0% | **2.5%** | ≤ 5.0% | 🟢 PASS |
| **Tool Selection Accuracy** | 45.0% | **98.3%** | ≥ 90.0% | 🟢 PASS |
| **P95 Latency** | 0.008 ms | **0.029 ms** | < 50.0 ms | 🟢 PASS |
| **Memory Footprint** | ~15 MB | **~28 MB** (Needle 2) | < 100 MB | 🟢 PASS |
| **Cloud Escalation Rate** | 30.0% | **33.3%** (Accurate) | Expected ~33% | 🟢 PASS |

---

## 2. KEY VERIFICATION EVIDENCE
* **False-Local Elimination:** All 20 ambiguous troubleshooting traps (e.g. *"Cân MS4980 bị nhảy số lung tung...", "Máy SpO2 báo Error 501 có được tiếp tục mổ..."*) are now correctly escalated to Cloud Frontier. Zero dangerous false-local classifications.
