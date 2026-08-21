# CACTUS UPSTREAM RESEARCH & API VERIFICATION REPORT

> **Document Version:** 2.1.0 (Production Verified)  
> **Target Projects:** `cactus-compute/cactus`, `cactus-compute/needle`, `cactus-compute/cactus-hybrid`, `9Router`, `NVIDIA-NeMo/labs-OO-Agents`  
> **Source of Truth Priority:** Priority 1 (Local Tested Wheel/Source) > Priority 2 (Official Upstream Docs) > Priority 3 (Official Upstream Tests) > Priority 4 (Local Design Docs)

---

## 1. UPSTREAM API VERIFICATION TABLE

| Component | Installed / Expected | Upstream Current | API Verified | Version / Commit | Evidence / Source File | Impact & Discrepancies |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| **`cactus-needle`** | `needle` package | `cactus_needle-2.0.8-py3-none-any.whl` | ✅ YES | v2.0.8 (PyPI) | `needle/__init__.py`, `needle/agent/tools.py` | Import name is `needle`. Core class is `Needle(tools, system, weights, tool_index_path, buffer_size)`. Method `complete(text)` and `run(query, max_steps)` return dict envelope with `function_calls` and `confidence`. |
| **Needle Tool Schema** | `@needle.tool` or Pydantic | Function docstrings & Pydantic models | ✅ YES | v2.0.8 | `needle/agent/tools.py` (`build_schema`, `pydantic_schema`, `Field`) | Tools can be either Pydantic models or Python callables with type hints and docstrings. `build_schema(fn)` converts docstrings into JSON Schema properties. |
| **Needle Confidence** | Direct envelope field | `response.get("confidence")` | ✅ YES | v2.0.8 | `needle/__init__.py:L98` | Confidence is provided by base weights in `complete()` envelope; for custom weights without calibration head, `confidence` is `None` (must be handled gracefully). |
| **`cactus-hybrid`** | Hybrid edge-cloud router | 65K parameter semantic complexity classifier | ✅ YES | `cactus-compute/cactus-hybrid` | `cactuscompute.com/hybrid`, Y Combinator W24 | Evaluates query complexity and confidence. High confidence (≥ threshold) routes to local Needle/SLM; low confidence (< threshold) escalates to Cloud Frontier API. |
| **`cactus` Engine** | Cross-platform C++/Rust engine | C++ / Rust Runtime with NPU, ARM NEON, Metal, CQ 2-bit GGUF loader | ✅ YES | `cactus-compute/cactus` | `cactus.sh/docs`, YC W24 | Low-level execution engine; supports GGUF models, VLM vision models on-device, and on-device vector search (RAG). |
| **`9Router`** | Local/Cloud LLM Gateway | OpenAI-compatible gateway (`/v1/chat/completions`) | ✅ YES | `http://127.0.0.1:20128/v1` | `nanobot/providers/nine_router.py` | Routes to cloud/local LLM providers with model selection, fallback, and structured outputs. Decoupled from OCR. |
| **`Mistral OCR`** | Mistral OCR 4.x API | REST API endpoint (`https://api.mistral.ai/v1/ocr`) | ✅ YES | Mistral API v1 | `nanobot/ocr/mistral_ocr.py` | Must be decoupled from routing. Outputs raw markdown/pages/blocks with evidence bounding boxes; trust level is strictly `RAW_OCR`. |
| **`NOOA` (NVIDIA)** | Object-Oriented Agent Framework | `nooa` PyPI package (Classes=Agents, Methods=Tools, Docstrings=Prompts) | ✅ YES | `NVIDIA-NeMo/labs-OO-Agents` (Apache 2.0) | `nanobot/agents/base_agent.py` | Provides clean class hierarchy for specialized agents (`MedicalEquipmentAgent`, `NotionAgent`, `OCRAgent`). |

---

## 2. DISCREPANCY & ARCHITECTURE GAP ANALYSIS

1. **Confidence Semantics Discrepancy:**
   * *Local Document Misconception:* Local docs previously hardcoded confidence as a float attached to keyword matches (e.g. `if "MS4980" in q: confidence = 0.98`).
   * *Upstream Reality:* Confidence has distinct provenances:
     - `CACTUS_HYBRID`: Query routing confidence (is this task within edge capability?).
     - `NEEDLE`: Tool selection confidence (is this tool call statistically confident?).
     - `OCR`: Optical character recognition confidence per block/bounding box.
     - `ROUTER`: Fallback router confidence.
     - `FACTUAL / PROVENANCE`: Database match validation (deterministic ground truth).
   * *Action:* We strictly separate `ConfidenceSource` and never mix OCR confidence with routing confidence.

2. **Routing Logic Discrepancy:**
   * *Old Code Flaw:* `nanobot/core/router.py` used string substring matching (`if "cân" in text: ...`).
   * *Target Architecture:* Replace with a typed `RoutingDecision` model powered by `CactusHybridRouter` utilizing feature vectors, complexity scoring, and dynamic confidence thresholds.

3. **Database Repository Discrepancy:**
   * *Old Code Flaw:* `nanobot/repositories/device_repo.py` had hardcoded dictionary returns (`if "MS4980" in q: return [...]`).
   * *Target Architecture:* Connect to real SQLite database (`database/devices.db`) with parameterized SQL queries, indexing on `serial_no`, `model`, `facility_id`, schema migration, and fixture test databases.
