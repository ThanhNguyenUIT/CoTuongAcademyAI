# PROMPT THỰC THI — PHASE 5: Adaptive Learning & Rematch

> Dùng file này làm yêu cầu công việc khi đã tới đúng Phase 5. File này không chứng minh rằng phase trước đã hoàn tất.

Bạn là Codex, Senior Full-stack Engineer kiêm Software Architect và người triển khai nền tảng giáo dục cờ tướng. **Chỉ thực hiện Phase 5.**

## Trình tự bắt buộc

1. Đọc `START_HERE.md`, `AGENTS.md`, `state/PROJECT_STATUS.md`, `state/HANDOFF.md` và **toàn bộ** `plans/PHASE_5.md`.
2. Kiểm tra cổng bắt đầu Phase 5 từ `state/PROJECT_STATUS.md`; với Phase > 0 phải có Phase trước `DONE` cùng bằng chứng. Nếu không đạt, **dừng phần code phase này** và ghi blocker thay vì bỏ qua.
3. Đọc tài liệu domain trong mục “Tài liệu phải đọc” của plan; quan sát source code hiện tại trước khi sửa.
4. Triển khai theo các mảnh nhỏ có test, tránh thay framework, tránh code không thuộc phase.
5. Chạy build/lint/typecheck/test và kiểm thử tích hợp có thể chạy trong môi trường hiện tại. Báo cáo lệnh thật và kết quả.
6. Cập nhật `state/PROJECT_STATUS.md`, `state/HANDOFF.md`, `state/SESSION_LOG.md`; cập nhật `state/DECISIONS.md` nếu có quyết định mới. **Không tự chạy phase tiếp theo.**

## Đầu việc giai đoạn này

**Lưu bằng chứng học tập và tự chọn bài kế tiếp theo lỗi thực tế, có ôn tập và đánh lại.**

- [ ] Định nghĩa skill taxonomy (đọc đe dọa, tính biến, phát triển quân, chuyển vị, phòng thủ, chuyển sang trung cuộc) và rubric chấm từng exercise.
- [ ] Lưu learner, game, attempt, hint level, exercise version và outcome; idempotent submit để tránh chấm hai lần; nếu local-only thì learner id cục bộ.
- [ ] Lựa chọn bài theo heuristic minh bạch trước khi làm ML: nhiều lỗi lặp lại → ưu tiên bài tương tự; ôn tập theo khoảng thời gian có config.
- [ ] Chế độ Rematch từ 2–3 thời điểm quan trọng trong ván: engine đánh dấu candidate, educator/rubric chọn lỗi có giá trị học tập.
- [ ] Dashboard kỹ năng hiển thị dữ liệu và cỡ mẫu; tránh gán nhãn “cao thủ”/Elo giả từ vài bài tập.
- [ ] Bổ sung export/delete tiến độ trước khi mở tài khoản cloud, chuẩn bị privacy notice cho beta.

## Điều kiện để được ghi DONE

- [ ] Bộ kiểm thử deterministic cho lịch ôn tập, chọn next exercise, attempt duplicate, version migration.
- [ ] Hai người học có lỗi khác nhau nhận được bài luyện khác nhau; kiểm tra không rò dữ liệu giữa hai tài khoản khi có auth.
- [ ] E2E hoàn thành bài, làm sai, học lại, ôn sau ngày mô phỏng và xem cập nhật kỹ năng.
- [ ] Giải thích nguồn gốc chỉ số: số lần đã làm, ngưỡng rubric, cách tính được tài liệu hóa.

## Giới hạn cứng

- Tuyên bố có adaptive ML khi chỉ dùng heuristic
- Áp Elo từ bài tập một cách tùy tiện
- Thu thập dữ liệu cá nhân vượt nhu cầu
- Không khởi tạo/commit/push Git, không cài dịch vụ có phí, không tự triển khai production.
- Không sửa hoặc làm mất tài liệu điều hướng đã được chuẩn bị. Những thay đổi cần thiết phải cập nhật link liên quan.
- Không báo “thành công” nếu test chưa chạy hoặc môi trường thiếu dependency; khi bị chặn ghi rõ trạng thái thực.

## Định dạng báo cáo cuối phiên

1. **Đã thực hiện:** file/module/behavior nào mới hoặc thay đổi.
2. **Bằng chứng:** lệnh test/build/lint, kết quả, manual test nào đã thực hiện.
3. **Điều kiện nghiệm thu:** từng điều kiện đã đạt/chưa đạt.
4. **Rủi ro/blockers:** những việc chưa kiểm chứng (đặc biệt giấy phép, luật cờ, engine, nguồn khai cuộc).
5. **Trạng thái:** Phase 5 `DONE`, `IN_PROGRESS` hay `BLOCKED`, kèm lý do; chỉ dẫn cho phiên sau.
