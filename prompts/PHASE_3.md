# PROMPT THỰC THI — PHASE 3: Opening Lab & First Course

> Dùng file này làm yêu cầu công việc khi đã tới đúng Phase 3. File này không chứng minh rằng phase trước đã hoàn tất.

Bạn là Codex, Senior Full-stack Engineer kiêm Software Architect và người triển khai nền tảng giáo dục cờ tướng. **Chỉ thực hiện Phase 3.**

## Trình tự bắt buộc

1. Đọc `START_HERE.md`, `AGENTS.md`, `state/PROJECT_STATUS.md`, `state/HANDOFF.md` và **toàn bộ** `plans/PHASE_3.md`.
2. Kiểm tra cổng bắt đầu Phase 3 từ `state/PROJECT_STATUS.md`; với Phase > 0 phải có Phase trước `DONE` cùng bằng chứng. Nếu không đạt, **dừng phần code phase này** và ghi blocker thay vì bỏ qua.
3. Đọc tài liệu domain trong mục “Tài liệu phải đọc” của plan; quan sát source code hiện tại trước khi sửa.
4. Triển khai theo các mảnh nhỏ có test, tránh thay framework, tránh code không thuộc phase.
5. Chạy build/lint/typecheck/test và kiểm thử tích hợp có thể chạy trong môi trường hiện tại. Báo cáo lệnh thật và kết quả.
6. Cập nhật `state/PROJECT_STATUS.md`, `state/HANDOFF.md`, `state/SESSION_LOG.md`; cập nhật `state/DECISIONS.md` nếu có quyết định mới. **Không tự chạy phase tiếp theo.**

## Đầu việc giai đoạn này

**Đồ thị khai cuộc có chuyển vị và 1 chương Pháo đầu đối Bình phong mã được biên soạn/duyệt.**

- [ ] Thiết kế schema Position, Edge, Opening, Line, Annotation, Lesson, Exercise và migration. Unique canonical position key (gồm lượt đi), không đồng nhất game state/history với vị trí thuần.
- [ ] Viết importer/validator từ YAML/JSON và unit tests; loại bỏ nước đi trái luật, FEN không hợp lệ, chu trình/path sai và nội dung thiếu nguồn.
- [ ] Tạo đồ thị/cây khai cuộc cho front-end có điều hướng tiến/lùi, highlight biến và nhận diện chuyển vị nhiều đường vào cùng vị trí.
- [ ] Biên soạn 1 chương MVP Pháo đầu vs Bình phong mã: 2–3 biến có nguồn, chiến lược, phản công, câu hỏi gợi mở và bài tập transfer. Nếu nguồn chuyên môn chưa được duyệt, trạng thái `draft` và không công bố như sự thật.
- [ ] Lưu review status/version/source per annotation; không sao chép nội dung có bản quyền. Nếu thiếu người duyệt, xây prototype bằng bộ bài được đánh dấu experimental.
- [ ] Có chế độ Learn/Practice: sau khi xem giải thích yêu cầu học viên dự đoán nước đối thủ và đưa ra lý do.

## Điều kiện để được ghi DONE

- [ ] Mỗi đường khai cuộc published là chuỗi nước hợp lệ với rules/engine (khi có).
- [ ] Test 2 chuỗi khác nhau chuyển vị tới cùng canonical position, sidebar hiển thị rõ hai đường.
- [ ] Importer từ chối dữ liệu giả/mất nguồn/illegal; draft không xuất hiện ở danh sách published.
- [ ] Manual end-to-end: hoàn thành một chương, sai một câu, xem phản công, quay lại thử phương án khác.
- [ ] Có nguồn/biên tập viên duyệt hoặc nội dung giới hạn là experimental được nêu rõ.

## Giới hạn cứng

- Import toàn bộ thư viện trước khi chất lượng mẫu được kiểm tra
- Lưu mọi biến như nhánh tuyến tính trùng lặp
- Phát hành annotations do chatbot tự bịa
- Không khởi tạo/commit/push Git, không cài dịch vụ có phí, không tự triển khai production.
- Không sửa hoặc làm mất tài liệu điều hướng đã được chuẩn bị. Những thay đổi cần thiết phải cập nhật link liên quan.
- Không báo “thành công” nếu test chưa chạy hoặc môi trường thiếu dependency; khi bị chặn ghi rõ trạng thái thực.

## Định dạng báo cáo cuối phiên

1. **Đã thực hiện:** file/module/behavior nào mới hoặc thay đổi.
2. **Bằng chứng:** lệnh test/build/lint, kết quả, manual test nào đã thực hiện.
3. **Điều kiện nghiệm thu:** từng điều kiện đã đạt/chưa đạt.
4. **Rủi ro/blockers:** những việc chưa kiểm chứng (đặc biệt giấy phép, luật cờ, engine, nguồn khai cuộc).
5. **Trạng thái:** Phase 3 `DONE`, `IN_PROGRESS` hay `BLOCKED`, kèm lý do; chỉ dẫn cho phiên sau.
