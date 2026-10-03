# Engine & giấy phép — cổng bắt buộc trước thương mại hóa

**Ngày đối chiếu nguồn:** 2026-09-26. Chính sách/giấy phép có thể thay đổi; kiểm tra lại bản cụ thể khi chọn binary và weights.

## 1. Các lựa chọn

### Pikafish

- Engine cờ tướng giao tiếp UCI, mã nguồn theo **GPLv3**. Việc phân phối có nghĩa vụ GPLv3 tương ứng.
- **Trọng số NNUE chính thức** của Pikafish có điều kiện **không sử dụng thương mại nếu chưa được cho phép**. Không suy luận rằng “chạy trên server là được miễn”.
- Vì thế: không tự động tải/bundle trọng số chính thức vào sản phẩm thương mại; trước khi sử dụng phải có bằng chứng quyền sử dụng hợp lệ.

Nguồn: https://github.com/official-pikafish/Pikafish ; https://github.com/official-pikafish/Networks

### Fairy-Stockfish

- Engine đa biến thể có hỗ trợ Xiangqi và UCI/UCCI, **GPLv3**; dự án có bản WASM cho phân tích client-side.
- Từng binary, WASM bundle và **từng bộ NNUE** phải được rà soát giấy phép riêng; không suy diễn từ giấy phép engine sang mọi trọng số đi kèm.
- Kho `official-pikafish/Networks` nêu bộ trọng số họ huấn luyện cho Xiangqi variant của Fairy-Stockfish theo CC0, nhưng vẫn phải kiểm tra đúng artifact, bản và xuất xứ khi tích hợp.

Nguồn: https://github.com/fairy-stockfish/Fairy-Stockfish ; https://github.com/fairy-stockfish/fairy-stockfish.wasm ; https://github.com/official-pikafish/Networks

### Thư viện luật JS

`xiangqi.js` là **ứng viên nghiên cứu**, không mặc định đầy đủ luật giải đấu. Kiểm tra version, giấy phép, test và khả năng FEN/ICCS trước khi phụ thuộc production: https://github.com/lengyanyu258/xiangqi.js

## 2. Bảng quyết định trước Phase 2

| Câu hỏi | Yêu cầu |
| --- | --- |
| Engine dùng cho MVP? | Chọn bản cụ thể sau spike benchmark/compatibility. |
| Protocol và tọa độ? | Kiểm chứng với fixture, `uci`/`ucci`/variant options nếu có. |
| Binary/NNUE đi kèm? | Danh sách artifact, hash/version, URL nguồn và license riêng. |
| Phạm vi sử dụng? | Local prototype / server / desktop redistribution / paid SaaS cần rà soát khác nhau. |
| GPL nghĩa vụ phân phối? | Có kế hoạch license notice, source offer nếu phân phối; khi nghi ngờ hỏi tư vấn pháp lý. |
| Nếu chưa chốt? | Chạy `MockEngine` hoặc engine/weights được xác minh, không hạ thấp license gate. |

## 3. Điều kiện ghi trong DECISIONS.md

Ghi `engine_name`, `engine_version`, `download_url`, `binary_license`, `weights_file`, `weights_license`, `intended_distribution`, `compatibility_test_result`, `reviewed_by`, `review_date`. Không đánh dấu đã duyệt nếu thiếu bằng chứng.

**Lưu ý:** Nội dung này là checklist kỹ thuật/bản quyền, không thay thế tư vấn pháp lý cho sản phẩm thương mại.

## 4. Kết quả kiểm tra Phase 2 — local-only

Ngày kiểm tra: **2026-09-27** · Máy Windows x86-64 · phạm vi sử dụng đã chốt: **chạy local, phi thương mại**. Cả hai ứng viên dùng UCI, nhận vị trí đầu ván, trả nước hợp lệ và 3 PV; adapter đã chuyển FEN `r/b` của ứng dụng sang `w/b` cho Pikafish và chuyển tọa độ rank `1–10` của Fairy-Stockfish về ICCS `0–9`.

| Engine/artifact đã chạy | License artifact | Phân tích local cùng vị trí, time 1000 ms, depth 12, MultiPV 3 | Kết quả |
| --- | --- | --- | --- |
| Pikafish 2026-09-06, commit `4c17cee`; binary `Pikafish-Windows-x86-64-universal.exe`, SHA-256 `0D57D64C212E78F96CBA9E5E4F140D8872F8FAA42EA631A27AB6C5DB08509DA3` | Binary GPLv3; `pikafish.nnue` SHA-256 `7D13D73569A9B571BA0EB20CF1596247BC2A42738967E61AFEF6482B231E900E`, license kèm release: legal use, **không thương mại nếu chưa được phép** | 428–467 ms, depth 12, 3 PV | PASS; 3 request đồng thời dùng cùng PID, stop và restart sau crash đều PASS |
| Fairy-Stockfish 14.0.1 XQ, commit `433d411`; binary `fairy-stockfish-largeboard_x86-64.exe`, SHA-256 `38C173576C13407B610A03DA8C31144BBDEE9F49D9D789C4E7B681CC18D36221` | Binary GPLv3; NNUE tích hợp `xiangqi-83f16c17fe26.nnue`, CC0 theo kho Networks chính thức | 795–911 ms, depth 12, 3 PV | PASS; 3 request đồng thời dùng cùng PID, stop và restart sau crash đều PASS |

Benchmark là vài lượt smoke trên máy local này, không phải so sánh Elo/benchmark tái lập trên nhiều máy. Lựa chọn cho cấu hình local hiện tại là Pikafish vì bản mới hơn và thời gian đo thấp hơn trong smoke này. Không hiển thị Elo đã hiệu chuẩn. Chỉ dùng weights Pikafish theo điều khoản phi thương mại hiện hành; trước khi phân phối hoặc đổi mục đích sử dụng phải rà soát license lại. Binary và weights ở `.local-engines/` bị gitignore, không được bundle vào source.

Nguồn artifact cụ thể: [Pikafish 2026-09-06 release](https://github.com/official-pikafish/Pikafish/releases/tag/Pikafish-2026-09-06), [Fairy-Stockfish 14.0.1 XQ release](https://github.com/fairy-stockfish/Fairy-Stockfish/releases/tag/fairy_sf_14_0_1_xq), [license Pikafish Networks/weights](https://github.com/official-pikafish/Networks), [Fairy-Stockfish license](https://github.com/fairy-stockfish/Fairy-Stockfish).
