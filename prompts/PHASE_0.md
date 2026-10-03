# PROMPT THỰC THI — PHASE 0: Bootstrap & Local Dev

> Dùng file này làm yêu cầu công việc khi đã tới đúng Phase 0. File này không chứng minh rằng phase trước đã hoàn tất.

Bạn là Codex, Senior Full-stack Engineer kiêm Software Architect và người triển khai nền tảng giáo dục cờ tướng. **Chỉ thực hiện Phase 0.**

## Trình tự bắt buộc

1. Đọc `START_HERE.md`, `AGENTS.md`, `state/PROJECT_STATUS.md`, `state/HANDOFF.md` và **toàn bộ** `plans/PHASE_0.md`.
2. Kiểm tra cổng bắt đầu Phase 0 từ `state/PROJECT_STATUS.md`; với Phase > 0 phải có Phase trước `DONE` cùng bằng chứng. Nếu không đạt, **dừng phần code phase này** và ghi blocker thay vì bỏ qua.
3. Đọc tài liệu domain trong mục “Tài liệu phải đọc” của plan; quan sát source code hiện tại trước khi sửa.
4. Triển khai theo các mảnh nhỏ có test, tránh thay framework, tránh code không thuộc phase.
5. Chạy build/lint/typecheck/test và kiểm thử tích hợp có thể chạy trong môi trường hiện tại. Báo cáo lệnh thật và kết quả.
6. Cập nhật `state/PROJECT_STATUS.md`, `state/HANDOFF.md`, `state/SESSION_LOG.md`; cập nhật `state/DECISIONS.md` nếu có quyết định mới. **Không tự chạy phase tiếp theo.**

## Đầu việc giai đoạn này

**Tạo nền dự án chạy cục bộ nhưng không viết lại bộ tài liệu Markdown đã có.**

- [ ] Kiểm tra `AGENTS.md`, `START_HERE.md` và các file docs đã có, **không ghi đè**; nhận diện repo chưa có code.
- [ ] Tạo `frontend/` bằng React + TypeScript + Vite + Tailwind CSS, UI trang chủ có đường dẫn placeholder đến các module chưa triển khai (không giả nút hoạt động).
- [ ] Tạo `backend/` bằng Python/FastAPI với `GET /health` trả `{ "status": "ok" }`; thiết lập test `pytest` cho route này.
- [ ] Thêm cấu hình lint/type-check + một smoke test frontend. Chọn npm và một cách quản lý Python (venv/pip hoặc uv), ghi rõ lệnh chạy trên Windows PowerShell và Ubuntu.
- [ ] Tạo `.env.example` không có secret; khai báo biến môi trường tương lai nhưng **chưa gọi LLM**.
- [ ] Thiết lập CORS chỉ cho local; giữ modules `api`, `rules`, `engine`, `knowledge`, `tutor`, `learning` ở mức skeleton cần thiết, không overengineer.
- [ ] Cập nhật README theo lệnh thực tế chỉ khi khác hướng dẫn; giữ link điều hướng hoạt động. Không tạo Git.

## Điều kiện để được ghi DONE

- [ ] Tại repo root có lệnh rõ ràng để chạy frontend và backend local.
- [ ] `GET /health` trả JSON và HTTP 200 trong test (và bằng curl/manual nếu môi trường cho phép).
- [ ] `npm run build` và `npm run lint`/type-check (hoặc script thay thế được tài liệu hóa) chạy thành công.
- [ ] `pytest` chạy thành công; các lệnh thực sự được ghi trong handoff.
- [ ] Không có engine, provider trả phí, tài khoản hay database production phát sinh ngoài scope.

## Giới hạn cứng

- Tạo lại AGENTS, README, START_HERE
- Viết luật cờ hoặc gọi AI
- Cài Postgres/Redis/Celery ngay
- Không khởi tạo/commit/push Git, không cài dịch vụ có phí, không tự triển khai production.
- Không sửa hoặc làm mất tài liệu điều hướng đã được chuẩn bị. Những thay đổi cần thiết phải cập nhật link liên quan.
- Không báo “thành công” nếu test chưa chạy hoặc môi trường thiếu dependency; khi bị chặn ghi rõ trạng thái thực.

## Định dạng báo cáo cuối phiên

1. **Đã thực hiện:** file/module/behavior nào mới hoặc thay đổi.
2. **Bằng chứng:** lệnh test/build/lint, kết quả, manual test nào đã thực hiện.
3. **Điều kiện nghiệm thu:** từng điều kiện đã đạt/chưa đạt.
4. **Rủi ro/blockers:** những việc chưa kiểm chứng (đặc biệt giấy phép, luật cờ, engine, nguồn khai cuộc).
5. **Trạng thái:** Phase 0 `DONE`, `IN_PROGRESS` hay `BLOCKED`, kèm lý do; chỉ dẫn cho phiên sau.
