# PHASE 0 — Bootstrap & Local Dev

**Mục tiêu:** Tạo nền dự án chạy cục bộ nhưng không viết lại bộ tài liệu Markdown đã có.

**Điều kiện bắt đầu:** Dự án mới; `state/PROJECT_STATUS.md` đang để Phase 0 PENDING. Không có yêu cầu rằng dự án đã có code.

## Tài liệu phải đọc

- [`START_HERE.md`](../START_HERE.md)
- [`AGENTS.md`](../AGENTS.md)
- [`state/PROJECT_STATUS.md`](../state/PROJECT_STATUS.md)
- [`state/HANDOFF.md`](../state/HANDOFF.md)
- [`docs/PRODUCT_SPEC.md`](../docs/PRODUCT_SPEC.md)
- [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md)
- [`docs/QUALITY_SECURITY.md`](../docs/QUALITY_SECURITY.md)

## Checklist triển khai

- [ ] Kiểm tra `AGENTS.md`, `START_HERE.md` và các file docs đã có, **không ghi đè**; nhận diện repo chưa có code.
- [ ] Tạo `frontend/` bằng React + TypeScript + Vite + Tailwind CSS, UI trang chủ có đường dẫn placeholder đến các module chưa triển khai (không giả nút hoạt động).
- [ ] Tạo `backend/` bằng Python/FastAPI với `GET /health` trả `{ "status": "ok" }`; thiết lập test `pytest` cho route này.
- [ ] Thêm cấu hình lint/type-check + một smoke test frontend. Chọn npm và một cách quản lý Python (venv/pip hoặc uv), ghi rõ lệnh chạy trên Windows PowerShell và Ubuntu.
- [ ] Tạo `.env.example` không có secret; khai báo biến môi trường tương lai nhưng **chưa gọi LLM**.
- [ ] Thiết lập CORS chỉ cho local; giữ modules `api`, `rules`, `engine`, `knowledge`, `tutor`, `learning` ở mức skeleton cần thiết, không overengineer.
- [ ] Cập nhật README theo lệnh thực tế chỉ khi khác hướng dẫn; giữ link điều hướng hoạt động. Không tạo Git.

## Exit criteria — cần bằng chứng, không chỉ báo miệng

- [ ] Tại repo root có lệnh rõ ràng để chạy frontend và backend local.
- [ ] `GET /health` trả JSON và HTTP 200 trong test (và bằng curl/manual nếu môi trường cho phép).
- [ ] `npm run build` và `npm run lint`/type-check (hoặc script thay thế được tài liệu hóa) chạy thành công.
- [ ] `pytest` chạy thành công; các lệnh thực sự được ghi trong handoff.
- [ ] Không có engine, provider trả phí, tài khoản hay database production phát sinh ngoài scope.

## Deliverables

- Frontend/backend có thể khởi động ở localhost
- Tài liệu lệnh setup chính xác theo code thật
- Kiểm thử smoke và status phase 0

## Không làm trong giai đoạn này

- Tạo lại AGENTS, README, START_HERE
- Viết luật cờ hoặc gọi AI
- Cài Postgres/Redis/Celery ngay

## Quy trình đóng giai đoạn

1. Đối chiếu từng ô exit criteria với file/test/chức năng thực tế.
2. Chạy test/lint/build đúng script đã có; ghi lệnh, mã thoát và điểm chưa đạt vào `state/HANDOFF.md`.
3. Cập nhật `state/DECISIONS.md` nếu có quyết định kiến trúc/giấy phép, và `state/SESSION_LOG.md` một mục.
4. Chỉ đánh dấu Phase 0 là `DONE` khi đã đủ điều kiện; nếu thiếu thì `IN_PROGRESS` hoặc `BLOCKED`, ghi blocker cụ thể. Không tự động chạy phase 1.

**Đầu mối bước tiếp theo:** Bắt đầu `plans/PHASE_1.md` để xây bàn cờ, luật và kiểm thử; không vội gắn engine.

**Prompt thực thi:** [`prompts/PHASE_0.md`](../prompts/PHASE_0.md).
