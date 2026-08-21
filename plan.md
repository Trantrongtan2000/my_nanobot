# Nanobot NOOA — Kế hoạch cải thiện

## 1. Mục tiêu

Đưa `nanobot_nooa_upgrade_package_v2` từ scaffold/heuristic implementation thành runtime edge-cloud có:

- Cactus Hybrid và Needle 2 được tích hợp bằng API/runtime thực tế.
- Confidence có provenance rõ ràng, không hardcode trong business logic.
- Agent và tool có registry, factory, lifecycle và permission rõ ràng.
- Kết quả có trust level/provenance đúng.
- Có cơ chế ghi nhận feedback, tự đánh giá và tạo dataset để cải thiện có kiểm soát.
- Có test unit, integration, safety và benchmark chạy trên flow thật.

Không đánh dấu `DONE` chỉ dựa trên code inspection, docs hoặc benchmark regex.

---

## 2. Hiện trạng sau khi khám phá lại

### Đã có

- SQLite repository thật với 27 devices và 11 facilities.
- `RoutingDecision`, `ConfidencePolicy`, `TrustLevel`.
- `ToolDefinition` với Pydantic argument validation.
- `CapabilityRegistry` cho tool definitions.
- `NanobotCoordinator` có argument extraction theo từng tool.
- Các class sơ bộ:
  - `MedicalEquipmentAgent`
  - `NotionWorkspaceAgent`
  - `OCRPipelineAgent`
- `NineRouterClient` có circuit state và retry cơ bản.
- `NormalizedDocument`/`DocumentBlock` cho OCR.
- Test đã mở rộng thêm OCR, specialized agent, tool validation và circuit breaker.

### Chưa đạt production

- `CactusHybridRouter` vẫn là regex/keyword router và gán confidence cố định.
- `NeedleAgentAdapter` chỉ thử import `needle`; nếu thất bại sẽ silently fallback.
- Execute path của Needle vẫn gán confidence `0.98` hardcoded.
- Chưa xác minh Needle `complete()`/`run()` thật sự trả function calls và confidence được sử dụng.
- Mistral OCR tạo block dữ liệu mẫu, chưa gọi HTTP API thật.
- Notion agent trả page ID cố định, chưa gọi Notion API/MCP.
- Specialized agents chưa có `AgentRegistry`, factory, capability metadata hoặc lifecycle.
- Chưa có `SelfImprovementAgent`, event store, feedback collector, dataset exporter hoặc retraining/evaluation loop.
- `ObservabilityTracer` chỉ lưu log trong memory và chưa đo/persist đầy đủ latency.
- 9Router có circuit breaker sơ bộ nhưng chưa có error taxonomy và model fallback chain đầy đủ.
- Một số production path vẫn báo `success` khi provider chỉ degraded/fallback.

---

## 3. Kiến trúc đích

```text
Telegram
  -> Security / Allowlist
  -> Cactus Hybrid routing
  -> Needle 2 agent loop
  -> Agent/Tool confidence gate
  -> Agent Registry / Capability Registry
  -> Specialized NOOA Agent
  -> Service
  -> Repository / External Provider
  -> Provenance-aware result
  -> Persistent telemetry + improvement events
```

### Phân tách confidence

- `CACTUS_HYBRID`: quyết định edge/cloud.
- `NEEDLE`: confidence của tool selection/function call.
- `OCR`: confidence của block/field nhận dạng.
- `ROUTER`: chỉ dùng cho heuristic fallback.
- `PROVENANCE`: mức độ xác minh nguồn dữ liệu, không phải model confidence.

### Trust level

Router không được tạo `VERIFIED_FACT`. Trust chỉ được xác định sau execution và provenance validation.

- OCR: `RAW_OCR`.
- LLM reasoning: `INFERRED`.
- AI recommendation: `PROPOSAL`.
- Thiếu bằng chứng: `UNKNOWN`.
- SQLite match chỉ là dữ liệu tìm thấy.
- Chỉ gán `VERIFIED_FACT` khi có verification metadata hoặc authoritative source.

