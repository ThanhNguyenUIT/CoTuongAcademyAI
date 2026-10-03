# PHASE 2 — Engine Adapter & Analysis

**Mục tiêu:** Chơi với engine cờ tướng và xem biến phân tích có provenance, timeout và kiểm soát giấy phép.

**Điều kiện bắt đầu:** `plans/PHASE_1.md` đã DONE và có bằng chứng test trong `state/HANDOFF.md`.

## Tài liệu phải đọc

- [`START_HERE.md`](../START_HERE.md)
- [`AGENTS.md`](../AGENTS.md)
- [`state/PROJECT_STATUS.md`](../state/PROJECT_STATUS.md)
- [`state/HANDOFF.md`](../state/HANDOFF.md)
- [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md)
- [`docs/DATA_API.md`](../docs/DATA_API.md)
- [`docs/ENGINE_LICENSE.md`](../docs/ENGINE_LICENSE.md)
- [`docs/QUALITY_SECURITY.md`](../docs/QUALITY_SECURITY.md)

## Checklist triển khai

- [ ] Làm spike Pikafish vs Fairy-Stockfish (không tự tải trọng số cấm thương mại); so sánh compatibility, hiệu năng local, UCI/UCCI, binary version và giấy phép.
- [ ] Ghi ADR quyết định engine/binary/weights/protocol và phạm vi dùng; nếu chưa đủ bằng chứng giấy phép, chỉ triển khai mock + adapter, giữ phase BLOCKED trước nghiệm thu engine thật.
- [ ] Thiết kế `EngineAdapter` và `MockEngine`, quản lý subprocess: start/isready, position, go, stop/cancel, quit, crash restart; cân nhắc variant options khi engine yêu cầu.
- [ ] Chuẩn hóa score perspective, PV, multipv, depth và version; validate FEN trước khi chạy, validate toàn bộ PV bằng RulesService khi nhận về.
- [ ] API phân tích và chơi với máy có limit CPU/time và timeout; front-end chọn độ khó dựa vào bộ giới hạn đã kiểm thử, không hiển thị chính xác Elo nếu không có calibration.
- [ ] Tạo fixture UCI transcript, logging có kiểm soát và cache theo position/version/limits nếu cần.

## Exit criteria — cần bằng chứng, không chỉ báo miệng

- [ ] Unit test với MockEngine cho normal/timeout/hang/crash/invalid PV và cancellation.
- [ ] Integration test engine thật tại localhost với vị trí chuẩn: trả best move hợp lệ và phân tích đa biến nếu engine hỗ trợ.
- [ ] Kiểm thử orientation: score phải được giải thích nhất quán theo Đỏ/Đen và theo phía tới lượt; đồng bộ hướng nhìn UI.
- [ ] Stress smoke với 2–3 request đồng thời không tạo process vô hạn, `stop` giải phóng tài nguyên.
- [ ] Bằng chứng license/version của **binary và weights cụ thể** ghi trong DECISIONS.md.

## Deliverables

- EngineAdapter thay thế được
- Đánh với AI + hiển thị phân tích
- License review có bằng chứng
- Bộ test timeout/stop/restart

## Không làm trong giai đoạn này

- Bundle Pikafish NNUE chính thức cho mục đích thương mại mà chưa xin phép
- Cho LLM phán nước cờ
- Tạo unbounded engine processes

## Quy trình đóng giai đoạn

1. Đối chiếu từng ô exit criteria với file/test/chức năng thực tế.
2. Chạy test/lint/build đúng script đã có; ghi lệnh, mã thoát và điểm chưa đạt vào `state/HANDOFF.md`.
3. Cập nhật `state/DECISIONS.md` nếu có quyết định kiến trúc/giấy phép, và `state/SESSION_LOG.md` một mục.
4. Chỉ đánh dấu Phase 2 là `DONE` khi đã đủ điều kiện; nếu thiếu thì `IN_PROGRESS` hoặc `BLOCKED`, ghi blocker cụ thể. Không tự động chạy phase 3.

**Đầu mối bước tiếp theo:** Phase 3 sử dụng engine để kiểm chứng đường đi, xây Opening Lab.

**Prompt thực thi:** [`prompts/PHASE_2.md`](../prompts/PHASE_2.md).
