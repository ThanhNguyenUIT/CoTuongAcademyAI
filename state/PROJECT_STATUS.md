# PROJECT STATUS — nguồn sự thật tiến độ

**Cập nhật:** 2026-10-03 · **Tình trạng:** prototype đã có Phase 0–5; Phase 6 `IN_PROGRESS`. Mục tiêu sử dụng hiện được xác nhận là học cá nhân trên máy tính, không chia sẻ app.

**Hướng dẫn học 2026-10-03:** thêm [`HUONG_DAN_HOC_CO_TUONG.md`](../HUONG_DAN_HOC_CO_TUONG.md), đối chiếu UI và học liệu thật: giải thích từng khối, ICCS/FEN, tải hai thế bài tập, gợi ý 3 tầng, đọc engine, luyện dự đoán/đánh lại, dashboard và nhật ký. Ghi rõ Board/Opening Lab chưa đồng bộ tự động, tutor chỉ gắn bài tập trên UI, 2/2 chưa chấm chất lượng lý do và nội dung còn experimental. Hai FEN, năm chuỗi lựa chọn/phản ứng và chuyển vị A/B được kiểm tra bằng rules; backend liên quan 31 passed, frontend 6 passed, lint/typecheck PASS. Chỉ sửa Markdown, không thêm tính năng hoặc đánh dấu tăng trình độ/đóng phase.

**Hướng dẫn chạy app 2026-10-03:** xác nhận API đang chạy trả `503 engine_unavailable` vì chưa đặt `ENGINE_COMMAND`. Thêm [`HUONG_DAN_CHAY_APP.md`](../HUONG_DAN_CHAY_APP.md) và bổ sung README để đặt biến trước khi mở app, restart trong cùng terminal và bấm nút cho mỗi lượt Đen. Pikafish integration 2/2 PASS; HTTP thử tại cổng 8765 xác nhận Đỏ đi → máy trả nước Đen → rules áp dụng hợp lệ. Backend 100 passed/2 skipped (dùng thư mục tạm trong workspace), frontend 6 passed, lint/typecheck/build PASS. Chỉ sửa tài liệu; chưa xác nhận thao tác browser hoặc việc người dùng restart phiên tại cổng 8000. Phase 6 giữ `IN_PROGRESS`.

**Kiểm tra hiện trạng 2026-09-30:** đối chiếu source và chạy lại backend 100 passed/2 skipped, frontend 6 passed, lint/typecheck/build và pip check PASS; chạy riêng tích hợp Pikafish thật 2/2 PASS. Không sửa source hoặc chuyển phase. UI còn nhãn “PHASE 5” ở `frontend/src/App.tsx`; đây là nhãn cũ, không phản ánh phase hiện hành. Chưa kiểm thử lại browser/manual refresh-resume/import/rematch trong phiên này.

**Rà tài liệu cải thiện 2026-09-30:** kế hoạch cụ thể cho app PC là [`plans/PHASE_6_LOCAL_APP_REVIEW_PLAN.md`](../plans/PHASE_6_LOCAL_APP_REVIEW_PLAN.md); phần ưu tiên đã triển khai, còn manual flow và đo HTTP/browser/tutor/dashboard. Hướng dài hạn nằm trong PRODUCT_SPEC, CONTENT_GUIDE và ARCHITECTURE; không coi đó là phê duyệt mở scope hoặc kế hoạch Phase 7. Phiên rà tài liệu không sửa source/chạy lại tests.

**Rà `.gitignore` 2026-10-03:** quy tắc hiện tại bao phủ dependency, build frontend, môi trường Python, cache, engine và dữ liệu học mặc định. Kiểm tra bằng Git xác nhận còn thiếu `.env.*`, Python bytecode ngoài `__pycache__`, coverage và log; `.idea` chỉ bỏ qua một số file nhờ ignore riêng. Chỉ đề xuất bổ sung, chưa sửa `.gitignore`; `.env.example` và `package-lock.json` vẫn được giữ. Git metadata hiện đã tồn tại, chưa có file tracked; không khởi tạo/commit/push. Phase 6 giữ `IN_PROGRESS`.

**Bổ sung `.gitignore` 2026-10-03:** theo yêu cầu tiếp nối, đã thêm `.env.*` (giữ `.env.example`), bytecode Python, coverage, log và `.idea/`. Gỡ riêng năm file .idea đã được staged khỏi index bằng `git rm -r --cached -- .idea`, giữ nguyên trên đĩa. Kiểm tra Git PASS với 22 đường dẫn phải ignore và 5 đường dẫn phải giữ; không sửa source hoặc commit/push. Phase 6 giữ `IN_PROGRESS`.

