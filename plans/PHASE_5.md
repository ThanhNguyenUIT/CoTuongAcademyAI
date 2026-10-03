# PHASE 5 — Adaptive Learning & Rematch

**Mục tiêu:** Lưu bằng chứng học tập và tự chọn bài kế tiếp theo lỗi thực tế, có ôn tập và đánh lại.

**Điều kiện bắt đầu:** `plans/PHASE_4.md` đã DONE và có bằng chứng test trong `state/HANDOFF.md`.

## Tài liệu phải đọc

- [`START_HERE.md`](../START_HERE.md)
- [`AGENTS.md`](../AGENTS.md)
- [`state/PROJECT_STATUS.md`](../state/PROJECT_STATUS.md)
- [`state/HANDOFF.md`](../state/HANDOFF.md)
- [`docs/PRODUCT_SPEC.md`](../docs/PRODUCT_SPEC.md)
- [`docs/DATA_API.md`](../docs/DATA_API.md)
- [`docs/QUALITY_SECURITY.md`](../docs/QUALITY_SECURITY.md)
- [`docs/CONTENT_GUIDE.md`](../docs/CONTENT_GUIDE.md)

## Checklist triển khai

- [x] Định nghĩa skill taxonomy (đọc đe dọa, tính biến, phát triển quân, chuyển vị, phòng thủ, chuyển sang trung cuộc) và rubric chấm từng exercise.
- [x] Lưu learner, game, attempt, hint level, exercise version và outcome; idempotent submit để tránh chấm hai lần; nếu local-only thì learner id cục bộ.
- [x] Lựa chọn bài theo heuristic minh bạch trước khi làm ML: nhiều lỗi lặp lại → ưu tiên bài tương tự; ôn tập theo khoảng thời gian có config.
- [x] Chế độ Rematch từ 2–3 thời điểm quan trọng trong ván: engine đánh dấu candidate, educator/rubric chọn lỗi có giá trị học tập.
- [x] Dashboard kỹ năng hiển thị dữ liệu và cỡ mẫu; tránh gán nhãn “cao thủ”/Elo giả từ vài bài tập.
- [x] Bổ sung export/delete tiến độ trước khi mở tài khoản cloud, chuẩn bị privacy notice cho beta.

## Exit criteria — cần bằng chứng, không chỉ báo miệng

- [x] Bộ kiểm thử deterministic cho lịch ôn tập, chọn next exercise, attempt duplicate, version migration.
- [x] Hai người học có lỗi khác nhau nhận được bài luyện khác nhau; kiểm tra cách ly dữ liệu theo learner ID cục bộ (xác thực nhiều tài khoản chưa thuộc phase này).
- [x] E2E hoàn thành bài, làm sai, học lại, ôn sau ngày mô phỏng và xem cập nhật kỹ năng; lịch ngày mô phỏng được kiểm tra deterministic trong backend, UI được smoke trên dữ liệu thật local.
- [x] Giải thích nguồn gốc chỉ số: số lần đã làm, ngưỡng rubric, cách tính được tài liệu hóa.

## Deliverables

- Learning data + dashboard
- Rematch và ôn tập
- Test heuristic + privacy basics

## Không làm trong giai đoạn này

- Tuyên bố có adaptive ML khi chỉ dùng heuristic
- Áp Elo từ bài tập một cách tùy tiện
- Thu thập dữ liệu cá nhân vượt nhu cầu

## Quy trình đóng giai đoạn

1. Đối chiếu từng ô exit criteria với file/test/chức năng thực tế.
2. Chạy test/lint/build đúng script đã có; ghi lệnh, mã thoát và điểm chưa đạt vào `state/HANDOFF.md`.
3. Cập nhật `state/DECISIONS.md` nếu có quyết định kiến trúc/giấy phép, và `state/SESSION_LOG.md` một mục.
4. Chỉ đánh dấu Phase 5 là `DONE` khi đã đủ điều kiện; nếu thiếu thì `IN_PROGRESS` hoặc `BLOCKED`, ghi blocker cụ thể. Không tự động chạy phase 6.

**Đầu mối bước tiếp theo:** Phase 6 tập trung chất lượng/phát hành chứ không tự mở rộng toàn bộ khai cuộc.

**Prompt thực thi:** [`prompts/PHASE_5.md`](../prompts/PHASE_5.md).
