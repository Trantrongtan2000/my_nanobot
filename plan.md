# Nanobot NOOA Upgrade Plan

## 1. Mục tiêu

Đưa `nanobot_nooa_upgrade_package_v2` từ scaffold/heuristic implementation hiện tại thành runtime edge-cloud có contract rõ ràng, confidence provenance đúng, tool execution an toàn và có bằng chứng kiểm thử thực tế.

Không đánh dấu hoàn tất chỉ dựa trên code inspection hoặc benchmark regex. Một hạng mục chỉ được xem là `DONE` khi:

1. Code tồn tại và import được.
2. Unit test tương ứng pass.
3. Integration/smoke path pass.
4. Runtime dependency/API thật đã được xác minh.
5. Không còn mock/stub trong production path của hạng mục đó.

## 2. Hiện trạng đã xác minh

- `pytest -q`: 19 tests passed.
- SQLite hiện có 27 devices và 11 facilities.
- `RoutingDecision`, `ConfidencePolicy`, `TrustLevel` đã tồn tại.
- Repository đang truy vấn SQLite thật.
- `CactusHybridRouter` hiện vẫn là regex/keyword router với confidence hardcoded.
- `NeedleToolAdapter` hiện chỉ dispatch callable trong registry, chưa gọi package `cactus-needle`.
- Mistral OCR, Notion và Cloudflare runtime vẫn là stub/simulation.
- Tool contract hiện không tương thích với cách `NanobotCoordinator` truyền `{"query": text}` cho mọi tool.

## 3. Nguyên tắc kiến trúc đích

```text
Telegram
  -> Security / Allowlist
  -> Cactus Hybrid routing confidence
  -> Needle 2 complete/run
  -> Tool confidence gate
  -> Capability Registry
  -> Specialized NOOA Agent
  -> Service
  -> Repository / Provider
  -> Provenance-aware result
```

### Phân tách confidence

- `CACTUS_HYBRID`: confidence quyết định edge hay cloud.
- `NEEDLE`: confidence của tool selection/function call.
- `OCR`: confidence nhận dạng ký tự/block.
- `ROUTER`: chỉ dùng cho fallback heuristic, phải được ghi nhận rõ.
- `PROVENANCE`: mức độ xác minh nguồn dữ liệu, không đồng nhất với model confidence.

### Trust level

Router không được tạo `VERIFIED_FACT`. Trust chỉ được xác định sau execution và provenance validation.

- SQLite match chưa chắc là `VERIFIED_FACT` nếu chưa có verification metadata.
- OCR luôn bắt đầu ở `RAW_OCR`.
- LLM reasoning là `INFERRED`.
- Đề xuất là `PROPOSAL`.
- Thiếu bằng chứng là `UNKNOWN`.

## 4. Phân kỳ thực hiện

## Phase 0 — Baseline và kiểm soát phạm vi

### Việc cần làm

- Giữ lại benchmark hiện tại làm baseline heuristic.
- Tách test synthetic routing khỏi test runtime integration.
- Lập bảng inventory cho mọi component: `REAL`, `PARTIAL`, `STUB`, `MOCK`, `DEAD_CODE`.
- Không dùng README/docs làm bằng chứng implementation.

### Deliverables

- Baseline metrics có route, tool, confidence source và false-local rate.
- Danh sách dependency/runtime cần cài và version cần pin.

### Acceptance criteria

- Baseline được chạy reproducible.
- Mọi test mới phân biệt rõ heuristic fallback và provider thật.

## Phase 1 — Sửa correctness và execution safety

### 1. Chuẩn hóa tool contract

Tạo typed `ToolDefinition` gồm:

- `name`
- `description`
- `input_schema`
- `handler`
- `required_permission`
- `risk_level`
- `result_schema`

Dùng Pydantic để validate arguments trước khi gọi handler.

Sửa các tool hiện tại:

- `lookup_device(query, department)`
- `lookup_device_by_serial(serial_no)`
- `get_calibration_status(days_ahead)`
- `get_device_location(device_name)`
- `search_service_record(device_serial)`
- `create_notion_note(title, content)`

Không truyền chung `{"query": text}` cho mọi tool.

### 2. Enforce security policy

Trong coordinator/executor:

```text
allowlist
  -> classify action
  -> check permission
  -> evaluate risk
  -> apply confidence threshold
  -> human confirmation if required
  -> execute
```

Quy tắc tối thiểu:

- Read-only lookup: `READ_ONLY` + read threshold.
- Notion write: `WRITE_NOTION` + write threshold.
- Database mutation: `WRITE_DATABASE` + mutation threshold + confirmation.
- Critical/admin action: reject hoặc human confirmation bắt buộc.

Sanitizer phải được gọi khi đưa OCR/document/web content vào model. Nội dung tài liệu chỉ là DATA, không phải INSTRUCTION.

### 3. Sửa lỗi repository/service

