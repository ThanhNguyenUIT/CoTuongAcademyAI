# SESSION LOG — nhật ký nối thêm qua các phiên Codex

Không xóa các entry cũ; giữ mỗi entry 5–12 dòng, chi tiết test trong `HANDOFF.md`.

## 2026-10-03 — Phase 6 rà cảnh báo IDE | IN_PROGRESS → IN_PROGRESS

- Đối chiếu hai migration SQL, anchor #home, entry Vite và throw/catch của Board theo cảnh báo người dùng gửi.
- Anchor có đích, entry tồn tại; throw được xử lý để hiển thị lỗi và giải phóng busy, không sửa source.
- npm run build (gồm TypeScript), npm run lint và chạy hai migration trong SQLite in-memory đều PASS.
- Tham khảo tài liệu JetBrains/Vite; chưa kiểm tra cấu hình IDE hoặc thao tác browser, không ghi database học thật.
- Phase 6 giữ IN_PROGRESS, không có ADR; lệnh và kết quả ở [`HANDOFF.md`](HANDOFF.md).

## 2026-10-03 — Phase 6 bổ sung `.gitignore` | IN_PROGRESS → IN_PROGRESS

- Sửa .gitignore theo yêu cầu: bỏ qua .env.*, bytecode, coverage, log và .idea; giữ .env.example và các quy tắc cũ.
- Gỡ riêng năm file .idea đã staged khỏi index bằng git rm --cached, giữ nguyên các file trên đĩa.
- Kiểm tra bằng Git/Python PASS: 22 đường dẫn ignore, 5 đường dẫn giữ; xác nhận .idea không còn trong index và file IDE vẫn tồn tại.
- Không đổi runtime hoặc chạy test ứng dụng; không stage thay đổi mới, commit/push hoặc thêm ADR.
- Phase 6 giữ IN_PROGRESS; bằng chứng lệnh ở [`HANDOFF.md`](HANDOFF.md).

## 2026-10-03 — Phase 6 kiểm tra `.gitignore` | IN_PROGRESS → IN_PROGRESS

- Đối chiếu ignore với thư mục thực tế, cấu hình TypeScript và nơi lưu engine/SQLite/backup.
- Git status/check-ignore/ls-files đều exit 0; dependency/build/cache/engine/dữ liệu học mặc định được bỏ qua đúng.
- Còn thiếu ignore cho `.env.*`, bytecode rời, coverage và log; một số file .idea đang untracked. `.env.example` và package-lock vẫn được giữ.
- Chỉ đề xuất bổ sung, không sửa `.gitignore`, source hoặc Git metadata; cập nhật status/handoff theo quy tắc phiên.
- Không chạy test ứng dụng vì không đổi hành vi; Phase 6 giữ IN_PROGRESS, không có ADR mới.
- Lệnh và kết quả trong [`HANDOFF.md`](HANDOFF.md).

## 2026-10-03 — Phase 6 hướng dẫn học và UI | IN_PROGRESS → IN_PROGRESS

- Tạo `HUONG_DAN_HOC_CO_TUONG.md` theo yêu cầu học thực chất thay vì chơi bản năng; thêm link vào README.
- Giải thích UI, ICCS/FEN, hai bài tập thật, gợi ý/engine, luyện dự đoán, đánh lại và nhật ký; có buổi học mẫu cùng lịch bảy buổi.
- Nêu đúng giới hạn Board/Opening Lab, tutor, dashboard, rematch và nội dung experimental; không cam kết tăng Elo hoặc thêm tính năng.
- Kiểm tra FEN/chuỗi nước/chuyển vị/link PASS; backend liên quan 31 passed; frontend 6 passed; lint/typecheck PASS.
- Chỉ sửa Markdown, không chạy lại build/full suite hoặc đo hiệu quả học; Phase 6 giữ IN_PROGRESS, không có ADR mới.
- Lệnh và kết quả thực tế trong [`HANDOFF.md`](HANDOFF.md).

## 2026-10-03 — Phase 6 hướng dẫn chạy app | IN_PROGRESS → IN_PROGRESS