**Rà cảnh báo IDE 2026-10-03:** SQL thiếu data source là cảnh báo hỗ trợ IDE; hai migration chạy thành công trên SQLite in-memory. Anchor `#home` có đích trong App.tsx, entry `/src/main.tsx` tồn tại và Vite build PASS; throw trong Board được catch để hiển thị lỗi và finally giải phóng trạng thái busy. `npm run build` (gồm TypeScript) và `npm run lint` PASS; không sửa source/cấu hình IDE, chưa kiểm tra tương tác browser. Phase 6 giữ `IN_PROGRESS`.

## Quy tắc trạng thái

- `LOCKED`: chưa được bắt đầu vì phase trước chưa DONE.
- `PENDING`: đủ điều kiện bắt đầu, nhưng chưa làm.
- `IN_PROGRESS`: đang làm, chưa thỏa hết exit criteria.
- `BLOCKED`: bị chặn, có blocker cụ thể trong HANDOFF.
- `DONE`: mọi exit criteria đã đối chiếu và có bằng chứng test/đầu ra.

| Phase | Tên | Status | Bằng chứng nghiệm thu | Việc còn thiếu |
| --- | --- | --- | --- | --- |
| 0 | Bootstrap | `DONE` | Frontend build/lint/typecheck/smoke; pytest `/health`; frontend và backend local trả HTTP 200 | Không còn việc Phase 0 |
| 1 | Board & Rules | `DONE` | Bộ luật/API, board 9×10, FEN/ICCS, replay; backend 29 tests và frontend 3 tests; build/lint/typecheck PASS | Ruleset thi đấu, chiếu/đuổi liên tục và giới hạn không bắt quân là issue trước khi tuyên bố tuân thủ giải đấu |
| 2 | Engine | `DONE` | Pikafish và Fairy-Stockfish Windows artifacts đã chạy thật; UCI, best move/PV, perspective, stop/restart, 3 request dùng 1 process; license/hash ghi trong ADR-007 | Chỉ hỗ trợ mục đích local phi thương mại; không có Elo đã hiệu chuẩn |
| 3 | Opening Lab | `DONE` | Importer YAML/JSON, SQLite schema, graph transposition, API/UI, 3 line và lesson experimental; backend 50 passed (2 engine tests skipped), frontend 5 passed, lint/typecheck/build PASS; browser E2E hoàn tất | Nội dung chưa được biên tập viên cờ tướng duyệt; không có line nào published |
| 4 | AI Tutor | `DONE` | Tutor API/UI, provider mock/OpenAI-compatible, evidence policy, fallback 3 tầng; backend 83 passed, 2 engine integration skipped; 20/20 eval, browser E2E fallback với Pikafish; frontend 5 passed, lint/typecheck/build PASS | Live provider smoke chưa xác minh vì chưa cấu hình credentials; kiến thức hiện vẫn experimental và không được phục vụ ở production |
| 5 | Adaptive Learning | `DONE` | Learning API/UI, local SQLite, taxonomy, lịch ôn, idempotency, rematch; backend 95 passed, 2 skipped; frontend 5 passed; lint/typecheck/build PASS; browser E2E local | Heuristic/rubric đơn giản; chưa có auth/cloud; nội dung vẫn experimental; không có Elo/mastery claim |
| 6 | Release | `IN_PROGRESS` | Readiness/threat/privacy/beta protocol, license inventory, local runbook/backup; npm audit 0; local health 20/20 and engine 12/12; latest backend 100 passed/2 skipped and frontend 6 passed; lint/typecheck/build/pip check PASS; local PC study; resume overwrite fixed with regression coverage; rules/content/game-save optimizations profiled | Full beta/release gate still has cohort/pre-post, distribution rights, full SBOM and deployment rollback items; user scope is private PC learning, so public/mobile work is out of scope. Lesson content remains experimental; full new-game replay and dashboard/UI paths were not further optimized |

**Phase hiện hành:** 6 (`IN_PROGRESS`)

**Prompt cần chạy:** [`prompts/PHASE_6.md`](../prompts/PHASE_6.md)

## Thao tác Codex khi đóng một phase

1. Ghi bằng chứng cụ thể trong `state/HANDOFF.md`; không ghi `DONE` nếu còn test chưa chạy hoặc fail.
2. Đổi đúng một phase thành DONE; đổi phase kế tiếp từ LOCKED thành PENDING, trừ khi có blocker tiền điều kiện rõ ràng.
3. Cập nhật “Phase hiện hành” và đường dẫn prompt mới. Không tự triển khai phase kế tiếp trong phiên vừa nghiệm thu.
4. Nếu phát hiện DONE cũ thiếu chứng cứ, đổi lại `IN_PROGRESS` và ghi rõ nguyên nhân, không xóa lịch sử.
