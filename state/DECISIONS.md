# DECISIONS — nhật ký kiến trúc và quyết định chưa chốt

Dùng định dạng ADR ngắn: `ID`, ngày, trạng thái (`PROPOSED | ACCEPTED | SUPERSEDED`), bối cảnh, quyết định, hậu quả, bằng chứng. Không viết lại một quyết định cũ không còn đúng; thêm ADR mới thay thế.

## ADR-001 — Phương án công nghệ ban đầu

- Ngày: 2026-09-26
- Trạng thái: `ACCEPTED`
- Phương án: React + TypeScript + Vite/Tailwind frontend; Python/FastAPI backend; modular monolith; local-first development.
- Lý do: giao diện bàn cờ độc lập với thuật toán cờ, backend Python tiện orchestration của engine và AI, dễ giao việc theo phase cho Codex.
- Giới hạn: modular monolith và local-first; chưa benchmark engine, không áp dụng microservices ngay.
- Bằng chứng: Phase 0 triển khai frontend React/TypeScript/Vite/Tailwind và backend FastAPI; npm cho frontend, Python venv + pip cho backend.

## ADR-002 — Chuẩn dữ liệu nước đi

- Trạng thái: `PROPOSED`
- Phương án: dùng FEN + ICCS coordinate nội bộ; xác minh chính xác variant/orientation bằng fixtures giai đoạn 1–2 trước khi ACCEPTED.

## ADR-003 — Engine và NNUE

- Trạng thái: `SUPERSEDED BY ADR-007`
- Cần điền: tên/version engine; binary URL/hash; protocol; nguồn và license weights; mục đích local / SaaS / phân phối desktop; kết quả spike; người duyệt; ngày duyệt.
- Hạn chế đã biết: Pikafish source GPLv3, NNUE chính thức không được sử dụng thương mại khi chưa có phép; Fairy-Stockfish GPLv3, license của artifact/weights cần xét riêng.
- Tham khảo: [`docs/ENGINE_LICENSE.md`](../docs/ENGINE_LICENSE.md).

## ADR-007 — Engine local Phase 2: Pikafish 2026-09-06

