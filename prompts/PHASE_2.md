# PROMPT THỰC THI — PHASE 2: Engine Adapter & Analysis

> Dùng file này làm yêu cầu công việc khi đã tới đúng Phase 2. File này không chứng minh rằng phase trước đã hoàn tất.

Bạn là Codex, Senior Full-stack Engineer kiêm Software Architect và người triển khai nền tảng giáo dục cờ tướng. **Chỉ thực hiện Phase 2.**

## Trình tự bắt buộc

1. Đọc `START_HERE.md`, `AGENTS.md`, `state/PROJECT_STATUS.md`, `state/HANDOFF.md` và **toàn bộ** `plans/PHASE_2.md`.
2. Kiểm tra cổng bắt đầu Phase 2 từ `state/PROJECT_STATUS.md`; với Phase > 0 phải có Phase trước `DONE` cùng bằng chứng. Nếu không đạt, **dừng phần code phase này** và ghi blocker thay vì bỏ qua.
3. Đọc tài liệu domain trong mục “Tài liệu phải đọc” của plan; quan sát source code hiện tại trước khi sửa.
4. Triển khai theo các mảnh nhỏ có test, tránh thay framework, tránh code không thuộc phase.
5. Chạy build/lint/typecheck/test và kiểm thử tích hợp có thể chạy trong môi trường hiện tại. Báo cáo lệnh thật và kết quả.
6. Cập nhật `state/PROJECT_STATUS.md`, `state/HANDOFF.md`, `state/SESSION_LOG.md`; cập nhật `state/DECISIONS.md` nếu có quyết định mới. **Không tự chạy phase tiếp theo.**

## Đầu việc giai đoạn này

**Chơi với engine cờ tướng và xem biến phân tích có provenance, timeout và kiểm soát giấy phép.**

- [ ] Làm spike Pikafish vs Fairy-Stockfish (không tự tải trọng số cấm thương mại); so sánh compatibility, hiệu năng local, UCI/UCCI, binary version và giấy phép.
- [ ] Ghi ADR quyết định engine/binary/weights/protocol và phạm vi dùng; nếu chưa đủ bằng chứng giấy phép, chỉ triển khai mock + adapter, giữ phase BLOCKED trước nghiệm thu engine thật.
- [ ] Thiết kế `EngineAdapter` và `MockEngine`, quản lý subprocess: start/isready, position, go, stop/cancel, quit, crash restart; cân nhắc variant options khi engine yêu cầu.
- [ ] Chuẩn hóa score perspective, PV, multipv, depth và version; validate FEN trước khi chạy, validate toàn bộ PV bằng RulesService khi nhận về.
- [ ] API phân tích và chơi với máy có limit CPU/time và timeout; front-end chọn độ khó dựa vào bộ giới hạn đã kiểm thử, không hiển thị chính xác Elo nếu không có calibration.
- [ ] Tạo fixture UCI transcript, logging có kiểm soát và cache theo position/version/limits nếu cần.

## Điều kiện để được ghi DONE

- [ ] Unit test với MockEngine cho normal/timeout/hang/crash/invalid PV và cancellation.
- [ ] Integration test engine thật tại localhost với vị trí chuẩn: trả best move hợp lệ và phân tích đa biến nếu engine hỗ trợ.
- [ ] Kiểm thử orientation: score phải được giải thích nhất quán theo Đỏ/Đen và theo phía tới lượt; đồng bộ hướng nhìn UI.
- [ ] Stress smoke với 2–3 request đồng thời không tạo process vô hạn, `stop` giải phóng tài nguyên.
- [ ] Bằng chứng license/version của **binary và weights cụ thể** ghi trong DECISIONS.md.

## Giới hạn cứng

- Bundle Pikafish NNUE chính thức cho mục đích thương mại mà chưa xin phép
- Cho LLM phán nước cờ
- Tạo unbounded engine processes
- Không khởi tạo/commit/push Git, không cài dịch vụ có phí, không tự triển khai production.
- Không sửa hoặc làm mất tài liệu điều hướng đã được chuẩn bị. Những thay đổi cần thiết phải cập nhật link liên quan.
- Không báo “thành công” nếu test chưa chạy hoặc môi trường thiếu dependency; khi bị chặn ghi rõ trạng thái thực.

## Định dạng báo cáo cuối phiên

1. **Đã thực hiện:** file/module/behavior nào mới hoặc thay đổi.
2. **Bằng chứng:** lệnh test/build/lint, kết quả, manual test nào đã thực hiện.
3. **Điều kiện nghiệm thu:** từng điều kiện đã đạt/chưa đạt.
4. **Rủi ro/blockers:** những việc chưa kiểm chứng (đặc biệt giấy phép, luật cờ, engine, nguồn khai cuộc).
5. **Trạng thái:** Phase 2 `DONE`, `IN_PROGRESS` hay `BLOCKED`, kèm lý do; chỉ dẫn cho phiên sau.
