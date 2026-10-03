# Hợp đồng dữ liệu và API

> Cập nhật Phase 5: health, rules, engine local, Opening Lab, tutor hint và adaptive learning local đã có triển khai. Phase 6 tập trung release.

## 1. Từ vựng/domain

- **Game:** một ván cờ gồm khởi tạo, history nước đi, trạng thái kết thúc. Không chỉ lưu FEN cuối.
- **Position:** vị trí bàn cờ với lượt đi và thông tin game cần thiết.
- **Position key:** dạng chuẩn hóa của vị trí để hỗ trợ chuyển vị; phải được kiểm chứng bằng fixture, không tự rút gọn các trường có ý nghĩa luật.
- **Variation edge:** một nước đi hợp lệ dẫn từ một Position tới Position khác; nhiều đường có thể dẫn tới cùng vị trí.
- **Lesson/Exercise:** giáo trình có mục tiêu kỹ năng, chứng cứ nguồn, rubric; exercise có vị trí, đáp án có thể chấp nhận và feedback.
- **Attempt:** câu trả lời, thời gian, hints đã xem, đánh giá theo rubric, phiên bản bài tập.

## 2. Schema logic ban đầu

| Bảng | Trường lõi | Lưu ý |
| --- | --- | --- |
| `positions` | `id`, `position_key`, `fen_canonical`, `side_to_move` | Unique key có kiểm thử |
| `position_edges` | `id`, `from_position_id`, `move_iccs`, `to_position_id` | Unique `(from,move)` nếu rules xác nhận |
| `openings` | `id`, `name_vi`, `classification_code`, `description`, `source_refs` | Không ép taxonomy khi chưa xác minh |
| `opening_lines` | `id`, `opening_id`, `edge_sequence`, `label`, `version` | Liên kết nhánh với đồ thị |
| `annotations` | `id`, `position_id`, `move_iccs`, `claim`, `source_refs`, `review_status` | Draft/reviewed/published |
| `lessons` | `id`, `slug`, `outcomes`, `steps`, `content_version`, `review_status` | Từ 1 chapter ở Phase 3 |
| `exercises` | `id`, `fen`, `rubric`, `accepted_lines`, `difficulty`, `source_refs` | Không đồng nhất best line với đáp án duy nhất |
| `games` / `game_moves` | `game_id`, `starting_fen`, `ply`, `move_iccs`, `fen_after`, `clock` | Truy vết sự kiện |
| `attempts` | `learner_id`, `exercise_id`, `exercise_version`, `answer`, `hint_level`, `score` | Phase 5 |
| `engine_analyses` | `position_key`, `engine_id`, `version`, `settings`, `depth`, `lines`, `timestamp` | Cache có phiên bản |

SQLite hoặc file có schema cho prototype; Postgres khi cần truy vấn tiến độ nhiều người. Nếu chỉ chạy local chưa có tài khoản, `learner_id` có thể tạm là ID cục bộ.

## 3. API contract dự kiến

| Endpoint (dự kiến) | Request | Response | Phase |
| --- | --- | --- | --- |
| `GET /health` | không | `{ "status": "ok" }` | 0 |
| `POST /v1/rules/legal-moves` | `{ "fen": "..." }` | `{ "fen": "...", "moves": ["a0a1"], "status": "...", "in_check": false, "checked_general": null }` | 1 · **đã triển khai** |
| `POST /v1/rules/apply-move` | `{ "fen": "...", "move": "a0a1", "history_fens": [] }` | `{ "fen": "...", "moves": [], "status": "...", "in_check": false, "checked_general": null, "repetition_count": 1 }` | 1 · **đã triển khai** |
| `POST /v1/engine/analyze` | `{ "fen": "...", "time_ms": 1000, "depth": 12, "multipv": 3, "job_id": "optional" }` | normalized analysis + provenance, score side-to-move và Đỏ | 2 · **đã triển khai** |
| `POST /v1/engine/best-move` | như analyze | analysis + best ICCS move, cùng giới hạn và provenance | 2 · **đã triển khai** |
| `POST /v1/engine/stop` | `{ "job_id": "..." }` | `{ "stopped": true, "job_id": "..." }` | 2 · **đã triển khai** |
| `GET /v1/openings?include_experimental=false` | query tùy chọn | danh mục published; experimental chỉ hiện khi yêu cầu rõ | 3 · **đã triển khai** |
| `GET /v1/openings/{id}?include_experimental=false` | ID + query tùy chọn | metadata + graph positions/edges + lines + sources | 3 · **đã triển khai** |
| `GET /v1/openings/{id}/branches?position_key=...&include_experimental=false` | canonical position key + query tùy chọn | outgoing legal transitions + annotations có nguồn | 3 · **đã triển khai** |
| `GET /v1/lessons/{id}?include_experimental=false` | ID + query tùy chọn | schema-validated lesson, exercise, version và review status | 3 · **đã triển khai** |
| `POST /v1/tutor/hint` | `{ lesson_id, exercise_id, fen, hint_level, previous_hint_level, learner_move?, learner_reason?, include_experimental? }` | `TutorAnswer`: claims có evidence refs, verified candidate moves, uncertainty, provider/fallback, trace ID | 4 · **đã triển khai** |
| `POST /v1/learning/games` | local learner/game IDs + FEN + move history | RulesService-validated and persisted positions | 5 · **implemented** |
| `GET /v1/learning/games/{game_id}?learner_id=...` | owned game ID + local learner ID | saved start FEN, ICCS move history, position history and ended flag for local resume | 6 · **implemented** |
| `POST /v1/learning/attempts` | attempt + exercise version + idempotency ID | observable rubric outcome + review date | 5 · **implemented** |
| `GET /v1/learning/progress/{learner_id}` | local learner ID | skill samples, focus alignment and due count | 5 · **implemented** |
| `GET /v1/learning/next/{learner_id}` | local learner ID + experimental opt-in | transparent heuristic recommendation | 5 · **implemented** |
| `GET /v1/learning/reviews/{learner_id}` | local learner ID | due exercises and schedule reason | 5 · **implemented** |
| `GET /v1/learning/games/{game_id}/rematch?learner_id=...` | owned game ID | up to three sampled engine score-drop checkpoints | 5 · **implemented** |
| `GET /v1/learning/export/{learner_id}` / `DELETE /v1/learning/progress/{learner_id}` | local learner ID | JSON export / delete all local data | 5 · **implemented** |

