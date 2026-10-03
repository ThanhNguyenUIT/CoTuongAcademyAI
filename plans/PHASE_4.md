# PHASE 4 — Evidence-grounded AI Tutor

**Mục tiêu:** AI gia sư hỏi gợi mở và giải thích dựa trên rules, nguồn khai cuộc đã duyệt và engine analysis.

**Điều kiện bắt đầu:** `plans/PHASE_3.md` đã DONE và có bằng chứng test trong `state/HANDOFF.md`.

## Tài liệu phải đọc

- [`START_HERE.md`](../START_HERE.md)
- [`AGENTS.md`](../AGENTS.md)
- [`state/PROJECT_STATUS.md`](../state/PROJECT_STATUS.md)
- [`state/HANDOFF.md`](../state/HANDOFF.md)
- [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md)
- [`docs/DATA_API.md`](../docs/DATA_API.md)
- [`docs/CONTENT_GUIDE.md`](../docs/CONTENT_GUIDE.md)
- [`docs/QUALITY_SECURITY.md`](../docs/QUALITY_SECURITY.md)

## Checklist triển khai

- [x] Thiết kế `TutorContext` và `TutorAnswer` có schema JSON/Pydantic rõ ràng, provenance cho từng ý chính. Tách provider adapter (mock/real) khỏi tutoring policy.
- [x] Thiết lập 3 mức hint: (1) gợi ý hướng quan sát, (2) chỉ ra mối đe dọa/kế hoạch, (3) giải thích phương án được xác thực. Không tiết lộ đáp án đầy đủ ngay.
- [x] Backend nạp FEN đã kiểm tra, annotation `published/reviewed`, engine PV và lesson context; loại bỏ dữ liệu chưa duyệt khi ở chế độ production.
- [x] API tutor lưu context đủ để trace nhưng không log secret. Validate response: mọi ICCS/candidate phải hợp lệ; không diễn giải PV chưa kiểm chứng.
- [x] Fallback khi LLM unavailable: dựa vào câu hỏi và feedback viết sẵn trong bài học, hiển thị giới hạn rõ ràng.
- [x] Xây bộ eval chuyên môn tối thiểu 20 ca gồm rời lý thuyết, thiếu thông tin, engine nói một đường nhưng giảng giải nói đường khác, prompt injection từ annotation.
- [x] Provider có thể cấu hình qua env. Không có API key; mock/local tests đạt, smoke với provider thật được ghi rõ là chưa xác minh trong handoff.

## Exit criteria — cần bằng chứng, không chỉ báo miệng

- [x] Schema tests + mock prompt snapshots; all moves từ tutor validated; các câu “thắng bắt buộc” thiếu proof bị loại/nêu bất định.
- [x] Đủ 20 ca eval: 20/20 pass; thủ công rà mẫu provider mâu thuẫn với PV và xác nhận claim/nước bị loại.
- [x] Không leak API key; prompt injection từ content/learner input không thay policy.
- [x] Browser E2E thực hiện một bài Opening Lab với hint theo 3 tầng; fallback khi không cấu hình LLM dùng được.
- [x] Smoke provider thật chưa chạy do không có credentials; được ghi là chưa xác minh, không tuyên bố live provider đã tích hợp kiểm chứng.

## Deliverables

- AI Tutor API + UI
- Mock/real provider boundary
- Eval set + fallback + observability

## Không làm trong giai đoạn này

- Để LLM tạo nước cờ tùy ý
- Đem secret vào frontend
- Gọi LLM ở mỗi lần click không có cache/quota

## Quy trình đóng giai đoạn

1. Đối chiếu từng ô exit criteria với file/test/chức năng thực tế.
2. Chạy test/lint/build đúng script đã có; ghi lệnh, mã thoát và điểm chưa đạt vào `state/HANDOFF.md`.
3. Cập nhật `state/DECISIONS.md` nếu có quyết định kiến trúc/giấy phép, và `state/SESSION_LOG.md` một mục.
4. Chỉ đánh dấu Phase 4 là `DONE` khi đã đủ điều kiện; nếu thiếu thì `IN_PROGRESS` hoặc `BLOCKED`, ghi blocker cụ thể. Không tự động chạy phase 5.

**Đầu mối bước tiếp theo:** MVP học khai cuộc có AI hoàn chỉnh trên một chương; tiếp tục phase 5 để đánh giá và ôn tập cá nhân hóa.

**Prompt thực thi:** [`prompts/PHASE_4.md`](../prompts/PHASE_4.md).
