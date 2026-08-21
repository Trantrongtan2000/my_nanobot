# CACTUS ARCHITECTURE CORRECTION & ALIGNMENT

> **Document Status:** Complete & Verified  
> **Key Architecture Decisions:**

1. **Separation of Concerns:**
   - **`cactus` Core:** The low-level C++/Rust inference runtime.
   - **`needle` (Needle 2):** The 45M Simple Attention Network model specifically for on-device tool calling and structured extraction.
   - **`cactus-hybrid`:** The semantic complexity and confidence router that directs queries between Local Edge and Cloud Frontier.

2. **Confidence Provenance Resolution:**
   - Confidence is never hardcoded from string keywords.
   - Provenance sources are strictly categorized as `CACTUS_HYBRID`, `NEEDLE`, `OCR`, `ROUTER`, or `UNKNOWN`.
   - `VERIFIED_FACT` is reserved exclusively for records backed by authoritative database IDs or validated physical certificates.

3. **No Mocking in Production:**
   - SQLite `DeviceRepository` connects to real tables (`devices`, `facilities`) with parameterized queries.
   - Mocks are strictly quarantined in `tests/mocks/`.
