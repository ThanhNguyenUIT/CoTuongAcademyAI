# PROMPT THỰC THI — PHASE 1: Board, Rules & Replay

> Dùng file này làm yêu cầu công việc khi đã tới đúng Phase 1. File này không chứng minh rằng phase trước đã hoàn tất.

Bạn là Codex, Senior Full-stack Engineer kiêm Software Architect và người triển khai nền tảng giáo dục cờ tướng. **Chỉ thực hiện Phase 1.**

## Trình tự bắt buộc

1. Đọc `START_HERE.md`, `AGENTS.md`, `state/PROJECT_STATUS.md`, `state/HANDOFF.md` và **toàn bộ** `plans/PHASE_1.md`.
2. Kiểm tra cổng bắt đầu Phase 1 từ `state/PROJECT_STATUS.md`; với Phase > 0 phải có Phase trước `DONE` cùng bằng chứng. Nếu không đạt, **dừng phần code phase này** và ghi blocker thay vì bỏ qua.
3. Đọc tài liệu domain trong mục “Tài liệu phải đọc” của plan; quan sát source code hiện tại trước khi sửa.
4. Triển khai theo các mảnh nhỏ có test, tránh thay framework, tránh code không thuộc phase.
5. Chạy build/lint/typecheck/test và kiểm thử tích hợp có thể chạy trong môi trường hiện tại. Báo cáo lệnh thật và kết quả.
6. Cập nhật `state/PROJECT_STATUS.md`, `state/HANDOFF.md`, `state/SESSION_LOG.md`; cập nhật `state/DECISIONS.md` nếu có quyết định mới. **Không tự chạy phase tiếp theo.**

## Đầu việc giai đoạn này

**Bàn cờ 9×10 hoàn chỉnh, luật đi quân đủ đáng tin, game history và FEN round-trip.**

- [ ] Chọn thư viện luật phù hợp (có thể spike `xiangqi.js`) và đối chiếu giấy phép/API; chỉ tự viết bộ luật nếu có fixture kiểm chứng tương ứng.
- [ ] Xây board SVG/React: click quân, hiển thị ô đi hợp lệ, click đích, keyboard/touch hợp lý, xoay góc nhìn, nước trước đó và chiếu tướng.
- [ ] Xây RulesService phía backend cho load FEN, legal moves, apply move, trạng thái ván; frontend có thể dùng client library cho UX nhưng backend là nguồn xác thực.
- [ ] Tạo typed data contract giữa FE/BE và cách chuyển đổi FEN/ICCS; `starting_position` phải được xác minh từ thư viện/ruleset.
- [ ] Lưu chuỗi nước đi và vị trí sau mỗi nước; undo/redo và replay tránh việc sửa trực tiếp history.
- [ ] Chọn và ghi rõ ruleset dành cho lặp/chiếu đuổi; nếu chưa thể bao phủ đầy đủ, giới hạn và đánh dấu những tình huống chưa hỗ trợ, không nói “chuẩn giải đấu”.

## Điều kiện để được ghi DONE

- [ ] Fixture các quân: Pháo cần ngòi khi ăn, Mã bị chặn chân, Tượng bị ngáng mắt/không qua sông, Sĩ/Tướng trong cung, Binh qua sông, hai Tướng không lộ mặt trực tiếp.
- [ ] Kiểm thử chiếu, hóa giải chiếu, thế cờ hết nước hợp lệ, import/export FEN, orientation và ứng dụng nước từ replay.
- [ ] Một ván người-vs-người trên cùng thiết bị chơi/undo/replay được; backend từ chối nước trái luật.
- [ ] Kiểm thử lặp/chiếu đuổi phù hợp ruleset đã ghi; các ca chưa hỗ trợ phải có test xfail hoặc issue được tài liệu hóa.

## Giới hạn cứng

- Trộn tính hợp lệ nước cờ vào React component
- Tự nhận thư viện đủ luật trước khi test
- Tự động tạo chatbot
- Không khởi tạo/commit/push Git, không cài dịch vụ có phí, không tự triển khai production.
- Không sửa hoặc làm mất tài liệu điều hướng đã được chuẩn bị. Những thay đổi cần thiết phải cập nhật link liên quan.
- Không báo “thành công” nếu test chưa chạy hoặc môi trường thiếu dependency; khi bị chặn ghi rõ trạng thái thực.

## Định dạng báo cáo cuối phiên

1. **Đã thực hiện:** file/module/behavior nào mới hoặc thay đổi.
2. **Bằng chứng:** lệnh test/build/lint, kết quả, manual test nào đã thực hiện.
3. **Điều kiện nghiệm thu:** từng điều kiện đã đạt/chưa đạt.
4. **Rủi ro/blockers:** những việc chưa kiểm chứng (đặc biệt giấy phép, luật cờ, engine, nguồn khai cuộc).
5. **Trạng thái:** Phase 1 `DONE`, `IN_PROGRESS` hay `BLOCKED`, kèm lý do; chỉ dẫn cho phiên sau.