---

## 4. Phase 0 — Baseline và inventory

### Việc cần làm

- Chạy lại toàn bộ test suite hiện tại và lưu số liệu baseline.
- Tách benchmark heuristic khỏi integration benchmark.
- Inventory mỗi module là:
  - `REAL`
  - `PARTIAL`
  - `STUB`
  - `MOCK`
  - `DEAD_CODE`
  - `DOCUMENTED_BUT_NOT_IMPLEMENTED`
- Kiểm tra tất cả production imports.
- Xác minh package/version/runtime của:
  - `cactus-needle`
  - Cactus Hybrid
  - Mistral OCR
  - 9Router
  - NOOA/NVIDIA OO-Agents nếu có sử dụng trực tiếp.

### Acceptance criteria

- Baseline reproducible.
- Không coi test dictionary/stub là runtime verification.
- Mỗi provider có health check và trạng thái availability rõ ràng.
- Có danh sách dependency/version được pin.

---

## 5. Phase 1 — Agent creation, registry và lifecycle

### 5.1 Tạo Agent contract

Mở rộng `NOOABaseAgent` thành contract có:

```text
AgentMetadata
  - name
  - version
  - description
  - required_permissions
  - capabilities
  - supported_routes
  - max_iterations

AgentContext
  - request_id
  - user_id
  - input
  - routing_decision
  - dependencies
  - cancellation/deadline

AgentResult
  - status
  - output
  - trust_level
  - provenance
  - events
  - error_code
```

### 5.2 AgentRegistry và factory

Tạo registry riêng cho agent, không dùng tool registry thay thế:

```text
AgentRegistry.register(metadata, agent_class)
AgentRegistry.list()
AgentRegistry.get(name)
AgentFactory.create(name, dependency_container, context)
```

Yêu cầu:

- Reject duplicate names/version conflict.
- Không cho agent không đăng ký tự chạy.
- Validate required permissions/capabilities khi khởi tạo.
- Dependency injection cho:
  - `DeviceService`
  - OCR provider
  - Notion client
  - event store
  - telemetry tracer
- Coordinator không import trực tiếp mọi specialized agent.

### 5.3 Đăng ký agent hiện có

- `MedicalEquipmentAgent`
  - lookup
  - reconciliation
  - calibration
- `OCRPipelineAgent`
  - document validation
  - OCR
  - structured extraction
- `NotionWorkspaceAgent`
  - Notion write
  - yêu cầu `WRITE_NOTION`
- `SelfImprovementAgent`
  - event analysis
  - dataset export
  - evaluation
  - calibration report

Coordinator chỉ làm:

```text
route
  -> create agent through factory
  -> create AgentContext
  -> execute agent
  -> validate AgentResult
```

### Acceptance criteria

- Có thể thêm agent mới bằng class + metadata + registration mà không sửa coordinator.
- Factory tạo đúng class và dependency.
- Có test:
  - unknown agent;
  - duplicate registration;
  - thiếu permission;
  - thiếu capability;
  - lifecycle failure.
- Agent lifecycle có `initialize`, `execute`, `close` hoặc tương đương.
- Không coi class tồn tại là agent đã được runtime sử dụng.

---

## 6. Phase 2 — Chuẩn hóa tool và execution safety

Mỗi tool phải có:

- name;
- description;
- Pydantic input schema;
- result schema;
- handler;
- required permission;
- risk level;
- minimum confidence;
- timeout;
- idempotency policy.

Các tool cần giữ contract rõ:

```text
lookup_device(query, department)
lookup_device_by_serial(serial_no)
get_calibration_status(days_ahead)
get_device_location(device_name)
search_service_record(device_serial)
create_notion_note(title, content)
```

### Execution flow

