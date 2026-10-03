# PROMPT THỰC THI — PHASE 4: Evidence-grounded AI Tutor

> Dùng file này làm yêu cầu công việc khi đã tới đúng Phase 4. File này không chứng minh rằng phase trước đã hoàn tất.

Bạn là Codex, Senior Full-stack Engineer kiêm Software Architect và người triển khai nền tảng giáo dục cờ tướng. **Chỉ thực hiện Phase 4.**

## Trình tự bắt buộc

1. Đọc `START_HERE.md`, `AGENTS.md`, `state/PROJECT_STATUS.md`, `state/HANDOFF.md` và **toàn bộ** `plans/PHASE_4.md`.
2. Kiểm tra cổng bắt đầu Phase 4 từ `state/PROJECT_STATUS.md`; với Phase > 0 phải có Phase trước `DONE` cùng bằng chứng. Nếu không đạt, **dừng phần code phase này** và ghi blocker thay vì bỏ qua.
3. Đọc tài liệu domain trong mục “Tài liệu phải đọc” của plan; quan sát source code hiện tại trước khi sửa.
4. Triển khai theo các mảnh nhỏ có test, tránh thay framework, tránh code không thuộc phase.
5. Chạy build/lint/typecheck/test và kiểm thử tích hợp có thể chạy trong môi trường hiện tại. Báo cáo lệnh thật và kết quả.
6. Cập nhật `state/PROJECT_STATUS.md`, `state/HANDOFF.md`, `state/SESSION_LOG.md`; cập nhật `state/DECISIONS.md` nếu có quyết định mới. **Không tự chạy phase tiếp theo.**

## Đầu việc giai đoạn này

**AI gia sư hỏi gợi mở và giải thích dựa trên rules, nguồn khai cuộc đã duyệt và engine analysis.**

- [ ] Thiết kế `TutorContext` và `TutorAnswer` có schema JSON/Pydantic rõ ràng, provenance cho từng ý chính. Tách provider adapter (mock/real) khỏi tutoring policy.
- [ ] Thiết lập 3 mức hint: (1) gợi ý hướng quan sát, (2) chỉ ra mối đe dọa/kế hoạch, (3) giải thích phương án được xác thực. Không tiết lộ đáp án đầy đủ ngay.
- [ ] Backend nạp FEN đã kiểm tra, annotation `published/reviewed`, engine PV và lesson context; loại bỏ dữ liệu chưa duyệt khi ở chế độ production.
- [ ] API tutor lưu context đủ để trace nhưng không log secret. Validate response: mọi ICCS/candidate phải hợp lệ; không diễn giải PV chưa kiểm chứng.
- [ ] Fallback khi LLM unavailable: dựa vào câu hỏi và feedback viết sẵn trong bài học, hiển thị giới hạn rõ ràng.
- [ ] Xây bộ eval chuyên môn tối thiểu 20 ca gồm rời lý thuyết, thiếu thông tin, engine nói một đường nhưng giảng giải nói đường khác, prompt injection từ annotation.
- [ ] Provider có thể cấu hình qua env. Nếu không có API key, hoàn thành mock/local tests, giữ nhiệm vụ smoke với provider thật là chưa xác minh trong handoff.

## Điều kiện để được ghi DONE

- [ ] Schema tests + mock prompt snapshots; all moves từ tutor validated; các câu “thắng bắt buộc” thiếu proof bị loại/nêu bất định.
- [ ] Đủ 20 ca eval có kết quả pass/fail và review thủ công ít nhất một mẫu sai.
- [ ] Không leak API key; prompt injection từ content/learner input không thay policy.
- [ ] E2E thực hiện một bài Opening Lab với hint theo 3 tầng; fallback không có LLM phải dùng được.
- [ ] Smoke provider thật chỉ xác nhận DONE tích hợp live khi có cấu hình hợp lệ; nếu chưa chạy được, ghi rõ chưa kiểm chứng.

## Giới hạn cứng

- Để LLM tạo nước cờ tùy ý
- Đem secret vào frontend
- Gọi LLM ở mỗi lần click không có cache/quota
- Không khởi tạo/commit/push Git, không cài dịch vụ có phí, không tự triển khai production.
- Không sửa hoặc làm mất tài liệu điều hướng đã được chuẩn bị. Những thay đổi cần thiết phải cập nhật link liên quan.
- Không báo “thành công” nếu test chưa chạy hoặc môi trường thiếu dependency; khi bị chặn ghi rõ trạng thái thực.

## Định dạng báo cáo cuối phiên

1. **Đã thực hiện:** file/module/behavior nào mới hoặc thay đổi.
2. **Bằng chứng:** lệnh test/build/lint, kết quả, manual test nào đã thực hiện.
3. **Điều kiện nghiệm thu:** từng điều kiện đã đạt/chưa đạt.
4. **Rủi ro/blockers:** những việc chưa kiểm chứng (đặc biệt giấy phép, luật cờ, engine, nguồn khai cuộc).
5. **Trạng thái:** Phase 4 `DONE`, `IN_PROGRESS` hay `BLOCKED`, kèm lý do; chỉ dẫn cho phiên sau.
