# PROMPT — tiếp tục dự án từ bất kỳ phiên Codex mới nào

Bạn là Codex tiếp quản Xiangqi AI Academy. **Đừng tin rằng người dùng hoặc cuộc chat mới nhớ chi tiết các phiên trước. Nguồn sự thật là file của workspace.**

## Bước 1 — đọc và kiểm tra

1. Đọc `START_HERE.md`, `AGENTS.md`, `state/PROJECT_STATUS.md`, `state/HANDOFF.md`, các entry mới nhất trong `state/SESSION_LOG.md`, các ADR liên quan trong `state/DECISIONS.md`.
2. Khảo sát thư mục và code hiện tại, đối chiếu các tuyên bố DONE với test và artifact thực tế. Nếu code/tài liệu mâu thuẫn, đừng đoán: ghi bất nhất rồi điều tra.
3. Xác định phase `IN_PROGRESS`/`BLOCKED` trước tiên; nếu không có, chọn phase `PENDING` sớm nhất mà phase trước đã `DONE`. Phase `LOCKED` không được tự mở.
4. Đọc `plans/PHASE_N.md`, `prompts/PHASE_N.md` và các docs được dẫn. Nếu thiếu đầu vào bắt buộc hoặc giấy phép, ghi blocker và tiếp tục các phần hợp lệ của **chính phase đó**, không nhảy tiếp.

## Bước 2 — tiếp tục đúng điểm dở dang

- Không làm lại file đã hoàn thành trừ khi có lỗi thật.
- Lấy `state/HANDOFF.md` làm danh sách việc chưa xong gần nhất, nhưng xác nhận bằng mã/test.
- Thực hiện phần nhỏ có thể nghiệm thu; không tự mở scope vì thấy “tiện”.
- Khi hoàn thành: chạy test/build/lint tương ứng, ghi bằng chứng và checklist exit criteria.

## Bước 3 — cập nhật trạng thái/handoff

Ghi trong `state/HANDOFF.md`: nội dung làm, file sửa, lệnh/kết quả kiểm thử, tiêu chí nghiệm thu còn thiếu, rủi ro và **chính xác prompt/file cần đọc ở phiên sau**. Cập nhật `PROJECT_STATUS.md`, nối thêm `SESSION_LOG.md`; giữ phase `IN_PROGRESS` hoặc `BLOCKED` nếu chưa đủ exit criteria.

**Không bắt đầu phase mới trong phiên này nếu người dùng chỉ yêu cầu “tiếp tục”; tiếp tục phần dở dang hoặc phase kế tiếp gần nhất, và dừng sau phase đó.**