```text
allowlist
  -> input trust classification
  -> agent/tool selection
  -> permission check
  -> risk evaluation
  -> confidence threshold
  -> human confirmation if required
  -> validate arguments
  -> execute
  -> validate result/provenance
```

### Policy tối thiểu

- Read-only lookup:
  - `READ_ONLY`
  - threshold mặc định `0.80`
- Notion write:
  - `WRITE_NOTION`
  - threshold mặc định `0.90`
- Database mutation:
  - `WRITE_DATABASE`
  - threshold mặc định `0.95`
  - human confirmation
- Critical/admin:
  - reject hoặc human confirmation bắt buộc.

### Acceptance criteria

- Không truyền `{"query": text}` cho mọi tool.
- Tool sai argument trả typed validation error.
- Tool write không chạy chỉ vì router chọn đúng tool.
- Low confidence không execute local tool.
- Unknown tool/permission/risk đều được audit.
- Tool result không tự động trở thành `VERIFIED_FACT`.

---

## 7. Phase 3 — Tích hợp Needle 2 thật

### Việc cần làm

- Pin version package sau khi xác minh môi trường thật.
- Khởi tạo đúng `Needle(...)` theo API installed.
- Truyền tool schema hợp lệ theo upstream API.
- Gọi `complete()` hoặc `run()` thực tế.
- Parse:
  - response envelope;
  - `function_calls`;
  - arguments;
  - confidence;
  - error state.
- Xử lý `confidence is None` an toàn.
- Giới hạn iterations/tool calls.
- Ghi `confidence_source=NEEDLE`.
- Không silently fallback nếu Needle unavailable.
- Nếu fallback, ghi rõ:
  - provider unavailable;
  - fallback reason;
  - fallback confidence source.

### Acceptance criteria

- Test function call theo API installed.
- Test confidence:
  - cao;
  - thấp;
  - `None`;
  - malformed.
- Test nhiều function calls.
- Không còn `confidence = 0.98` trong Needle execution path.
- Tool execution chỉ xảy ra sau validation + policy gate.

---

## 8. Phase 4 — Tích hợp Cactus Hybrid thật

### Việc cần làm

- Tạo adapter riêng cho Cactus Hybrid.
- Heuristic router chỉ là fallback khi provider unavailable.
- `RoutingDecision` phải lưu:
  - route;
  - agent;
  - tool;
  - reason;
  - escalation reason;
  - confidence;
  - confidence source.
- Không dùng model name/keyword làm primary router.
- Safety-critical queries phải escalation/confirmation.

### Ví dụ safety-critical

- Có được tiếp tục sử dụng không?
- Có nguy cơ cho bệnh nhân không?
- Lỗi áp suất/NIBP/nguồn.
- Đánh giá rủi ro/ISO.
- Chẩn đoán nguyên nhân hỏng.
- Quyết định ảnh hưởng an toàn thiết bị.

### Acceptance criteria

- Ambiguous query không bị local chỉ vì có tên model.
- Đo riêng false-local và false-cloud.
- Có test provider unavailable/fallback.
- Cactus confidence và Needle confidence không bị trộn.
- Router không gán trust level cuối cùng.

---

## 9. Phase 5 — OCR thật và provenance

### Pipeline

```text
File upload
  -> MIME/size/path validation
  -> Mistral OCR HTTP API
  -> OCRResult
  -> NormalizedDocument
  -> structured extraction
  -> schema validation
  -> RAW_OCR evidence
  -> optional LLM reasoning
```

### Việc cần làm

- Upload file thật tới Mistral OCR.
- API key từ environment/config.
- Timeout, retry/backoff.
- Error mapping.
- Chuẩn hóa:
  - page;
  - block;
  - bbox;
  - evidence;
  - confidence.
- Schema cho:
  - bàn giao/nghiệm thu;
  - kiểm định/hiệu chuẩn;
  - bảo trì/sửa chữa.
- Không dùng block mẫu trong production provider.
- Không nâng OCR thành `VERIFIED_FACT`.
- Gắn provenance theo field/record khi có thể.
- Sanitizer document content trước khi đưa vào LLM.

