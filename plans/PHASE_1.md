# PHASE 1 — Board, Rules & Replay

**Mục tiêu:** Bàn cờ 9×10 hoàn chỉnh, luật đi quân đủ đáng tin, game history và FEN round-trip.

**Điều kiện bắt đầu:** `plans/PHASE_0.md` đã DONE và có bằng chứng test trong `state/HANDOFF.md`.

## Tài liệu phải đọc

- [`START_HERE.md`](../START_HERE.md)
- [`AGENTS.md`](../AGENTS.md)
- [`state/PROJECT_STATUS.md`](../state/PROJECT_STATUS.md)
- [`state/HANDOFF.md`](../state/HANDOFF.md)
- [`docs/PRODUCT_SPEC.md`](../docs/PRODUCT_SPEC.md)
- [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md)
- [`docs/DATA_API.md`](../docs/DATA_API.md)
- [`docs/QUALITY_SECURITY.md`](../docs/QUALITY_SECURITY.md)

## Checklist triển khai

- [ ] Chọn thư viện luật phù hợp (có thể spike `xiangqi.js`) và đối chiếu giấy phép/API; chỉ tự viết bộ luật nếu có fixture kiểm chứng tương ứng.
- [ ] Xây board SVG/React: click quân, hiển thị ô đi hợp lệ, click đích, keyboard/touch hợp lý, xoay góc nhìn, nước trước đó và chiếu tướng.
- [ ] Xây RulesService phía backend cho load FEN, legal moves, apply move, trạng thái ván; frontend có thể dùng client library cho UX nhưng backend là nguồn xác thực.
- [ ] Tạo typed data contract giữa FE/BE và cách chuyển đổi FEN/ICCS; `starting_position` phải được xác minh từ thư viện/ruleset.
- [ ] Lưu chuỗi nước đi và vị trí sau mỗi nước; undo/redo và replay tránh việc sửa trực tiếp history.
- [ ] Chọn và ghi rõ ruleset dành cho lặp/chiếu đuổi; nếu chưa thể bao phủ đầy đủ, giới hạn và đánh dấu những tình huống chưa hỗ trợ, không nói “chuẩn giải đấu”.

## Exit criteria — cần bằng chứng, không chỉ báo miệng

- [ ] Fixture các quân: Pháo cần ngòi khi ăn, Mã bị chặn chân, Tượng bị ngáng mắt/không qua sông, Sĩ/Tướng trong cung, Binh qua sông, hai Tướng không lộ mặt trực tiếp.
- [ ] Kiểm thử chiếu, hóa giải chiếu, thế cờ hết nước hợp lệ, import/export FEN, orientation và ứng dụng nước từ replay.
- [ ] Một ván người-vs-người trên cùng thiết bị chơi/undo/replay được; backend từ chối nước trái luật.
- [ ] Kiểm thử lặp/chiếu đuổi phù hợp ruleset đã ghi; các ca chưa hỗ trợ phải có test xfail hoặc issue được tài liệu hóa.

## Deliverables

- Board responsive có thể thao tác
- RulesService và API rules đã kiểm thử
- Fixture luật và ván mẫu, replay

## Không làm trong giai đoạn này

- Trộn tính hợp lệ nước cờ vào React component
- Tự nhận thư viện đủ luật trước khi test
- Tự động tạo chatbot

## Quy trình đóng giai đoạn

1. Đối chiếu từng ô exit criteria với file/test/chức năng thực tế.
2. Chạy test/lint/build đúng script đã có; ghi lệnh, mã thoát và điểm chưa đạt vào `state/HANDOFF.md`.
3. Cập nhật `state/DECISIONS.md` nếu có quyết định kiến trúc/giấy phép, và `state/SESSION_LOG.md` một mục.
4. Chỉ đánh dấu Phase 1 là `DONE` khi đã đủ điều kiện; nếu thiếu thì `IN_PROGRESS` hoặc `BLOCKED`, ghi blocker cụ thể. Không tự động chạy phase 2.

**Đầu mối bước tiếp theo:** Phase 2 cần engine adapter nhưng không sửa contract rules đã ổn định nếu không có migration/test.

**Prompt thực thi:** [`prompts/PHASE_1.md`](../prompts/PHASE_1.md).