Opening knowledge được import và kiểm tra từ YAML/JSON bằng `backend/app/knowledge/service.py`. Position key gồm placement FEN và lượt đi, không gồm bộ đếm nước; graph gộp vị trí chuyển vị nhưng line vẫn giữ sequence riêng. Migration SQLite nằm ở `backend/app/knowledge/migrations/001_opening_knowledge.sql`. Catalog và endpoint detail mặc định chỉ trả nội dung `published`; nội dung `experimental` chỉ trả khi caller đặt `include_experimental=true`. Draft/needs-review không được trả ra API.

Các response rules, opening và tutor dùng schema Pydantic. Tutor chỉ nhận FEN hợp lệ; nước người học gửi và mọi candidate/PV được đối chiếu với RulesService. Tầng hint phải đi tuần tự; tầng 3 yêu cầu một nước thử và phần giải thích của người học. Production chỉ nạp nội dung `reviewed`/`published`; dữ liệu experimental cần opt-in chỉ ở local. `APP_ENV=production` từ chối experimental dù request bật cờ.

Provider mặc định là `none`, không gọi mạng và dùng hint đã soạn trong lesson. `LLM_PROVIDER=mock` dành cho kiểm thử. Provider tùy chọn `openai_compatible` cần `LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY` ở backend; chưa chọn nhà cung cấp hay cấu hình API key thật. Lời gọi lỗi chuyển về fallback và không trả body/header upstream. Provider cache 20 phút, tối đa 20 request chưa cache mỗi client/phút. Hint từ tầng 2 có thể kèm PV engine giới hạn 400 ms/depth 8/MultiPV 2; nếu engine không sẵn sàng, response nêu rõ.

Phase 5 learner ID là UUID ngẫu nhiên trong `localStorage`, không phải tài khoản/xác thực. SQLite mặc định ở `.local-data/learning.sqlite3`, ngoài source control. Endpoint learning bị tắt với `APP_ENV=production` đến khi có xác thực và phân quyền. Export và xóa áp dụng cho toàn bộ learner ID. `LEARNING_REVIEW_INTERVALS_DAYS` cấu hình chuỗi ngày (mặc định `1,3,7`).

Attempt version được giữ nguyên trong lịch sử; submission cũ cùng idempotency ID trả đúng receipt cũ, còn submission mới với version cũ bị từ chối. Rubric tự động chỉ ghi 1 điểm khi nước khớp trọng tâm do bài tập tác giả đánh dấu và 1 điểm khi có nhập lý do; văn bản lý do, chất lượng tư duy và các mục tự kiểm tra không được chấm tự động. Skill dashboard ghi cỡ mẫu và số lượt khớp trọng tâm, không quy đổi Elo/mastery.

## 4. Ví dụ response Tutor đúng dạng

```json
{
  "contract_version": "1",
  "trace_id": "<server-generated id>",
  "context_digest": "<sha256 of normalized tutor context>",
  "lesson_id": "lesson-001",
  "exercise_id": "exercise-01",
  "position_fen": "<validated FEN>",
  "hint_level": 1,
  "question": "Đối thủ vừa tạo ra mối đe dọa nào?",
  "claims": [{"text": "Hãy quan sát mối đe dọa.", "evidence_refs": ["lesson:lesson-001:exercise:exercise-01"]}],
  "candidate_moves": [],
  "evidence": [{"ref": "lesson:lesson-001:exercise:exercise-01", "kind": "lesson", "review_status": "published"}],
  "uncertainty": "Chưa có đủ phân tích để xếp hạng nước đi.",
  "provider": "fallback",
  "fallback": true,
  "engine_status": "not_requested"
}
```

Những chuỗi trong ngoặc nhọn là placeholder, **không phải dữ liệu cờ thật**. Xây dựng fixture hợp lệ khi code Phase 1–4.

## 5. Kiểm tra contract tối thiểu

- FEN sai trả lỗi có cấu trúc, không làm crash server.
- Nước đi trái luật có mã lỗi dự đoán được.
- Mọi engine line đi qua bộ xác nhận nước đi; line lỗi không lọt vào tutor.
- Mỗi line có `score_perspective: side_to_move`; response cũng kèm `score_cp_red`/`mate_in_red`, engine ID/version, protocol, vị trí, limits và thời gian chạy.
- `time_ms` giới hạn 100–5000 ms, `depth` 1–20, `multipv` 1–3; engine process local tái sử dụng và request quá tải bị từ chối.
- Response có phiên bản/hợp đồng test để frontend không phụ thuộc vào text lỗi ngẫu nhiên.
- Chuẩn hóa score và orientation bằng fixtures đỏ/đen.
- Mỗi tutor claim phải dẫn evidence ref tồn tại; ở hint tier 1–2 không được tiết lộ ICCS answer move.
- Từ chối provider candidate không có trong tập nước đã kiểm chứng; câu thắng bắt buộc cần mate evidence.
- Không log FEN, learner reason, prompt, API key hoặc body lỗi upstream.