- Xác nhận app tại 8000/5173 mở được nhưng engine trả 503 vì thiếu `ENGINE_COMMAND`.
- Tạo `HUONG_DAN_CHAY_APP.md`, bổ sung README: đặt biến trước khi chạy, cùng terminal, restart phiên cũ, bấm nút cho mỗi lượt Đen và xử lý lỗi thường gặp.
- Không sửa source, tải engine, bật LLM hoặc thay kiến trúc; giữ phiên app của người dùng đang chạy.
- Pikafish integration 2/2 PASS; HTTP smoke riêng 8765 xác nhận nước Đỏ → nước máy Đen → rules áp dụng hợp lệ; server thử đã dừng.
- Backend 100 passed/2 skipped sau đổi basetemp vào workspace; frontend 6 passed; lint/typecheck/build PASS. Các hạn chế sandbox/lần chạy lỗi được ghi trong HANDOFF.
- Chưa kiểm thử browser/manual hoặc xác nhận người dùng đã restart app; Phase 6 vẫn IN_PROGRESS.
- Chi tiết lệnh thật và kết quả trong [`HANDOFF.md`](HANDOFF.md).

## 2026-09-30 — Phase 6 rà tài liệu nâng cấp/cải thiện

- Rà docs/plans/state và điều hướng theo yêu cầu, không sửa source/chạy test mới.
- Tìm thấy kế hoạch cải thiện PC cụ thể ngày 2026-09-28: `PHASE_6_LOCAL_APP_REVIEW_PLAN.md`; phần ưu tiên đã làm, phần profile/manual và tối ưu có điều kiện còn chờ.
- Tìm các định hướng học liệu/sư phạm, Master Campaign, ký pháp Việt Nam và desktop packaging trong PRODUCT_SPEC/CONTENT_GUIDE/ARCHITECTURE.
- Phân biệt định hướng dài hạn, release gates và scope học cá nhân hiện tại; không mở thêm phase hoặc coi tài liệu là phê duyệt triển khai.
- Phase 6 giữ `IN_PROGRESS`; chi tiết nguồn và giới hạn trong [`HANDOFF.md`](HANDOFF.md).

## 2026-09-30 — Phase 6 kiểm tra hiện trạng | IN_PROGRESS → IN_PROGRESS

- Đọc hồ sơ điều hướng, Phase 6 và đối chiếu module/source; xác nhận Phase 0–5 đã DONE ở mức prototype local.
- Không sửa source, mở scope, khởi tạo Git hoặc triển khai; cập nhật trạng thái và bằng chứng kiểm tra.
- Backend 100 passed/2 skipped; frontend 6 passed; lint/typecheck/build và pip check PASS.
- Chạy riêng Pikafish integration 2/2 PASS, gồm legal PV/API provenance, concurrent reuse, stop và crash/restart.
- Ghi nhận UI còn nhãn “PHASE 5”; chưa kiểm thử browser/manual mới hoặc kết nối LLM thật.
- Phase 6 giữ IN_PROGRESS; bước tiếp theo là thử học trên PC và xác nhận refresh/resume/import/rematch. Chi tiết lệnh thật ở [`HANDOFF.md`](HANDOFF.md).

## 2026-09-28 — Phase 6 local logic/performance implementation

- Implemented the prioritized personal-PC slice from `PHASE_6_LOCAL_APP_REVIEW_PLAN.md`: game resume on refresh, owner-scoped saved-game read, and suffix-only validation for incremental saves.
- Consolidated per-position rules analysis, cached validated opening content/graph with file invalidation, removed duplicate tutor PV validation, and separated bounded engine queue wait from search timeout.
- Added backend/frontend regressions and repeatable local profiling. Same-PC medians improved for legal moves (4.179→2.103 ms), apply move (5.757→3.959 ms), and warm opening lookup (104.953→0.312 ms).
- Append to a saved 300-ply game measured 5.111 ms median; full new-game replay at 300 plies remains 412.473 ms. Workload differs from old full-history save baseline and measurements are in-process only.
- Verification: backend 100 passed/2 skipped; frontend 6 passed; lint, typecheck, build, and `pip check` PASS. Full command/output notes are in [`HANDOFF.md`](HANDOFF.md).
- Phase 6 remains `IN_PROGRESS`; no public/mobile work. Next practical step is a short PC manual study flow with refresh/resume/import/rematch and report any concrete UI or learning issue.

