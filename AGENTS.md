# AGENTS.md — quy tắc cố định cho Codex

## Mục tiêu

Xây dựng **học viện cờ tướng AI đào tạo tư duy chiến thuật**, không phải chỉ một bàn cờ và chatbot. Người học phải biết **vì sao** chọn nước đi, phản ứng khi đối thủ đi khác lý thuyết, và tự suy luận trong thế cờ mới.

## Trước mỗi tác vụ

1. Đọc [`START_HERE.md`](START_HERE.md), [`state/PROJECT_STATUS.md`](state/PROJECT_STATUS.md) và [`state/HANDOFF.md`](state/HANDOFF.md).
2. Xác định phase hiện tại từ status; chỉ đọc plan, prompt và docs liên quan trước khi code.
3. Không bỏ qua phase trước hoặc âm thầm mở scope; khi tài liệu và code mâu thuẫn, ghi nhận và kiểm tra.

## Nguyên tắc code

- Frontend React + TypeScript + Vite; backend Python + FastAPI; ban đầu modular monolith. Không tự chuyển framework nếu không có quyết định được ghi nhận.
- Tách **rules**, **engine adapter**, **opening knowledge**, **AI tutor**, **learning progress**. Không nhúng nước cờ/học liệu tĩnh vào component UI.
- Tầng rules/backend là nguồn kiểm tra nước đi hợp lệ; frontend chỉ đưa ra gợi ý UX. LLM không bao giờ là trọng tài luật cờ hoặc nguồn tạo ra dòng phân tích engine.
- Các nguồn khai cuộc và ví dụ chuyên môn cần trích nguồn, có trạng thái duyệt. Không gán nhãn “tốt nhất”, “thắng bắt buộc” khi chưa có chứng cứ từ engine và/hoặc biên tập nội dung.
- Thiết kế interface cho engine và LLM để thay thế được; mock engine/mock tutor cho test.
- Không hard-code bí mật, không commit `.env`; dùng `.env.example` với giá trị giả.
- Không tự `git init`, commit, push, tạo remote hoặc triển khai cloud nếu không được yêu cầu.
- Không cài dịch vụ trả phí hoặc sử dụng trọng số có hạn chế thương mại mà không được duyệt; xem `docs/ENGINE_LICENSE.md`.
- Không xóa, viết lại các file Markdown điều hướng đã chuẩn bị. Chỉ cập nhật để phản ánh quyết định thực tế hoặc tiến độ; giữ link hoạt động.

## Quy tắc thực thi và nghiệm thu

- Mỗi phiên chỉ một phase; nếu việc quá lớn, chia thành phần nhỏ ngay trong phase đó.
- Khi thay đổi hành vi phải có test tương ứng. Chạy lint, typecheck, unit/integration liên quan; ghi **lệnh và kết quả thực tế** vào `state/HANDOFF.md`.
- Không báo DONE nếu chưa vượt qua exit criteria trong `plans/PHASE_N.md`.
- Sau mỗi phiên: cập nhật `state/PROJECT_STATUS.md`, `state/HANDOFF.md`, ghi một entry mới vào `state/SESSION_LOG.md`; thêm ADR ở `state/DECISIONS.md` nếu có thay đổi kiến trúc.
- Nếu vướng blocker hoặc không chạy được test, nêu chính xác lý do và giữ status `BLOCKED`/`IN_PROGRESS`.

## Ưu tiên sản phẩm

1. Đúng luật và hiển thị đáng tin cậy.
2. Dữ liệu khai cuộc đáng tin cậy và dễ mở rộng.
3. Gia sư đặt câu hỏi khơi gợi tư duy trước khi tiết lộ đáp án.
4. Cá nhân hóa dựa trên bằng chứng học tập, không dựa trên điểm số tự bịa.
5. Dễ triển khai và kiểm thử cục bộ trước khi mở rộng hạ tầng.
