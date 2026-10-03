# PHASE 6 — Beta, Quality & Release

**Mục tiêu:** Đưa sản phẩm ra beta có kiểm soát, bảo mật và kiểm chứng chất lượng học tập.

**Điều kiện bắt đầu:** `plans/PHASE_5.md` đã DONE và có bằng chứng test trong `state/HANDOFF.md`.

## Tài liệu phải đọc

- [`START_HERE.md`](../START_HERE.md)
- [`AGENTS.md`](../AGENTS.md)
- [`state/PROJECT_STATUS.md`](../state/PROJECT_STATUS.md)
- [`state/HANDOFF.md`](../state/HANDOFF.md)
- [`docs/PRODUCT_SPEC.md`](../docs/PRODUCT_SPEC.md)
- [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md)
- [`docs/QUALITY_SECURITY.md`](../docs/QUALITY_SECURITY.md)
- [`docs/ENGINE_LICENSE.md`](../docs/ENGINE_LICENSE.md)
- [`docs/SOURCES.md`](../docs/SOURCES.md)

## Checklist triển khai

- [x] Đánh giá lại threat model, secrets, auth nếu có, quota/timeout engine và LLM; thông báo riêng tư, cơ chế export/delete phù hợp mô hình người dùng. Kết quả phạm vi local ghi ở [`docs/BETA_READINESS.md`](../docs/BETA_READINESS.md).
- [x] Rà soát giấy phép toàn bộ dependency, engine binary, NNUE, dữ liệu giáo trình và ván mẫu; lưu evidence/bản công bố phù hợp. Kiểm kê local và các quyền còn thiếu ghi ở [`docs/RELEASE_LICENSE_AUDIT.md`](../docs/RELEASE_LICENSE_AUDIT.md); chưa cho phép phân phối.
- [ ] Chạy load test theo ngân sách hạ tầng, giới hạn concurrent engine workers, quan sát p95 và chi phí/token; đo trên môi trường beta thật.
- [ ] Kiểm thử accessibility/touch/mobile; xử lý lỗi mất mạng, restart/cancel, import dữ liệu sai; thêm logging không chứa secrets.
- [x] Thiết kế kế hoạch beta nhỏ có consent/feedback; đo pre/post về dự đoán phản công và khả năng vận dụng chiến thuật trên câu hỏi chưa học. Protocol đã được ghi; cohort và pre/post chưa chạy.
- [x] Viết runbook local cho backup/recovery/rollback và chốt danh sách lỗi chặn phát hành ở [`docs/LOCAL_BETA_RUNBOOK.md`](../docs/LOCAL_BETA_RUNBOOK.md) và [`docs/BETA_READINESS.md`](../docs/BETA_READINESS.md).
- [ ] Tạo/cấu hình môi trường deployment beta và triển khai **chỉ khi chủ dự án yêu cầu rõ ràng**.

**Trạng thái thực thi 2026-09-27:** threat model, notice và beta protocol được ghi trong [`docs/BETA_READINESS.md`](../docs/BETA_READINESS.md); runbook/snapshot SQLite ở [`docs/LOCAL_BETA_RUNBOOK.md`](../docs/LOCAL_BETA_RUNBOOK.md); kiểm kê dependency/artifact/nội dung ở [`docs/RELEASE_LICENSE_AUDIT.md`](../docs/RELEASE_LICENSE_AUDIT.md). Local smoke/load và automated keyboard tests có bằng chứng trong HANDOFF. Các checkbox vẫn mở nếu cần beta thật, rights-holder clearance, touch/mobile UAT hoặc load measurement trên hạ tầng beta; chưa triển khai public.

## Exit criteria — cần bằng chứng, không chỉ báo miệng

- [x] Checklist giấy phép đã được rà soát có bằng chứng về đúng binary, weights và dữ liệu được ship/loại khỏi bản phân phối hiện tại; quyền phân phối một số nội dung vẫn chưa có.
- [ ] Load/security/smoke/accessibility có báo cáo kết quả thực tế; không tuyên bố đạt chỉ tiêu chưa đo.
- [ ] Môi trường beta có fallback/quota và rollback; không rò secret trong bundle/log.
- [ ] Chương MVP được người học thử từ đầu đến cuối; lỗi nghiêm trọng và rủi ro được theo dõi.
- [x] Nếu chưa được cho phép triển khai public, giữ release READY_FOR_APPROVAL, không tự publish.

## Deliverables

- Beta readiness + runbook
- License/security checklist
- Báo cáo kiểm thử và đánh giá giáo dục

## Không làm trong giai đoạn này

- Tự mua domain, tự đưa lên production, tự phát hành commercial
- Mở rộng nội dung bằng scrape hàng loạt
- Cam kết học viên lên trình độ cao khi chưa có số liệu

## Quy trình đóng giai đoạn

1. Đối chiếu từng ô exit criteria với file/test/chức năng thực tế.
2. Chạy test/lint/build đúng script đã có; ghi lệnh, mã thoát và điểm chưa đạt vào `state/HANDOFF.md`.
3. Cập nhật `state/DECISIONS.md` nếu có quyết định kiến trúc/giấy phép, và `state/SESSION_LOG.md` một mục.
4. Chỉ đánh dấu Phase 6 là `DONE` khi đã đủ điều kiện; nếu thiếu thì `IN_PROGRESS` hoặc `BLOCKED`, ghi blocker cụ thể. Không tự động chạy phase mới.

**Đầu mối bước tiếp theo:** Sau phase 6, lựa chọn mở rộng dựa trên beta feedback và sổ quyết định riêng, không tự sinh phase không được yêu cầu.

**Prompt thực thi:** [`prompts/PHASE_6.md`](../prompts/PHASE_6.md).