- Resolve database path từ config một cách deterministic.
- Không tự tạo database production rỗng khi path sai.
- Dùng context manager cho SQLite connections.
- Thực sự áp dụng `days_ahead` trong calibration query.
- Thêm index cho `serial_no`, `model`, `facility_id`, `next_calibration_due`.
- Thêm migration/schema version.
- Xử lý SQLite lock với retry giới hạn.

### Acceptance criteria Phase 1

- Mọi tool có schema và permission rõ ràng.
- Test sai argument trả lỗi typed, không có `TypeError` không kiểm soát.
- Tool write không thể chạy chỉ vì router chọn đúng tool.
- Calibration query tôn trọng `days_ahead`.
- Test path sai không âm thầm tạo production DB mới.

## Phase 2 — Tích hợp Needle 2 thật

### 1. Dependency và API verification

- Pin version package `cactus-needle` sau khi xác minh môi trường đích.
- Xác minh import name, constructor, weights và tool schema API từ package thực tế.
- Không dựa chỉ vào tài liệu thiết kế.

### 2. Tạo `NeedleAgentAdapter`

Adapter phải:

1. Khởi tạo Needle agent.
2. Truyền typed tool catalog.
3. Gọi `complete()` hoặc `run()` theo API thực tế.
4. Parse response envelope.
5. Lấy `function_calls`.
6. Lấy confidence từ response.
7. Xử lý `confidence is None` an toàn.
8. Giới hạn số bước/iterations.
9. Trả về typed result.

### 3. Confidence gating

Policy theo action:

- Read-only lookup: threshold configurable, mặc định 0.80.
- Notion write: mặc định 0.90.
- Database mutation: mặc định 0.95.
- High-impact action: human confirmation bất kể confidence.

Luồng:

```text
confidence >= high
  -> execute nếu permission hợp lệ
medium <= confidence < high
  -> clarify hoặc restricted execution
confidence < medium
  -> cloud escalation
```

### Acceptance criteria Phase 2

- Có test chứng minh confidence Needle thấp không execute tool.
- Có test confidence `None`.
- Có test nhiều function calls.
- Tool arguments được validate trước execution.
- Không còn confidence giả trong Needle adapter.

## Phase 3 — Tích hợp Cactus Hybrid thật

### Việc cần làm

- Tạo `CactusHybridClient`/adapter riêng, không trộn logic với regex fallback.
- Xác minh API/model/weights/runtime của Cactus Hybrid.
- Router trả `RoutingDecision` typed.
- Heuristic chỉ là fallback khi provider unavailable.
- Ghi rõ `confidence_source=ROUTER` cho fallback.
- Không dùng keyword matching làm primary router.

### Safety override

Các truy vấn có dấu hiệu safety-critical phải ưu tiên escalation/confirmation, kể cả khi chứa model name hoặc keyword lookup:

- Có được tiếp tục sử dụng không?
- nguy cơ cho bệnh nhân
- lỗi nguồn/áp suất/NIBP
- tiêu chuẩn an toàn
- đánh giá rủi ro
- chẩn đoán nguyên nhân

### Acceptance criteria

- Ambiguous medical queries không bị route local chỉ vì chứa tên model.
- Có đo `false-local rate` riêng.
- Có fallback behavior rõ khi Cactus Hybrid unavailable.
- Confidence của Cactus Hybrid được lưu riêng với confidence của Needle.

## Phase 4 — Hoàn thiện 9Router production client

### Việc cần làm

- Tách timeout, DNS/network error, 4xx, 5xx, rate limit và auth failure.
- Implement circuit breaker thật với state: `CLOSED`, `OPEN`, `HALF_OPEN`.
- Implement model fallback chain configurable.
- Không trả fallback giả dưới dạng thành công.
- Validate OpenAI-compatible response bằng schema.
- Propagate request ID, provider, model và latency.
- Không hardcode secret mặc định trong production.

### Acceptance criteria

- 9Router offline trả `degraded`/`provider_error`, không trả `success` giả.
- Circuit breaker ngăn request lặp vô hạn khi provider down.
- Fallback chain có test.
- Structured output lỗi bị reject rõ ràng.

## Phase 5 — Hoàn thiện Mistral OCR pipeline

### Pipeline đích

```text
File upload
  -> validation / size limit / MIME check
  -> Mistral OCR API
  -> OCRResult
  -> NormalizedDocument
  -> structured extraction
  -> schema validation
  -> RAW_OCR evidence
  -> optional LLM reasoning
```

### Việc cần làm

- Implement HTTP upload thật đến Mistral OCR.
- Dùng API key từ environment/config, không hardcode.
- Timeout, retry/backoff và error mapping.
- Chuẩn hóa page/block/bbox/evidence.
- Gắn OCR confidence theo block/field.
- Không nâng OCR output thành `VERIFIED_FACT`.
- Tạo schema cho bàn giao/nghiệm thu, kiểm định/hiệu chuẩn và bảo trì/sửa chữa.
- Phân biệt production provider và test fake.

### Acceptance criteria

- Import provider sạch trên Python version được hỗ trợ.
- Có mocked HTTP tests và ít nhất một smoke test provider configuration.
- Mọi field extracted có evidence hoặc trạng thái thiếu evidence.
- OCR prompt/document content được đánh dấu là untrusted data.

