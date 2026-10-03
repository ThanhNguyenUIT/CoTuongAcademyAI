# Chiến lược kiểm thử, chất lượng, bảo mật và giám sát

## 1. Quality gates theo phase

| Phase | Automated tests bắt buộc | Kiểm thử thủ công |
| --- | --- | --- |
| 0 | `GET /health`, frontend smoke, typecheck/lint | frontend/backend khởi động local |
| 1 | luật đi quân, chiếu, mặt tướng, FEN round-trip, history/undo, từ chối nước sai | bàn cờ desktop/mobile |
| 2 | mock UCI transcripts, timeout/cancel/restart, illegal PV rejection, score perspective | engine thật chạy local nếu license đáp ứng |
| 3 | import/validate dữ liệu, legal branch paths, transposition, lesson navigation | thử 1 chương đầu-cuối |
| 4 | schema tutor, evidence policy, prompt injection fixtures, fabricated moves blocked | đánh giá bởi người hiểu cờ |
| 5 | rubric scoring, deterministic scheduling, idempotent attempts, data separation | người học có điểm yếu khác nhau nhận bài khác nhau |
| 6 | load, release smoke, security regression, accessibility, license checklist | UAT, beta nhỏ |

## 2. Fixtures cờ cần tạo ở Phase 1

- Vị trí khai cuộc chuẩn + số nước đi hợp lệ xác minh với hai nguồn/rules reference độc lập nếu có thể.
- Điểm kiểm tra chiếu, chống chiếu, Tướng không đối mặt trực tiếp, chặn chân Mã, ngáng mắt Tượng, Pháo ăn có quân ngòi, quân qua sông.
- Lặp vị trí/chiếu liên tục/đuổi liên tục theo luật thi đấu được chọn, kèm lịch sử nước đi; không đơn giản hóa thành “ba lần lặp là hòa” nếu không đúng ruleset.
- Bộ tests snapshot FEN/ICCS với orientation Đỏ ở dưới, Đen ở trên và đảo góc nhìn UI.

## 3. AI Tutor safety và độ tin cậy

- Chỉ dùng LLM để **diễn giải/tutor**, không chấp nhận lệnh “hợp lệ” khi rules xác nhận sai.
- Truy xuất nội dung có provenance, gắn `review_status` và version; không để chuỗi từ học liệu thành system instruction.
- Validate output theo schema. Kiểm tra mọi move/PV được nêu; nếu không xác minh được, bỏ nhánh hoặc nêu bất định.
- Không tiết lộ API key hoặc prompt bí mật trong lỗi trả về client.
- Nếu engine/LLM không sẵn sàng, fallback bài học có chú giải; không giả vờ phân tích đã hoàn tất.
- Đánh giá trên các ca “đối phương cố tình đi khác bài”, multi-step tactic và các trường hợp ambiguous/không đủ chứng cứ.

## 4. Bảo mật và riêng tư

- CORS theo môi trường; secret chỉ backend. Rate limit cho API phân tích và tutor, timeout toàn bộ thao tác engine.
- Không thực thi nước đi, đoạn văn học liệu hay prompt người dùng thành shell command.
- Mọi file import có schema, giới hạn size và kiểm soát đường dẫn.
- Nếu có tài khoản: bảo đảm người học chỉ truy cập dữ liệu của chính mình; chính sách xóa/export và thời hạn lưu log cần được chốt trước beta.
- Với sản phẩm phục vụ trẻ em, bổ sung đánh giá chính sách quyền riêng tư trước public release; MVP local không tuyên bố tuân thủ pháp lý chưa kiểm chứng.
- Phase 5 lưu lời giải tự do và lịch sử ván trong SQLite local. Profile UUID là định danh ngẫu nhiên, không phải auth; learning API hiện chỉ dành cho loopback/local và tự từ chối `APP_ENV=production`. Không bind public host hoặc bật cloud trước khi có authz, privacy notice/review, retention và backup policy. Export JSON và xóa toàn bộ learner/game/attempt/schedule có sẵn.
- Không log câu trả lời người học. Số điểm prototype chỉ gồm lựa chọn khớp trọng tâm bài (1) và có nhập lý do (1); không suy đoán chất lượng lập luận. Rubric checkbox là self-report và hiển thị cỡ mẫu, không phải mastery/Elo.

## 5. Quan sát và chi phí

Log theo request id, không đưa secret hoặc toàn bộ lịch sử cá nhân vào log. Các metric thiết thực: engine timeout, p95 analysis latency, số token LLM, tỷ lệ fallback, tỷ lệ bài tập thất bại, chi phí ước tính trên mỗi học viên. Cache engine analysis có provenance và version.

**Quy tắc báo cáo:** mỗi lần nghiệm thu phải ghi lệnh và kết quả thực tế vào `state/HANDOFF.md`. Không được chỉ ghi “test pass” khi chưa chạy.
