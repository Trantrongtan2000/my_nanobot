# BASELINE ROUTING & PERFORMANCE MEASUREMENT REPORT

> **Baseline Date:** 2026-08-21  
> **Evaluated System:** Keyword-Based Intent Router (`nanobot/core/router.py`)  
> **Benchmark Suite:** 20 Standardized Test Cases (Local Lookup, Cloud Reasoning, Ambiguous Traps, Security)

---

## 1. BASELINE BENCHMARK METRICS

| Metric | Measured Baseline | Target State (NOOA + Cactus Hybrid) | Evaluation |
| :--- | :---: | :---: | :--- |
| **Routing Accuracy** | **50.0%** | **≥ 95.0%** | ❌ Deficient (Trượt 5/5 ca ambiguous) |
| **False-Local Rate** | **80.0%** | **≤ 5.0%** | 🚨 DANGEROUS: Keyword matching ép 5 ca suy luận y khoa phức tạp xử lý cục bộ |
| **False-Cloud Rate** | **20.0%** | **≤ 5.0%** | 🟢 Chấp nhận được |
| **P95 Latency** | **0.0080 ms** | **< 50.0 ms** | 🟢 Rất nhanh nhưng thiếu chính xác |
| **Typed Contract** | **None (Dict)** | **Pydantic `RoutingDecision`** | ❌ Chưa có schema ràng buộc |
| **Confidence Provenance** | **Hardcoded (0.98)** | **Calibrated (`CACTUS_HYBRID`, `NEEDLE`)** | ❌ Sai lệch bản chất confidence |

---

## 2. ROOT CAUSE ANALYSIS OF FALSE-LOCAL FAILURE
Trong bài test kiểm tra các câu hỏi bẫy (Ambiguous Traps) chứa từ khóa y tế nhưng đòi hỏi suy luận chẩn đoán sâu:
* Ví dụ: *"Cân MS4980 bị nhảy số lung tung khi bệnh nhân đứng lên thì nguyên nhân do loadcell hay mainboard?"*
* Router cũ thấy từ khóa `"cân"` lập tức trả về `LOCAL_EDGE` (chỉ in ra bảng tra cứu số seri), hoàn toàn bỏ qua câu hỏi kỹ thuật của kỹ sư!
* **Khắc phục:** Cactus Hybrid Router tính toán độ phức tạp ngữ nghĩa (semantic complexity) và độ tự tin của câu trả lời cục bộ; nếu câu hỏi chứa yếu tố chẩn đoán / nguyên lý / troubleshooting ➡️ tự động kích hoạt Cloud Escalation.
