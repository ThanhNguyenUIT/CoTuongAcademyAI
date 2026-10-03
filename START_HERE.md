# START HERE — trung tâm điều hướng dự án

**Bạn là Codex đang làm việc trên Xiangqi AI Academy? Bắt đầu đọc file này trước khi sửa code.**

## 1. Nguồn sự thật và thứ tự ưu tiên

1. Yêu cầu trực tiếp, hiện tại của chủ dự án; không tự suy đoán rằng đã có phê duyệt triển khai bước mới.
2. [`AGENTS.md`](AGENTS.md): quy tắc phát triển ổn định.
3. [`state/PROJECT_STATUS.md`](state/PROJECT_STATUS.md): trạng thái giai đoạn thực tế.
4. [`plans/PHASE_N.md`](plans/PHASE_0.md): checklist và điều kiện nghiệm thu của giai đoạn đang làm.
5. [`prompts/PHASE_N.md`](prompts/PHASE_0.md): lệnh triển khai theo giai đoạn.
6. [`docs/PRODUCT_SPEC.md`](docs/PRODUCT_SPEC.md), [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/DATA_API.md`](docs/DATA_API.md), [`docs/CONTENT_GUIDE.md`](docs/CONTENT_GUIDE.md), [`docs/QUALITY_SECURITY.md`](docs/QUALITY_SECURITY.md), [`docs/ENGINE_LICENSE.md`](docs/ENGINE_LICENSE.md): tài liệu nền.
7. [`state/DECISIONS.md`](state/DECISIONS.md), [`state/HANDOFF.md`](state/HANDOFF.md), [`state/SESSION_LOG.md`](state/SESSION_LOG.md): lý do quyết định, công việc dở dang, bằng chứng.

Nếu code và tài liệu mâu thuẫn, kiểm tra và ghi nhận sự khác biệt; **không tự sửa lịch sử tiến độ cho khớp với code**.

## 2. Luồng triển khai có kiểm soát

```text
START_HERE.md
    |
    v
state/PROJECT_STATUS.md ----> Có giai đoạn đang IN_PROGRESS?
    |                              |
    |                        Có: tiếp tục phase đó
    |                              |
    +----> Chưa: chọn phase PENDING đầu tiên có phase trước DONE
                                   |
                                   v
                    plans/PHASE_N.md + prompts/PHASE_N.md
                                   |
                                   v
                  Code + kiểm thử + đối chiếu exit criteria
                                   |
                      +------------+------------+
                      |                         |
                    FAIL                       PASS
                      |                         |
               giữ IN_PROGRESS          cập nhật status DONE
               ghi blocker               ghi HANDOFF/SESSION_LOG
                                                |
                                                v
                             DỪNG; chỉ chạy phase tiếp khi được yêu cầu
```

**Tuyệt đối không đánh dấu DONE khi test chưa chạy, thất bại hoặc chưa có bằng chứng.** Nếu môi trường không cho chạy test, đánh dấu `BLOCKED`/`IN_PROGRESS` và giải thích.

## 3. Bản đồ giai đoạn

| Giai đoạn | Kết quả chính | Plan | Prompt |
| --- | --- | --- | --- |
| 0 — Bootstrap | Frontend/backend khởi động + tài liệu + chất lượng cơ bản | [Plan 0](plans/PHASE_0.md) | [Prompt 0](prompts/PHASE_0.md) |
| 1 — Board & Rules | Bàn cờ 9×10, luật cờ, replay và kiểm thử | [Plan 1](plans/PHASE_1.md) | [Prompt 1](prompts/PHASE_1.md) |
| 2 — Engine | Adapter UCI/UCCI, chơi máy, phân tích có giới hạn tài nguyên | [Plan 2](plans/PHASE_2.md) | [Prompt 2](prompts/PHASE_2.md) |
| 3 — Opening Lab | Đồ thị khai cuộc + **một chương** học hoàn chỉnh | [Plan 3](plans/PHASE_3.md) | [Prompt 3](prompts/PHASE_3.md) |
| 4 — AI Tutor | Gia sư giải thích dựa trên engine và kiến thức đã duyệt | [Plan 4](plans/PHASE_4.md) | [Prompt 4](prompts/PHASE_4.md) |
| 5 — Adaptive Learning | Hồ sơ năng lực, lỗi lặp lại, luyện lại, ôn tập | [Plan 5](plans/PHASE_5.md) | [Prompt 5](prompts/PHASE_5.md) |
| 6 — Release | Mở rộng nội dung, tối ưu, bảo mật, beta và phát hành | [Plan 6](plans/PHASE_6.md) | [Prompt 6](prompts/PHASE_6.md) |

**MVP có giá trị kiểm chứng: hoàn tất giai đoạn 0–4**. Mỗi giai đoạn sau là phạm vi mở rộng có kiểm soát, không phải lý do để làm quá tay ở phase đầu.

## 4. Khi vừa mở dự án lần đầu

Đọc `prompts/PHASE_0.md`. Toàn bộ Markdown trong bộ này đã được chuẩn bị; **đừng tạo lại README, AGENTS, plan, prompt**. Phase 0 chỉ hiện thực cấu trúc code, health check, các lệnh chạy và các kiểm thử được nêu trong plan.

## 5. Khi mở phiên Codex mới

Dùng đúng prompt dưới đây, hoặc giao Codex đọc [`prompts/RESUME.md`](prompts/RESUME.md):

> Hãy đọc `START_HERE.md`, `AGENTS.md`, `state/PROJECT_STATUS.md`, `state/HANDOFF.md` và `prompts/RESUME.md`. Xác định giai đoạn chưa hoàn tất gần nhất, đối chiếu code và kiểm thử hiện có, sau đó chỉ thực hiện công việc của giai đoạn đó. Không chuyển giai đoạn nếu exit criteria chưa đạt.

Không cần dán toàn bộ hồ sơ vào chat mỗi lần; Codex đọc file ở workspace. Cập nhật `state/PROJECT_STATUS.md`, `state/HANDOFF.md` và `state/SESSION_LOG.md` sau mỗi phiên đã làm việc.

## 6. Kiểm tra cuối mỗi phiên

- Phạm vi thay đổi có nằm trong phase đang làm không?
- Test/lint/type-check nào đã chạy thực sự; kết quả cụ thể?
- Mã nguồn đã khớp các contract ở `docs/` chưa?
- Còn quyết định/chặn kỹ thuật hay rủi ro giấy phép nào?
- Đã cập nhật trạng thái, handoff, nhật ký chưa?
- Bước kế tiếp có thể thực hiện bằng một phiên Codex độc lập chưa?

Nếu có mục chưa đạt, để phase `IN_PROGRESS` hoặc `BLOCKED`, không chuyển tiếp.
