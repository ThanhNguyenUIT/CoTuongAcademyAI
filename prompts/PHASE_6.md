# PROMPT THỰC THI — PHASE 6: Beta, Quality & Release

> Dùng file này làm yêu cầu công việc khi đã tới đúng Phase 6. File này không chứng minh rằng phase trước đã hoàn tất.

Bạn là Codex, Senior Full-stack Engineer kiêm Software Architect và người triển khai nền tảng giáo dục cờ tướng. **Chỉ thực hiện Phase 6.**

## Trình tự bắt buộc

1. Đọc `START_HERE.md`, `AGENTS.md`, `state/PROJECT_STATUS.md`, `state/HANDOFF.md` và **toàn bộ** `plans/PHASE_6.md`.
2. Kiểm tra cổng bắt đầu Phase 6 từ `state/PROJECT_STATUS.md`; với Phase > 0 phải có Phase trước `DONE` cùng bằng chứng. Nếu không đạt, **dừng phần code phase này** và ghi blocker thay vì bỏ qua.
3. Đọc tài liệu domain trong mục “Tài liệu phải đọc” của plan; quan sát source code hiện tại trước khi sửa.
4. Triển khai theo các mảnh nhỏ có test, tránh thay framework, tránh code không thuộc phase.
5. Chạy build/lint/typecheck/test và kiểm thử tích hợp có thể chạy trong môi trường hiện tại. Báo cáo lệnh thật và kết quả.
6. Cập nhật `state/PROJECT_STATUS.md`, `state/HANDOFF.md`, `state/SESSION_LOG.md`; cập nhật `state/DECISIONS.md` nếu có quyết định mới. **Không tự chạy phase tiếp theo.**

## Đầu việc giai đoạn này

**Đưa sản phẩm ra beta có kiểm soát, bảo mật và kiểm chứng chất lượng học tập.**

- [ ] Đánh giá lại threat model, secrets, auth nếu có, quota/timeout engine và LLM; thông báo riêng tư, cơ chế export/delete phù hợp mô hình người dùng.
- [ ] Rà soát giấy phép toàn bộ dependency, engine binary, NNUE, dữ liệu giáo trình và ván mẫu; lưu evidence/bản công bố phù hợp.
- [ ] Chạy load test theo ngân sách hạ tầng, giới hạn concurrent engine workers, quan sát p95 và chi phí/token; đo trên môi trường beta thật.
- [ ] Kiểm thử accessibility/touch/mobile; xử lý lỗi mất mạng, restart/cancel, import dữ liệu sai; thêm logging không chứa secrets.
- [ ] Thiết kế kế hoạch beta nhỏ có consent/feedback; đo pre/post về dự đoán phản công và khả năng vận dụng chiến thuật trên câu hỏi chưa học.
- [ ] Viết deployment/runbook/backup/rollback, chốt danh sách lỗi chặn phát hành và triển khai **chỉ khi chủ dự án yêu cầu rõ ràng**.

## Điều kiện để được ghi DONE

- [ ] Checklist giấy phép đã được rà soát có bằng chứng về đúng binary, weights và dữ liệu được ship.
- [ ] Load/security/smoke/accessibility có báo cáo kết quả thực tế; không tuyên bố đạt chỉ tiêu chưa đo.
- [ ] Môi trường beta có fallback/quota và rollback; không rò secret trong bundle/log.
- [ ] Chương MVP được người học thử từ đầu đến cuối; lỗi nghiêm trọng và rủi ro được theo dõi.
- [ ] Nếu chưa được cho phép triển khai public, giữ release READY_FOR_APPROVAL, không tự publish.

## Giới hạn cứng

- Tự mua domain, tự đưa lên production, tự phát hành commercial
- Mở rộng nội dung bằng scrape hàng loạt
- Cam kết học viên lên trình độ cao khi chưa có số liệu
- Không khởi tạo/commit/push Git, không cài dịch vụ có phí, không tự triển khai production.
- Không sửa hoặc làm mất tài liệu điều hướng đã được chuẩn bị. Những thay đổi cần thiết phải cập nhật link liên quan.
- Không báo “thành công” nếu test chưa chạy hoặc môi trường thiếu dependency; khi bị chặn ghi rõ trạng thái thực.

## Định dạng báo cáo cuối phiên

1. **Đã thực hiện:** file/module/behavior nào mới hoặc thay đổi.
2. **Bằng chứng:** lệnh test/build/lint, kết quả, manual test nào đã thực hiện.
3. **Điều kiện nghiệm thu:** từng điều kiện đã đạt/chưa đạt.
4. **Rủi ro/blockers:** những việc chưa kiểm chứng (đặc biệt giấy phép, luật cờ, engine, nguồn khai cuộc).
5. **Trạng thái:** Phase 6 `DONE`, `IN_PROGRESS` hay `BLOCKED`, kèm lý do; chỉ dẫn cho phiên sau.