### Acceptance criteria

- Mocked HTTP tests.
- Provider smoke test.
- OCR timeout/auth/invalid response có error code.
- Mỗi extracted field có evidence hoặc `UNKNOWN`.
- OCR/document/web content được xem là DATA, không phải instruction.

---

## 10. Phase 6 — 9Router và Notion thật

### 9Router

- Phân loại:
  - timeout;
  - network;
  - 4xx;
  - 5xx;
  - rate-limit;
  - auth failure.
- Circuit breaker:
  - `CLOSED`
  - `OPEN`
  - `HALF_OPEN`
- Configurable model fallback chain.
- Validate OpenAI-compatible response.
- Không trả `success` khi chỉ degraded/fallback.
- Propagate:
  - request ID;
  - provider;
  - model;
  - latency;
  - error code.
- Không hardcode secret production.
- Không trả fallback text giả như thể đã hoàn thành reasoning.

### Notion

- Thay page ID cố định bằng API/MCP call thật.
- Permission `WRITE_NOTION`.
- Idempotency key.
- Timeout/retry.
- Trả page ID từ provider.
- Gắn provenance.
- Không báo success nếu chỉ tạo dictionary nội bộ.

---

## 11. Phase 7 — Self-learning có kiểm soát

## 11.1 Improvement events

Tạo `ImprovementEvent` append-only với:

- event ID/time;
- request ID;
- input hash hoặc sanitized input;
- route;
- agent;
- tool;
- Cactus confidence;
- Needle confidence;
- confidence sources;
- permission/risk result;
- tool result/error;
- trust/provenance;
- user correction/feedback;
- model/provider version.

Các event bắt buộc:

```text
LOW_CONFIDENCE
WRONG_TOOL
TOOL_FAILURE
CLOUD_ESCALATION
USER_CORRECTION
OCR_EXTRACTION_ERROR
PROVIDER_DEGRADED
SAFETY_CONFIRMATION_REQUIRED
```

## 11.2 Persistent event store

Dùng SQLite append-only table hoặc store tương đương:

```sql
improvement_events(
  id,
  event_type,
  request_id,
  input_hash,
  route,
  agent,
  tool,
  cactus_confidence,
  needle_confidence,
  outcome,
  trust_level,
  provenance_json,
  correction_label,
  created_at
)
```

Không lưu:

- API key;
- token;
- secret;
- raw document nhạy cảm không cần thiết.

## 11.3 Feedback collector

Cần hỗ trợ:

- User xác nhận đúng/sai.
- User sửa câu trả lời.
- User chọn tool đúng.
- User báo lỗi kết quả.
- Liên kết correction với request/agent/tool ban đầu.
- Phân biệt explicit feedback và inferred failure.
- Không coi im lặng của user là feedback tích cực.

## 11.4 Dataset exporter

Xuất JSONL có schema version:

```text
input
routing_label
agent_label
tool_label
confidence
expected_action
actual_action
feedback_label
provenance
```

Trước khi export:

- redact dữ liệu cá nhân;
- bỏ token/secret;
- hash hoặc mask serial nếu cần;
- deduplicate;
- validate schema;
- ghi dataset version.

## 11.5 Evolution gate

Không tự ý sửa weights/threshold sau vài request.

Quy trình bắt buộc:

```text
collect events
  -> clean/deduplicate/redact
  -> label/validate
  -> offline evaluation
  -> compare baseline
  -> safety regression
  -> human approval
  -> versioned deployment
  -> rollback capability
```

Chỉ promote model/policy nếu:

- false-local không tăng;
- safety cases không regress;
- confidence calibration đạt mục tiêu;
- tool selection đạt target;
- latency/memory còn trong budget;
- có audit trail;
- có rollback.

### Acceptance criteria