## 2026-09-28 — Rà soát logic/performance và lập repair plan

- Đọc lại trạng thái Phase 6, kiến trúc, quality/security, engine license, sources và các luồng UI/backend luật, engine, tutor, knowledge, learning.
- Rà soát tĩnh chỉ; không sửa code, không chạy test/profiler. Chưa có route-level benchmark mới.
- Phát hiện rủi ro overwrite game sau refresh do Board reset về FEN đầu nhưng tái sử dụng game ID đã lưu; ưu tiên thêm resume và regression coverage.
- Nhận diện các việc có lợi hiệu năng: tái sử dụng kết quả rules trong response, cache knowledge/graph có invalidation, tránh replay cả ván sau mỗi nước, bỏ PV validation trùng và sửa timeout/queue semantics.
- Ghi kế hoạch đầy đủ tại [`../plans/PHASE_6_LOCAL_APP_REVIEW_PLAN.md`](../plans/PHASE_6_LOCAL_APP_REVIEW_PLAN.md); điểm số trước/sau phải được đo trên cùng PC.
- Phase 6 giữ `IN_PROGRESS`; mục tiêu phiên sau là characterize/test game resume và benchmark baseline trước khi sửa.

## 2026-09-27 — Làm rõ mục tiêu cá nhân; thử truy cập iPhone

- Chủ dự án xác nhận chỉ học trên app cá nhân, không chia sẻ; chọn tiếp tục dùng trên PC, dừng xử lý mobile hiện tại.
- Vite khởi động được khi bind `192.168.0.147`; frontend mở được trên PC. IP ví dụ ban đầu gây `EADDRNOTAVAIL`.
- iPhone cùng subnet `192.168.0.140` không truy cập được trang dù đã thử hướng dẫn firewall; chưa xác định nguyên nhân, không ghi nhận PASS.
- Không thay đổi source và không chạy automated tests trong lần hỗ trợ này; Phase 6 vẫn `IN_PROGRESS` theo plan hiện hành.
- Bước kế: người dùng học thử lesson trên PC, báo lỗi UI/nội dung để xử lý trong scope local. Chi tiết ở [`HANDOFF.md`](HANDOFF.md).

## 2026-09-27 — Phase 6 Beta, Quality & Release | PENDING → IN_PROGRESS

- Thêm threat/privacy/beta protocol, kiểm kê license/dependency, và runbook start/stop/backup/recovery/rollback local; thêm bounded load smoke và SQLite backup verifier.
- Rà soát xác nhận phạm vi hiện tại chỉ supervised loopback; không có auth beta, quyền phân phối nội dung, cohort thật, pre/post evaluation hay production rollback.
- Nâng Vitest/coverage lên 4.1.11 sau 3 moderate npm advisory; `npm audit` cuối cùng 0 vulnerabilities. `pip check` sạch; npm SBOM chưa tạo được vì thiếu platform-optional WASI package manifests.
- Local smoke: health 20/20 HTTP 200; Pikafish analysis 12/12 HTTP 200, client p95 141.4 ms và engine p95 63 ms; không suy thành beta SLO/capacity.
- Kiểm tra: backend 95 passed/2 skipped; frontend 5 passed; lint/typecheck/build PASS; SQLite backup fixture `integrity_check=ok`.
- Phase 6 giữ `IN_PROGRESS`; chỉ readiness `READY_FOR_APPROVAL` cho local có giám sát. Không publish hoặc bắt đầu thêm phase.
- Chi tiết lệnh, kết quả và blocker tại [`HANDOFF.md`](HANDOFF.md).

## 2026-09-27 — Phase 5 Adaptive Learning & Rematch | IN_PROGRESS → DONE