- Ngày: 2026-09-27
- Trạng thái: `ACCEPTED — prototype local phi thương mại`
- engine_name: `Pikafish`
- engine_version: `2026-09-06`, release commit `4c17cee`
- download_url: [Pikafish Windows x86-64 universal release](https://github.com/official-pikafish/Pikafish/releases/tag/Pikafish-2026-09-06), archive `Pikafish.2026-09-06.7z`
- binary: `Pikafish-Windows-x86-64-universal.exe`; SHA-256 `0D57D64C212E78F96CBA9E5E4F140D8872F8FAA42EA631A27AB6C5DB08509DA3`; binary license GPLv3 (`Copying.txt` trong archive)
- weights_file: `pikafish.nnue` từ cùng archive; SHA-256 `7D13D73569A9B571BA0EB20CF1596247BC2A42738967E61AFEF6482B231E900E`
- weights_license: điều khoản `NNUE-License.md` kèm release; legal use và không thương mại nếu chưa có phép
- intended_distribution: chỉ chạy local trong prototype, phi thương mại; binary và weights không bundle/redistribute
- protocol: UCI; tọa độ 0–9; adapter đổi FEN active color `r` thành `w`
- compatibility_test_result: PASS; UCI handshake, best move và 3 PV tại vị trí đầu ván hợp lệ theo RulesService; analysis API localhost; 3 request đồng thời dùng một process; stop, restart sau crash; cùng smoke 1000 ms/depth 12/MultiPV 3 đo được 428–467 ms trên máy hiện tại
- alternative_reviewed: Fairy-Stockfish 14.0.1 XQ, commit `433d411`, GPLv3 binary + NNUE Xiangqi tích hợp CC0; UCI rank 1–10 chuyển đúng sang ICCS 0–9; cùng smoke đo được 795–911 ms
- reviewed_by: Codex đã xác minh metadata/license upstream và chạy compatibility smoke; chủ dự án xác nhận phạm vi local, phi thương mại ngày 2026-09-27
- review_date: 2026-09-27
- Lý do: chọn release Pikafish mới hơn và độ trễ smoke thấp hơn trên máy hiện tại; tách binary/weights khỏi source và chỉ cho phép người dùng chọn rõ qua `ENGINE_COMMAND`.
- Hệ quả: đổi sang phân phối app, dịch vụ, hoặc mục đích thương mại cần review giấy phép mới và thay weights nếu cần; không khẳng định Elo đã hiệu chuẩn.
- Bằng chứng hash và license: [`docs/ENGINE_LICENSE.md`](../docs/ENGINE_LICENSE.md); artifact lưu ở `.local-engines/` (ignored).

## ADR-008 — Opening Lab knowledge graph và nội dung thử nghiệm

- Ngày: 2026-09-27
- Trạng thái: `ACCEPTED — prototype local; chapter chưa được biên tập viên duyệt`
- Quyết định: Phase 3 lưu học liệu YAML có schema Pydantic và importer dùng `yaml.safe_load`; JSON cũng được chấp nhận. SQLite migration định nghĩa positions, edges, openings, lines, annotations, lessons, exercises và sources. Position key là placement FEN + lượt đi; bộ đếm halfmove/fullmove không tham gia canonical identity. Đồ thị gộp position chuyển vị nhưng lines giữ sequence và nhãn riêng.
- Xuất bản: catalog mặc định chỉ liệt kê opening `published`; draft/experimental không được trình bày như nội dung đã duyệt. Frontend local có thể yêu cầu rõ nội dung `experimental` và hiển thị nguồn/version/review status.
- Nội dung mẫu: ba line Pháo đầu đối Bình phong mã và một bài tập là experimental. RulesService xác nhận mọi nước ở line, lựa chọn và phản ứng mẫu; nguồn liên kết giúp người học tra cứu. Chưa có đánh giá của biên tập viên nên không xác nhận chiến lược, độ mạnh hoặc tương đương thực chiến của biến.
- Lý do: kiểm tra được provenance, tính hợp lệ và transposition trước khi mở rộng thư viện; giảm nguy cơ biến diễn giải chưa duyệt thành sự thật.
- Bằng chứng: `backend/tests/test_knowledge.py`, importer `backend/app/knowledge/service.py`, migration `backend/app/knowledge/migrations/001_opening_knowledge.sql`, dữ liệu `backend/app/knowledge/data/cannon-vs-screen-horse.yaml`.

## ADR-004 — Luật thi đấu

- Trạng thái: `SUPERSEDED BY ADR-006`
- Cần điền ruleset/reference/version, test cho chiếu liên tục/đuổi liên tục/lặp lại. Không tuyên bố đầy đủ luật giải đấu khi chưa có fixtures.

## ADR-006 — Luật prototype Phase 1 và chính sách lặp

- Ngày: 2026-09-26
- Trạng thái: `ACCEPTED — chỉ cho prototype local; chưa phải luật thi đấu`
- Bối cảnh: Phase 1 cần backend xác nhận nước hợp lệ và xử lý lặp mà không tự đoán bên thắng khi chưa có kiểm chứng quy tắc chiếu/đuổi.
- Quyết định: tự triển khai Python RulesService làm nguồn sự thật; dùng FEN 10×9 và ICCS cho nước đi. Khi cùng vị trí xuất hiện lần thứ ba trong lịch sử truyền vào, API trả `repetition_review_required` và UI dừng để trọng tài xem xét. Không tự xử thắng/hòa cho perpetual check/chase.
- Lý do chọn: `xiangqi.js` được spike để đối chiếu API, FEN, ICCS, giấy phép BSD-2-Clause và move list ban đầu, nhưng upstream tự ghi nhận FEN validation còn cần cải thiện và API ba lần lặp mặc định không đủ để quyết định vi phạm chiếu/đuổi theo luật giải đấu. Không đưa thư viện đó vào runtime.
- Giới hạn đã biết: chưa chọn phiên bản ruleset thi đấu chính thức; chưa phân xử check/chase, chưa có giới hạn nước không bắt quân; cần kiểm tra lặp theo từng bên và bộ fixtures từ ruleset được chọn trước khi hỗ trợ thi đấu.
- Hệ quả: prototype không được quảng bá là chuẩn giải đấu; ruleset thi đấu phải được chốt trước khi đối kháng hoặc phân xử kết quả chính thức.
- Bằng chứng/nguồn: backend fixtures trong `backend/tests/test_xiangqi_rules.py` và `backend/tests/test_rules_api.py`; [xiangqi.js README/API](https://github.com/lengyanyu258/xiangqi.js), [package/license metadata](https://github.com/lengyanyu258/xiangqi.js/blob/dev/package.json), [Asian Xiangqi Federation rules](https://www.asianxiangqi.org/English/AXFrulesEng.htm).

## ADR-005 — LLM provider & ngân sách

- Ngày: 2026-09-27
- Trạng thái: `ACCEPTED — provider boundary only; no live vendor selected`
- Quyết định: tách `TutorProvider` khỏi `TutorService`; hỗ trợ `none` (mặc định, fallback soạn sẵn), `mock` cho kiểm thử, và adapter tương thích OpenAI Chat Completions qua `LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY`. Secret chỉ ở backend; lỗi upstream được sanitize.
- Chính sách: provider chỉ diễn giải context dạng JSON; chuỗi lesson/learner được coi là untrusted. TutorService kiểm tra schema, provenance, ICCS tokens, candidate moves và engine PV; RulesService vẫn là nguồn sự thật về nước hợp lệ. Cache phản hồi provider 20 phút, quota tối đa 20 request chưa cache/client/phút. Engine hint analysis giới hạn 400 ms/depth 8/MultiPV 2 và cache 45 giây.
- Nội dung: production chỉ dùng `reviewed`/`published`; experimental cần cờ explicit và chỉ dùng ngoài `APP_ENV=production`. Không có tài liệu mẫu hiện tại đã được chuyên gia duyệt.
- Lý do: hoàn thiện MVP local mà không phát sinh phí và vẫn cho phép chủ dự án gắn provider tương thích sau này; API key, model, ngân sách và chính sách dữ liệu của dịch vụ thật cần chủ dự án duyệt riêng trước khi bật.
- Bằng chứng: `backend/app/tutor/providers.py`, `backend/app/tutor/service.py`, prompt snapshot, 20 ca eval. Không có smoke provider thật hoặc API key trong môi trường hiện tại; live integration chưa xác minh.

## ADR-009 — Phase 5 local learning history, rubric và review

- Ngày: 2026-09-27
- Trạng thái: `ACCEPTED — prototype local-only; chưa có auth/cloud`
- Quyết định: dùng SQLite local trong `.local-data/learning.sqlite3` (gitignored), migration `backend/app/learning/migrations/001_learning.sql`. Browser giữ learner/game UUID; API ghi game history sau khi backend re-apply toàn bộ move bằng RulesService, attempt có idempotency ID, hint level, answer, rubric self-check, game ID và exercise version. Mỗi learner được cascade export/delete riêng.
- Taxonomy gồm đọc mối đe dọa, tính biến, phát triển quân, chuyển vị, phòng thủ, chuyển sang trung cuộc. Legacy exercise tags map tường minh. Heuristic chọn due exercise trước, sau đó lặp lỗi nhiều lần, rồi bài chưa làm; mặc định interval ôn 1/3/7 ngày và configurable qua env.
- Rubric MVP chỉ tự chấm hai observables: nước có khớp trọng tâm do nội dung tác giả chỉ ra (1 điểm) và lời giải thích có được nhập (1 điểm). Không semantic-grade free text, không tự suy ra mastery/Elo. Dashboard luôn hiện sample size.
- Rematch lấy mẫu tối đa 3 ply từ một game đã lưu; engine so sánh eval theo Red, đánh dấu checkpoint nếu bên vừa đi mất ít nhất 100 cp; người học tự chọn checkpoint để replay. Mốc này là heuristic, không được gắn nhãn “blunder”/lỗi chuyên môn.
- Privacy: service không log câu trả lời; các route Phase 5 từ chối khi `APP_ENV=production` cho tới khi có auth/authz, do local UUID không phải credential. Export JSON và DELETE learner cascade gồm game/attempt/schedule.
- Lý do: tạo vòng lặp cá nhân hóa giải thích được trên một chương mà không dựng ML, tài khoản hoặc cloud; giữ dữ liệu người học cục bộ.
- Bằng chứng: `backend/app/learning/`, `backend/tests/test_learning.py`, frontend `LearningDashboard.tsx` và Board rematch; giới hạn còn lại ghi tại `state/HANDOFF.md`.