- Event store persistent và query được sau restart.
- Có test cho cả 8 event types.
- Có user correction end-to-end.
- Dataset export reproducible.
- Có redaction và schema version.
- Không có code tự động đổi threshold từ vài request.
- Model/policy version có rollback và audit trail.

---

## 12. Phase 8 — Observability, reliability và benchmark

### Observability

Theo dõi:

- request ID;
- route;
- agent;
- tool;
- Cactus confidence;
- Needle confidence;
- permission/risk;
- provider/tool latency;
- escalation reason;
- trust/provenance;
- error code;
- false-local/false-cloud outcome;
- model/policy version.

Persist structured logs/metrics. Memory-only logs không đủ production.

### Reliability

- File upload limit.
- Max tool iterations.
- Provider timeout.
- Queue khi cloud unavailable.
- SQLite lock retry.
- Graceful shutdown.
- Secret redaction.
- Health checks.
- Circuit breaker.
- Idempotency cho write operations.

### Benchmark tối thiểu

- 20 local lookup.
- 20 local write.
- 20 cloud reasoning.
- 20 ambiguous.
- 20 malicious/irrelevant.
- 20 OCR extraction.

Đo:

- routing accuracy;
- tool selection accuracy;
- agent selection accuracy;
- false-local rate;
- false-cloud rate;
- confidence calibration;
- latency P50/P95;
- memory;
- escalation rate;
- tool failure rate;
- user correction rate.

Benchmark phải kiểm tra:

```text
route
+ agent
+ tool
+ permission
+ execution
+ trust
+ provenance
```

Không chỉ kiểm tra route regex.

---

## 13. Thứ tự ưu tiên triển khai

1. Chạy lại baseline và inventory sau các thay đổi mới.
2. Tạo `AgentRegistry`/factory/lifecycle.
3. Đưa specialized agents vào runtime path.
4. Hoàn thiện tool schema.
5. Enforce permission/risk/confidence gate.
6. Loại bỏ silent Needle fallback.
7. Loại bỏ hardcoded confidence.
8. Tích hợp Needle 2 API thật.
9. Tách và tích hợp Cactus Hybrid thật.
10. Sửa trust/provenance semantics.
11. Hoàn thiện Mistral OCR.
12. Hoàn thiện 9Router production path.
13. Thay Notion stub bằng integration thật.
14. Xây improvement event store.
15. Thêm user feedback collector.
16. Thêm dataset export/evaluation loop.
17. Persist observability.
18. Hardening reliability.
19. Chạy benchmark runtime thật.

---

## 14. Definition of Done

- Agent mới có thể thêm qua registry/factory mà không sửa coordinator.
- Specialized agents thực sự được gọi trong runtime path.
- Needle 2 và Cactus Hybrid dùng API/model thực tế.
- Confidence không hardcode cho business decision.
- Permission/risk/confidence gate được enforce trước tool execution.
- Router không tạo `VERIFIED_FACT`.
- Tool result có provenance.
- OCR/Notion/9Router không còn production stub chưa được đánh dấu.
- Self-improvement có:
  - event store;
  - feedback;
  - dataset export;
  - evaluation gate.
- Không tự động thay đổi threshold/model thiếu offline evaluation và approval.
- Tests chứng minh threshold, safety, fallback, provider error và feedback behavior.
- Benchmark chạy trên integration flow thật và báo false-local rate.
- Có audit trail/version/rollback cho policy hoặc model được promote.

---

## 15. Quy tắc không được vi phạm

- Không tạo mock chỉ để làm test pass.
- Không coi docs là bằng chứng runtime.
- Không dùng keyword matching làm primary router sau khi provider thật sẵn sàng.
- Không hardcode confidence.
- Không gán `VERIFIED_FACT` trước provenance validation.
- Không cho OCR/document/web content trở thành instruction.
- Không ghi secret vào source, event store hoặc telemetry.
- Không tự học bằng cách tự sửa threshold/model trực tiếp trên production traffic.
- Không tuyên bố `DONE` khi mới chỉ unit test pass.