## Phase 6 — NOOA agents và Notion

### Specialized agents

Tạo và đăng ký:

- `MedicalEquipmentAgent`
- `OCRPipelineAgent`
- `NotionWorkspaceAgent`
- `SelfImprovementAgent`

Coordinator chỉ điều phối capability, không chứa business logic của từng agent.

### Notion

- Implement MCP/API call thật.
- Permission `WRITE_NOTION`.
- Idempotency key.
- Timeout/retry.
- Trả về page ID thật.
- Không trả `success` nếu chỉ mới tạo dictionary nội bộ.

### Self-improvement

Ghi event cho low confidence, wrong tool, tool failure, cloud escalation, user correction và OCR extraction error.

Không tự động điều chỉnh threshold dựa trên vài request. Mọi calibration change phải qua dataset/evaluation.

## Phase 7 — Observability, reliability và release

### Observability

Theo dõi tối thiểu:

- request ID;
- route và confidence source;
- Needle confidence;
- selected tool;
- permission/risk decision;
- tool/provider latency;
- escalation reason;
- trust level/provenance;
- error code;
- false-local và false-cloud outcome.

Persist structured logs hoặc metrics phù hợp với Raspberry Pi.

### Reliability

- File upload limit.
- Max tool iterations.
- Timeout cho tool/provider.
- Queue khi cloud unavailable.
- SQLite lock retry.
- Graceful shutdown.
- Secret redaction trong logs.
- Không expose prompt/API key/Notion token.

### Acceptance criteria

- Có smoke test toàn flow.
- Có retry/circuit breaker tests.
- Có security injection tests cho OCR/web/document input.
- Có regression benchmark tối thiểu 20 local lookup, 20 local write, 20 cloud reasoning, 20 ambiguous, 20 malicious/irrelevant và 20 OCR extraction.
- Báo cáo có routing accuracy, tool selection accuracy, false-local rate, false-cloud rate, calibration, latency, memory và escalation rate.

## 5. Test matrix bắt buộc

### Unit

- Pydantic routing/tool contracts.
- Confidence policy từng action type.
- Trust/provenance validation.
- Security risk/permission.
- Repository query và calibration date filtering.
- OCR response normalization.
- 9Router error classification.

### Integration

- Coordinator → security → router → Needle → tool → service → repository.
- Coordinator → cloud escalation → 9Router.
- OCR → normalized document → extraction.
- Notion write với permission/confirmation.

### Negative/safety

- Unauthorized Telegram user.
- Prompt injection trong OCR content.
- Low Needle confidence.
- Missing confidence.
- Unknown tool.
- Wrong tool arguments.
- Database unavailable/locked.
- 9Router offline.
- OCR timeout.
- Critical action without confirmation.

### Runtime smoke

- Import all production modules.
- Run against configured SQLite path.
- Run provider health checks without leaking secrets.
- Verify actual external API only in explicitly enabled environment.

## 6. Definition of Done

Chỉ đánh dấu toàn dự án hoàn tất khi:

- Cactus Hybrid được phân biệt và tích hợp đúng API thực tế.
- Needle 2 được gọi bằng package/API thực tế.
- Confidence lấy từ model/provider, không hardcode trong routing business logic.
- Có confidence source riêng cho Hybrid, Needle, OCR và fallback router.
- Router không tạo `VERIFIED_FACT`.
- Tool result có provenance đầy đủ.
- Permission/risk/confidence gate nằm trong runtime execution path.
- Tool schemas khớp arguments thực tế.
- OCR API thật hoạt động và không nhầm OCR confidence với database truth.
- 9Router fallback/circuit breaker hoạt động và không báo success giả.
- Notion integration có execution evidence.
- Specialized NOOA agents được đăng ký và gọi qua capability layer.
- Tests chứng minh threshold behavior và safety behavior.
- Benchmark có false-local rate và chạy trên flow thật.
- Không còn production stub/simulation chưa được đánh dấu rõ.
- Tài liệu audit/report phản ánh đúng implementation hiện tại.

## 7. Thứ tự ưu tiên thực tế

1. Sửa tool argument contract.
2. Enforce permission + risk + confidence gate.
3. Tích hợp Needle 2 thật.
4. Tách heuristic fallback khỏi Cactus Hybrid adapter.
5. Sửa trust/provenance semantics.
6. Hoàn thiện 9Router reliability.
7. Hoàn thiện Mistral OCR thật.
8. Tạo specialized agents và Notion integration.
9. Hardening SQLite, observability và release tests.

## 8. Quy tắc không được vi phạm

- Không tạo mock để làm test pass.
- Không coi docs là bằng chứng runtime.
- Không dùng keyword matching làm primary router sau khi provider thật đã sẵn sàng.
- Không hardcode confidence cho business decision.
- Không gán `VERIFIED_FACT` trước provenance validation.
- Không cho document/OCR/web content trở thành instruction.
- Không ghi secret vào source hoặc telemetry.
- Không tuyên bố `DONE` nếu mới chỉ unit test pass.