- Hoàn thiện lưu tiến độ SQLite local, taxonomy 6 kỹ năng, attempt versioned/idempotent, heuristic bài kế tiếp và lịch ôn configurable, dashboard, export/delete và rematch engine.
- Dữ liệu learning bị chặn trong `APP_ENV=production` đến khi có auth; rubric chỉ chấm chọn theo mục tiêu và việc nhập lý do, không khẳng định mastery/Elo.
- Browser E2E: gửi đáp án sai `a9a8` cùng lý do, thấy receipt 1/2 và dashboard/recommendation/due date thay đổi; rematch với engine thật không tự gán lỗi khi không vượt ngưỡng.
- Backend có kiểm thử deterministic cho lịch ôn, hai learner với lỗi khác nhau, cách ly, duplicate/idempotency, content-version conflict, rematch, export/delete.
- Kiểm tra cuối: pytest 95 passed/2 skipped; frontend 5 passed; lint, typecheck, build PASS; HTTP health/frontend/engine smoke PASS.
- Phase 5 được đánh dấu DONE; Phase 6 thành PENDING. Không triển khai Phase 6 trong phiên này.
- Chi tiết lệnh, kết quả và giới hạn tại [`HANDOFF.md`](HANDOFF.md).

## 2026-09-27 — Phase 4 Evidence-grounded AI Tutor | IN_PROGRESS → DONE

- Hoàn thiện Tutor API/UI với schema và provenance, provider mock/OpenAI-compatible, ba hint tuần tự, policy kiểm tra luật/evidence, cache/quota và fallback an toàn.
- Production chỉ lấy nội dung reviewed/published; lesson hiện vẫn experimental. LLM không cấu hình nên live provider smoke chưa xác minh.
- 20 eval đạt 20/20; rà tay engine conflict: claim `b9c7` bị loại khi PV evidence chỉ có `a9a8`; fallback giữ uncertainty.
- Browser E2E local hoàn tất Opening Lab với lựa chọn và lý do người học, nhận đủ ba hint; fallback và Pikafish evidence depth 8 hiển thị.
- Kiểm tra: backend 83 passed, 2 skipped; frontend 5 passed; typecheck, lint và build PASS.
- Phase 5 chuyển `LOCKED → PENDING`; phiên này dừng sau Phase 4.
- Chi tiết command, output, giới hạn và bằng chứng thủ công ở [`HANDOFF.md`](HANDOFF.md).

## 2026-09-27 — Sửa lệnh chạy local trên Windows

- Lần chạy ban đầu dùng Python hệ thống nên thiếu `uvicorn`; bổ sung bước kích hoạt `.venv` vào hướng dẫn engine.
- Tắt Uvicorn `--reload` trong script dev backend vì Windows selector event loop không hỗ trợ subprocess asyncio của UCI.
- Xác minh `npm run dev`: backend và frontend khởi động; health 200, giao diện 200, engine trả `h2e2` cùng 3 PV.
- Ghi rõ cách chạy và giới hạn reload ở README; không thay đổi phase trạng thái.
- Chi tiết lệnh và kết quả ở [HANDOFF.md](HANDOFF.md).

## 2026-09-27 — Phase 3 Opening Lab & First Course | PENDING → IN_PROGRESS → DONE

- Đã thêm schema knowledge, SQLite migration, importer YAML/JSON và validator cho FEN, moves, sources, cycles, annotation, exercise choices/counterplay.
- Tạo graph gộp canonical positions theo board + lượt đi; ba lines minh họa có chuyển vị, API catalog mặc định ẩn nội dung chưa published.
- Xây Opening Lab và chương Learn/Practice: điều hướng graph/lesson, yêu cầu lời giải thích trước khi mở feedback, rubric tự kiểm tra và chuỗi counterplay hợp lệ.
- Nội dung Pháo đầu đối Bình phong mã có nguồn/version nhưng vẫn experimental; chưa được chuyên gia duyệt và không có line published.
- Kiểm tra: backend 50 passed, 2 engine integration skipped; frontend 5 passed; lint/typecheck/build PASS. Browser E2E xác nhận chuyển vị, hoàn thành chương, trả lời sai, xem phản hồi rồi thử lại.
- Thêm ADR-008; Phase 4 chuyển LOCKED → PENDING. Phiên này dừng sau Phase 3.
- Chi tiết command, warnings và giới hạn ở [HANDOFF.md](HANDOFF.md).

## 2026-09-27 — Phase 2 Engine Adapter & Analysis | PENDING → IN_PROGRESS → DONE

