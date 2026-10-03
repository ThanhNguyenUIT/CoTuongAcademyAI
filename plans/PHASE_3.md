# PHASE 3 — Opening Lab & First Course

**Mục tiêu:** Đồ thị khai cuộc có chuyển vị và 1 chương Pháo đầu đối Bình phong mã được biên soạn/duyệt.

**Điều kiện bắt đầu:** `plans/PHASE_2.md` đã DONE và có bằng chứng test trong `state/HANDOFF.md`.

## Tài liệu phải đọc

- [`START_HERE.md`](../START_HERE.md)
- [`AGENTS.md`](../AGENTS.md)
- [`state/PROJECT_STATUS.md`](../state/PROJECT_STATUS.md)
- [`state/HANDOFF.md`](../state/HANDOFF.md)
- [`docs/PRODUCT_SPEC.md`](../docs/PRODUCT_SPEC.md)
- [`docs/DATA_API.md`](../docs/DATA_API.md)
- [`docs/CONTENT_GUIDE.md`](../docs/CONTENT_GUIDE.md)
- [`docs/QUALITY_SECURITY.md`](../docs/QUALITY_SECURITY.md)

## Checklist triển khai

- [x] Thiết kế schema Position, Edge, Opening, Line, Annotation, Lesson, Exercise và migration. Unique canonical position key (gồm lượt đi), không đồng nhất game state/history với vị trí thuần.
- [x] Viết importer/validator từ YAML/JSON và unit tests; loại bỏ nước đi trái luật, FEN không hợp lệ, chu trình/path sai và nội dung thiếu nguồn.
- [x] Tạo đồ thị/cây khai cuộc cho front-end có điều hướng tiến/lùi, highlight biến và nhận diện chuyển vị nhiều đường vào cùng vị trí.
- [x] Biên soạn 1 chương MVP Pháo đầu vs Bình phong mã: 2–3 biến có nguồn, chiến lược, phản công, câu hỏi gợi mở và bài tập transfer. Nếu nguồn chuyên môn chưa được duyệt, trạng thái `draft` và không công bố như sự thật.
- [x] Lưu review status/version/source per annotation; không sao chép nội dung có bản quyền. Nếu thiếu người duyệt, xây prototype bằng bộ bài được đánh dấu experimental.
- [x] Có chế độ Learn/Practice: sau khi xem giải thích yêu cầu học viên dự đoán nước đối thủ và đưa ra lý do.

## Exit criteria — cần bằng chứng, không chỉ báo miệng

- [x] Mỗi đường khai cuộc published là chuỗi nước hợp lệ với rules/engine (khi có). Hiện chưa publish line nào; mọi line experimental đều qua RulesService.
- [x] Test 2 chuỗi khác nhau chuyển vị tới cùng canonical position, sidebar hiển thị rõ hai đường.
- [x] Importer từ chối dữ liệu giả/mất nguồn/illegal; draft không xuất hiện ở danh sách published.
- [x] Manual end-to-end: hoàn thành một chương, sai một câu, xem phản công, quay lại thử phương án khác.
- [x] Có nguồn/biên tập viên duyệt hoặc nội dung giới hạn là experimental được nêu rõ. Nguồn có lưu; nội dung hiện experimental vì chưa có biên tập viên.

## Deliverables

- Knowledge graph và importer
- Opening Lab tương tác
- Một chương học đầu-cuối với rubric

## Không làm trong giai đoạn này

- Import toàn bộ thư viện trước khi chất lượng mẫu được kiểm tra
- Lưu mọi biến như nhánh tuyến tính trùng lặp
- Phát hành annotations do chatbot tự bịa

## Quy trình đóng giai đoạn

1. Đối chiếu từng ô exit criteria với file/test/chức năng thực tế.
2. Chạy test/lint/build đúng script đã có; ghi lệnh, mã thoát và điểm chưa đạt vào `state/HANDOFF.md`.
3. Cập nhật `state/DECISIONS.md` nếu có quyết định kiến trúc/giấy phép, và `state/SESSION_LOG.md` một mục.
4. Chỉ đánh dấu Phase 3 là `DONE` khi đã đủ điều kiện; nếu thiếu thì `IN_PROGRESS` hoặc `BLOCKED`, ghi blocker cụ thể. Không tự động chạy phase 4.

**Đầu mối bước tiếp theo:** Phase 4 dùng position, annotation và engine evidence để giảng dạy; không cần RAG/vector DB nếu chưa cần.

**Prompt thực thi:** [`prompts/PHASE_3.md`](../prompts/PHASE_3.md).
