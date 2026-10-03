# Product specification — Xiangqi AI Academy

**Trạng thái:** prototype local đã hoàn tất Phase 0–5; Phase 6 hiện là beta readiness/release, chưa mở public.

## 1. Tầm nhìn và đối tượng

Dạy người **đã biết luật di chuyển cơ bản** trở thành người có khả năng đọc thế trận, hiểu và vận dụng khai cuộc, tính toán phương án, phòng ngự và lập kế hoạch từ khai cuộc sang trung cuộc. Hướng học từ cơ bản → trung cấp → nâng cao bằng bài học có kiểm chứng và bài tập chuyển giao kiến thức.

### Jobs to be done

- “Tôi đã biết đi quân nhưng không biết nên phát triển quân nào trong 10–15 nước đầu.”
- “Tôi học thuộc khai cuộc nhưng khi đối phương đi khác bài thì không biết làm gì.”
- “Tôi thường chỉ nhận ra sai lầm khi mất quân; muốn tập nhìn mối đe dọa trước khi đi.”
- “Sau mỗi ván, tôi muốn biết 2–3 lỗi quan trọng và có bài tập ôn lại.”

## 2. Vòng lặp học tập bắt buộc

1. **Quan sát**: người học mô tả mục tiêu, đe dọa, quân chưa phát triển.
2. **Dự đoán**: chọn nước đi **và** chỉ ra 1–3 phản ứng có khả năng của đối thủ.
3. **Đối kháng**: máy chọn phản ứng theo mục tiêu bài học hoặc đánh giá engine.
4. **Giải thích**: hiển thị bằng chứng từ engine/giáo trình; ưu tiên câu hỏi gợi mở trước khi mở đáp án.
5. **Luyện lại**: cùng một ý tưởng trong thế cờ khác; ôn tập sau khoảng thời gian phù hợp.

Một “nước đúng” không chứng minh rằng đã hiểu. Điều kiện qua bài cần gồm giải thích, xử lý phản công và vận dụng ở biến chưa học.

## 3. Game modes và phạm vi

| Mode | Mục tiêu | Thời điểm triển khai |
| --- | --- | --- |
| Board & Practice | Bàn cờ 9×10, nước hợp lệ, history, undo, import/export FEN | Phase 1 |
| Engine Match & Analysis | Đánh với máy, phân tích vài biến, dừng/cancel | Phase 2 |
| Opening Lab | Cây/đồ thị khai cuộc, biến chính/phụ, đổi thứ tự nước | Phase 3 |
| AI Coach | Hỏi “vì sao”, gợi ý nhiều tầng, giải thích theo bằng chứng | Phase 4 |
| Rematch & Spaced Review | Tái đấu từ sai lầm, ôn tập dựa trên kết quả | Phase 5 |
| Master Campaign | Các phong cách đối kháng, hành trình kỹ năng | Sau Phase 6; cần quyết định sản phẩm riêng |

Phase 1 hiện là prototype board/rules/replay local. Backend xác nhận nước đi hợp lệ và board hỗ trợ chơi/tua ván. Quy tắc lặp chiếu/đuổi chưa đủ để tuyên bố tuân thủ luật thi đấu; xem [`state/HANDOFF.md`](../state/HANDOFF.md) và ADR-006.

## 4. MVP bắt buộc

**Một chương khai cuộc hoàn chỉnh trước khi mở rộng thư viện**. Gợi ý: Pháo đầu đối Bình phong mã. Phần kiến thức **không** được phát hành bằng cách tự tạo hàng chục biến không nguồn.

MVP phải cho phép: vào bài học → quan sát ý tưởng → chọn phương án → xem phản công hợp lệ → nhận gợi ý AI → đánh lại → hoàn thành bằng kiểm tra hiểu chứ không chỉ nhớ nước. Có thể dùng giao diện tiếng Việt trước; kiến trúc dữ liệu cho phép i18n sau này.

## 5. Nguyên tắc UX

- Bố cục desktop: bàn cờ chính; sidebar hiển thị cây khai cuộc/bài học; thanh dưới hoặc panel phải dành cho AI Tutor. Trên mobile ưu tiên bàn cờ và các tab chuyển panel.
- Dùng SVG/React làm bàn cờ; quân cờ rõ ràng, di chuyển được bằng click/touch và tùy chọn drag/drop. Không cần game engine 2D nặng.
- Có ký hiệu nước vừa đi, ô nguồn/đích, nước hợp lệ khi chọn quân, cảnh báo chiếu và điều khiển keyboard cơ bản.
- Không dùng màu làm tín hiệu duy nhất. Thao tác bàn cờ phải có nhãn accessible và xử lý reduced motion.
- Độ sâu engine **không** đồng nghĩa độ phù hợp sư phạm; lời giải thích không biến thành “thấy engine bảo thế”.

## 6. Phạm vi không làm trong MVP

- Đối kháng online giữa người với người, giải đấu, hệ thống bạn bè.
- Thanh toán, bảng xếp hạng quốc tế, training model cờ tướng từ đầu.
- Thư viện “tất cả khai cuộc” ngay bản đầu, tự động scrape/copy tài liệu có bản quyền.
- Tự động cấp Elo trình độ cao hoặc cam kết nâng trình nếu chưa có nghiên cứu đánh giá.

## 7. Chỉ số kiểm chứng sản phẩm

- Completion rate của chương đầu và phần trăm người học có thể giải thích được mục tiêu chính.
- Tỷ lệ phát hiện đe dọa trong bộ bài kiểm tra **chưa từng gặp** (pre/post với độ khó tương đương).
- Số lần lặp lại cùng một loại lỗi qua các bài tập sau 7/14 ngày.
- Chất lượng AI Tutor qua bộ câu hỏi chuyên môn có đáp án được người duyệt xác nhận; tỷ lệ hallucination và dẫn chứng không phù hợp.

Chỉ số phải có mẫu kiểm tra cố định, lưu phiên bản nội dung, không được tự nhận rằng sản phẩm đã nâng cấp trình độ của người chơi khi chưa có bằng chứng.