- Đã tích hợp UCI adapter quản lý process tái sử dụng, giới hạn threads/hash/thời gian, cancel/stop/restart, chuẩn hóa PV và điểm Đỏ/Đen; thêm API best-move/analyze/stop và giao diện engine local.
- Spike chạy thật trên Pikafish 2026-09-06 và Fairy-Stockfish 14.0.1 XQ; xác minh tọa độ/FEN, 3 biến, concurrent/stop/restart. Chọn Pikafish cho local phi thương mại; binary và NNUE ở thư mục gitignore.
- Ghi ADR-007 với version, download source, license, hash artifact và kết quả; không hiển thị Elo đã hiệu chuẩn.
- Smoke Uvicorn trên `127.0.0.1:8765`: health 200 và Pikafish analysis 200, 3 PV hợp lệ, 491 ms; server đã dừng sau kiểm tra.
- Kiểm tra: pytest 38 passed, 2 integration skip mặc định; integration thật 2/2 cho mỗi engine; npm test 4; lint/typecheck/build PASS.
- Phase 3 chuyển `LOCKED → PENDING`; phiên này dừng sau Phase 2.
- Chi tiết evidence và constraints ở [`HANDOFF.md`](HANDOFF.md), [`docs/ENGINE_LICENSE.md`](../docs/ENGINE_LICENSE.md).

## 2026-09-26 — tạo gói tài liệu (trước khi chạy Codex)

- Status: Phase 0 `PENDING`, Phase 1–6 `LOCKED`.
- Đã tạo: START_HERE, AGENTS, docs, plans, prompts, state.
- Chưa tạo code ứng dụng; chưa chạy bất kỳ test/build ứng dụng nào.
- Phiên sau: yêu cầu Codex đọc `prompts/PHASE_0.md`.

## 2026-09-26 — Phase 0 bootstrap | PENDING → DONE

- Đã thêm React/Vite/Tailwind homepage, FastAPI health route, skeleton domain, lệnh root, `.env.example` và hướng dẫn local.
- Kiểm tra đạt: build, lint, typecheck, Vitest (1), pytest (1), combined dev server, HTTP 200 frontend/backend.
- Không tích hợp luật cờ, engine, LLM, tài khoản hay database; Phase 1 trở thành `PENDING`.
- Chi tiết lệnh và cảnh báo dependency nằm trong [`HANDOFF.md`](HANDOFF.md).
- Phiên sau: đọc `prompts/RESUME.md`, thực hiện Phase 1.

## 2026-09-26 — Phase 1 Board & Rules | IN_PROGRESS → DONE

- Đã thêm backend RulesService/API, FEN/ICCS, board SVG tương tác, history/undo/replay, import/copy FEN và accessibility bàn phím cơ bản.
- Đối chiếu `xiangqi.js` API/license nhưng không dùng runtime; chốt chính sách prototype lặp ở ADR-006, không phán quyết chiếu/đuổi.
- Kiểm tra đạt: `python -m pytest -q` (29); `npm run build`; `npm run lint`; `npm run typecheck`; `npm test` (3 UI tests, gồm hai lượt Đỏ–Đen và tua ván).
- `npm run build` cần quyền ngoài sandbox mặc định vì esbuild bị từ chối đọc thư mục cha workspace; build thực tế đã PASS khi chạy với quyền cần thiết.
- Còn issue trước khi tuyên bố luật thi đấu: chốt ruleset/version; thêm fixtures và phân xử perpetual check/chase, lặp theo bên gây lặp, giới hạn nước không bắt quân. Browser manual interaction chưa xác nhận.
- Phase 2 chuyển `LOCKED → PENDING`; không triển khai engine trong phiên này.
- Chi tiết lệnh, kết quả và giới hạn nằm trong [`HANDOFF.md`](HANDOFF.md); phiên tới bắt đầu qua `prompts/RESUME.md` và Phase 2.

---

## Mẫu cho phiên tiếp theo

`YYYY-MM-DD HH:MM | Phase N | trạng thái trước → sau`

- Đã làm: ...
- Test: `lệnh` → PASS/FAIL/BLOCKED, output tóm tắt ...
- Chưa làm/blocker: ...
- Decision: ADR-... nếu có
- Phiên sau: đọc `prompts/RESUME.md`, kiểm tra `state/HANDOFF.md`
