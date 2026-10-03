# Chuẩn biên soạn kiến thức khai cuộc và bài tập

## 1. “Toàn bộ khai cuộc” là mục tiêu dài hạn, không phải gói nội dung ban đầu

Tổ chức taxonomy tham khảo theo ECCO và các hệ thống được đối chiếu, hỗ trợ tên tiếng Việt và tên/biệt danh khác, nhưng không mặc định một hệ phân loại bao phủ tất cả biến. Dữ liệu là **đồ thị vị trí**, không chỉ một cây nước đi tuyến tính: nhiều trình tự nước đi có thể chuyển vị.

## 2. Học phần MVP: Pháo đầu đối Bình phong mã

Đề xuất một chương bao gồm: (a) mục tiêu phát triển quân của hai bên; (b) 2–3 nhánh mở đầu đã được người duyệt xác thực; (c) một lỗi chiến thuật phổ biến và phương án phản công; (d) bài luyện chọn kế hoạch, bài luyện dự đoán nước đối thủ và bài luyện chuyển vị. Nếu không có nguồn đáng tin cậy cho một nhánh, ghi `NEEDS_REVIEW` — không yêu cầu LLM tự bịa nước và gắn nhãn học thuyết.

## 3. Template một biến khai cuộc

```yaml
opening_id: cannon-vs-screen-horse
line_id: example-to-be-reviewed
name_vi: "Pháo đầu đối Bình phong mã — [tên nhánh đã duyệt]"
version: "0.1-draft"
source_refs: []
review_status: draft  # draft | reviewed | published
starting_fen: "<validated FEN>"
moves_iccs: []          # validated legal sequence
learning_outcomes:
  - "Nêu hai mục tiêu phát triển quân của hai bên"
key_positions: []
strategic_ideas: []
counterplay: []
common_mistakes: []
transfer_exercises: []
```

Không đưa ví dụ giả này vào production database như một khai cuộc đã duyệt.

## 4. Template bài tập

Mỗi bài tập có `lesson_id`, `exercise_id`, `version`, `fen`, `side_to_move`, `question_type`, `skill_tags`, `accepted_moves`, `acceptable_plans`, `engine_evidence`, `source_refs`, `hint_ladder` (3 mức), `feedback_per_choice`, `review_status`.

Kiểu câu hỏi nên đa dạng:

- **Identify threat:** phát hiện mối đe dọa của đối phương trước khi hành động.
- **Predict response:** dự đoán 1–3 phương án đối phương và diễn giải hệ quả.
- **Choose plan:** chọn kế hoạch thay vì nhớ đúng duy nhất một nước.
- **Find mistake:** chỉ ra đâu là bước khiến kế hoạch cũ thất bại.
- **Transfer:** cùng một ý tưởng xuất hiện trong vị trí mới/khác thứ tự nước đi.

## 5. Luồng duyệt nội dung

`draft → engine-validated → human-reviewed → published`. Engine có thể cho biết biến hợp lệ, độ ổn định và đòn chiến thuật; **không** tự xác nhận tính đúng đắn của diễn giải lịch sử/trường phái. Nếu chưa có người biên tập chuyên môn, giữ nội dung thử nghiệm và nêu giới hạn rõ ràng.

Lưu nguồn cho mọi khẳng định chuyên môn, nguồn của ván minh họa và điều kiện cấp phép dữ liệu. Không scrape các khóa học có bản quyền rồi đưa nguyên văn vào thư viện.

## 6. Quy tắc mở rộng

- Thêm nội dung bằng import/validator, không sửa trực tiếp component.
- Cho phép source, version và editorial status theo từng annotation; ghi vị trí liên quan, không chỉ ghi ở cấp opening.
- Viết migration khi schema đổi; bài tập cũ phải giữ version để không làm sai lịch sử người học.
- Sau khi chương MVP có số liệu học tập, ưu tiên các nhánh thường gây nhầm lẫn, không chạy theo số lượng node.

### Prototype Phase 3

Chương `cannon-vs-screen-horse` trong `backend/app/knowledge/data/cannon-vs-screen-horse.yaml` đang mang trạng thái `experimental`. Các sequence đã qua RulesService, mỗi line/annotation/exercise có nguồn và version; điều đó chỉ xác minh cấu trúc dữ liệu và tính hợp lệ nước đi, **không** chứng minh đây là các biến tốt hay lý thuyết đã được chuyên gia duyệt. API catalog mặc định chỉ trả bài `published`; frontend prototype yêu cầu hiện nội dung experimental và gắn nhãn trạng thái.
