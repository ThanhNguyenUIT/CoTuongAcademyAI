# Kiến trúc kỹ thuật — modular monolith trước, tách service khi có lý do

## 1. Công nghệ được chọn cho bản đầu

- **Frontend:** React + TypeScript + Vite + Tailwind CSS; SVG cho bàn cờ, component riêng cho nước đi và panel.
- **Backend:** Python + FastAPI + Pydantic; tách các domain module dù cùng một process.
- **Persistence:** opening knowledge hiện lấy YAML làm nguồn runtime; Phase 5 learner history dùng SQLite local và migration riêng. Chỉ chọn PostgreSQL/auth khi có yêu cầu multi-user/cloud.
- **Engine:** process native giao tiếp UCI/UCCI qua adapter; `MockEngine` trong automated tests. Chọn binary/weights sau license gate.
- **LLM:** provider adapter, API key phía backend, có chế độ mock và fallback không dùng LLM.
- **Worker/queue:** chỉ bổ sung khi nhu cầu concurrency thực tế vượt mức xử lý local; không đưa Celery/Redis vào Phase 0.
- **Quản lý gói:** npm cho frontend; Python venv + pip hoặc uv cho backend, chốt một công cụ khi bootstrap và ghi trong `state/DECISIONS.md`.

## 2. Ranh giới trách nhiệm

```text
Browser (React)
  ├── Board UI (render + input + optimistic UX)
  ├── Opening Lab (knowledge graph + study controls)
  └── Tutor panel (hints + chat + evidence)
          |
        REST (WebSocket/SSE khi thật sự cần streaming)
          |
FastAPI modular monolith
  ├── api          request validation, auth (later), response DTO
  ├── rules        source-of-truth legal moves/game state
  ├── engine       interface + subprocess adapters + timeouts
  ├── knowledge    positions, branches, annotations, lessons
  ├── tutor        retrieval + prompt policy + factual verification
  ├── learning     attempts, mastery, spaced review
  └── persistence  repository + migrations
          |
   PostgreSQL / SQLite       Process engine       LLM provider
```

## 3. Các interface cốt lõi

**RulesService**: `load_position(fen)`, `legal_moves(fen)`, `apply_move(fen, iccs)`, `game_status(fen, move_history)`. Chú ý các luật đuổi/chiếu liên tục có thể cần **lịch sử ván**, không quyết định chỉ từ FEN.

**EngineAdapter**: process UCI local được tái sử dụng, hỗ trợ handshake/readiness, `analyze(position, limits, multipv)`, best move qua PV đã kiểm tra và `stop(job_id)`; giới hạn tiến trình, thời gian và bộ nhớ. Kết quả chứa `engine_id`, `engine_version`, `protocol`, `position`, `limits`, `lines`, `score_perspective`, `elapsed_ms`, `is_complete`. RulesService kiểm tra từng nước của mọi PV.

**OpeningRepository**: `get_position(key)`, `get_variations(position_key)`, `get_annotation(position_key, move_key, locale)`, `get_lesson(id)`. Không yêu cầu vector DB khi chưa có nhu cầu.

**TutorProvider**: `explain(TutorContext) -> TutorProviderDraft`; `TutorService` owns hint progression, retrieval, evidence and legal-move policy. Context includes validated FEN, approved annotations, lesson/exercise context and validated engine PV. All lesson and learner strings are untrusted data in the prompt. The provider cannot execute game commands; draft claims need resolvable provenance and candidate moves must match RulesService plus an approved lesson choice or engine PV. Default provider is `none` (written fallback); optional mock and OpenAI-compatible adapters are configured only on the backend.

**LearningService**: `submit_attempt()` (idempotent, exercise-versioned), `recommend()`, `due_reviews()`, `progress()`, `rematch()` và local export/delete. SQLite ghi learner/game/validated positions/attempt/review schedule. Saved games có đường đọc theo owner để Board khôi phục sau refresh; khi lưu tiếp chỉ xác thực suffix mới sau common prefix đã lưu, còn nhánh divergent được xác thực lại. Heuristic được kiểm thử bằng clock giả; rubric không tự chấm chất lượng lời giải văn bản.

## 4. Quy ước tọa độ và phiên bản

- Backend và frontend trao đổi FEN + nước **ICCS/UCI coordinate**; ghi chú người dùng có thể hiển thị ký pháp cờ tướng Việt Nam ở UI (giai đoạn sau).
- Không mặc định orientation/tọa độ giữa hai engine giống nhau; có fixture khởi đầu và round-trip tests.
- Mã vị trí khai cuộc loại bỏ/chuẩn hóa các trường FEN không quyết định vị trí khi định danh nút đồ thị, nhưng **không loại bỏ lượt đi**. Quy tắc lặp phải xét lịch sử phù hợp.
- Mọi adapter nêu rõ engine version, protocol, score perspective. Không hiển thị “+3” nếu không định nghĩa + dành cho bên nào và đơn vị đánh giá nào.

## 5. Luồng API phân tích

1. Browser gửi FEN/nước đi; backend validates.
2. RulesService xác nhận vị trí/nước. EngineService phân tích đồng thời tối đa theo quota.
3. Kết quả được chuẩn hóa, chỉ lưu cache khi có đủ thông tin engine/version/limits.
4. Tutor retrieves only reviewed/published content in production; experimental material requires explicit local opt-in. Engine hint analysis is capped at 400 ms, depth 8, MultiPV 2 and cached for 45 seconds.
5. Provider output is schema-validated; ICCS tokens in claims need cited move evidence, and candidate moves must be legal and evidence-backed. Unsupported forced-win claims are removed.
6. Frontend asks for three sequential hint tiers. Without a provider it uses authored lesson hints, labels fallback and uncertainty, and does not pretend an LLM or engine ran.

Provider calls use a 20-minute response cache and a process-local ceiling of 20 uncached calls per client per minute. No paid provider is selected or activated as part of the prototype.

## 6. Khả năng mở rộng

- Phase 5 learning profile là local-only: UUID ngẫu nhiên ở browser storage không phải xác thực. Endpoint learning bị tắt trong `APP_ENV=production`; cần authentication/authorization và privacy review trước khi mở multi-user hoặc cloud.
- Skill stats hiển thị sample size và số lần lựa chọn khớp trọng tâm do nội dung đánh dấu; không tự đổi ra Elo/mastery. Ôn tập mặc định 1/3/7 ngày, cấu hình bằng `LEARNING_REVIEW_INTERVALS_DAYS`.
- Rematch chỉ lấy mẫu tối đa ba nước trong game đã RulesService kiểm tra. Engine đánh dấu khi chênh lệch side-to-move normalized Red đạt ngưỡng 100 cp; người học chọn checkpoint cần đánh lại. Đây là heuristic tìm kiếm, không phải giám định viên gắn nhãn sai lầm.

- Đặt giới hạn CPU/process, timeout, cancellation, rate limit; không chạy một engine process per user không giới hạn.
- Cache theo `position_key + engine_id/version + settings + limits` (sau này theo kiểu chính sách cache được chốt).
- Streaming analysis dùng SSE hoặc WebSocket **chỉ khi** cần UX realtime; MVP REST poll hoặc response ngắn cũng được.
- Giữ khả năng đóng gói desktop về sau bằng cách không trộn code engine vào React UI.
