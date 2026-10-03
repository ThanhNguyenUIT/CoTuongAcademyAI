# Xiangqi AI Academy — prototype local

> Prototype local hiện hoàn tất Phase 0–5; Phase 6 (Release) đang chờ. Có bàn cờ, engine UCI local, Opening Lab, gia sư AI dựa trên evidence và hồ sơ học tập local.

## Bắt đầu trong 3 bước

1. Giải nén ZIP. Nếu tạo dự án **mới**, mở thư mục `xiangqi-ai-academy-codex/` vừa giải nén làm workspace Codex. Nếu đã có repository/dự án, chép **toàn bộ nội dung bên trong** thư mục đó vào root của dự án (nơi Codex sẽ chạy). Không chỉ chép riêng một prompt, vì prompt liên kết đến các tài liệu, checklist và trạng thái khác.
2. Mở Codex **tại thư mục chứa `AGENTS.md`**, đọc [`START_HERE.md`](START_HERE.md), rồi yêu cầu: `Hãy đọc START_HERE.md và thực hiện đúng prompts/PHASE_0.md. Không làm các giai đoạn sau.`
3. Khi Codex hoàn thành và các tiêu chí nghiệm thu của Giai đoạn 0 đã được kiểm tra, lần sau chỉ cần yêu cầu: `Hãy đọc START_HERE.md rồi prompts/RESUME.md để tiếp tục đúng giai đoạn kế tiếp chưa hoàn thành.`

## Cấu trúc

| Vị trí | Công dụng |
| --- | --- |
| [`START_HERE.md`](START_HERE.md) | **File điều hướng chính**: thứ tự đọc, khóa giai đoạn, cách bắt đầu và tiếp tục. |
| [`AGENTS.md`](AGENTS.md) | Quy tắc lâu dài cho Codex, ngắn và có tính bắt buộc. |
| [`docs/`](docs/PRODUCT_SPEC.md) | Mục tiêu, kiến trúc, hợp đồng dữ liệu/API, nội dung, chất lượng, bản quyền và nguồn. |
| [`plans/`](plans/PHASE_0.md) | Công việc, tiêu chí nghiệm thu, cổng chuyển giai đoạn. |
| [`prompts/`](prompts/PHASE_0.md) | Prompt **thực thi** theo từng giai đoạn; có prompt tiếp tục phiên mới. |
| [`state/PROJECT_STATUS.md`](state/PROJECT_STATUS.md) | Nguồn sự thật duy nhất về tiến độ. Không đánh dấu xong theo suy đoán. |
| [`state/DECISIONS.md`](state/DECISIONS.md) | Sổ quyết định kỹ thuật; ghi rõ vấn đề chưa chốt. |
| [`state/HANDOFF.md`](state/HANDOFF.md) | Tóm tắt thay đổi, kiểm thử, blocker, bước tiếp theo sau mỗi phiên. |
| [`state/SESSION_LOG.md`](state/SESSION_LOG.md) | Nhật ký ngắn các phiên Codex, không thay thế trạng thái. |

## Quy ước

- Các file `.md` đã có sẵn **không được Codex tạo lại/ghi đè** trong Giai đoạn 0. Chỉ được cập nhật phần trạng thái, nhật ký và tài liệu khi có lý do được ghi nhận.
- Chỉ chuyển sang giai đoạn tiếp theo khi **điều kiện hoàn thành (exit criteria)** đạt và ghi bằng chứng lệnh/test vào `state/HANDOFF.md`.
- **Không tự `git init`, commit, push hay tạo remote**. Nếu thư mục đã có Git do bạn chủ động tạo, Codex cũng không tự commit/push.
- Không đưa API key vào frontend hoặc tài liệu.
- Quyết định về giấy phép engine và bộ trọng số phải được xử lý trước khi thương mại hóa; xem [`docs/ENGINE_LICENSE.md`](docs/ENGINE_LICENSE.md).

## Sau khi giải nén

Bạn có thể dùng Codex CLI trong terminal hoặc Codex extension trong VS Code. Điều quan trọng là mở đúng thư mục dự án, không phải hình thức nhập prompt. Nếu chạy nhiều phiên, mỗi phiên bắt đầu bằng `prompts/RESUME.md`, thay vì dựa vào trí nhớ của phiên trước.

## Chạy ứng dụng local

Cần Node.js 20+ và Python 3.11+.

**Hướng dẫn dùng hằng ngày và xử lý lỗi máy không đánh:** [HUONG_DAN_CHAY_APP.md](HUONG_DAN_CHAY_APP.md).

**Hướng dẫn học với app, hiểu UI và luyện suy luận:** [HUONG_DAN_HOC_CO_TUONG.md](HUONG_DAN_HOC_CO_TUONG.md).

### Windows PowerShell

```powershell
npm install
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
# Bật máy đánh cờ với binary đã có trong workspace này.
$env:ENGINE_COMMAND = (Resolve-Path '.local-engines/Pikafish-Windows-x86-64-universal.exe' -ErrorAction Stop).Path
npm run dev
```

Frontend: http://127.0.0.1:5173 · Backend health: http://127.0.0.1:8000/health

Chạy các lệnh trong **cùng một cửa sổ PowerShell**, tại thư mục dự án. `ENGINE_COMMAND` cần được đặt **trước** `npm run dev` để backend nhận cấu hình. Nếu chỉ muốn mở bàn cờ và bài học, có thể bỏ dòng này; máy đánh và phân tích engine sẽ chưa hoạt động. Binary/weights không nằm trong ZIP/source; nếu `Resolve-Path` báo không tìm thấy, cần cấu hình engine local theo mục dưới, không tiếp tục với đường dẫn lỗi.

### Bật engine Xiangqi local (Phase 2)

Engine binary và weights nằm ngoài source trong thư mục local bị gitignore. Với artifact Pikafish đã được kiểm thử trong workspace, đặt biến trước khi chạy backend:

```powershell
.\.venv\Scripts\Activate.ps1
$env:ENGINE_COMMAND = (Resolve-Path '.local-engines/Pikafish-Windows-x86-64-universal.exe').Path
npm run dev
```

Nếu UI mở được nhưng máy đánh báo `Set ENGINE_COMMAND to a local UCI engine executable…` hoặc `503 engine_unavailable`, dừng ứng dụng bằng **Ctrl+C** trong terminal đang chạy, rồi chạy lại ba lệnh trên trong chính terminal đó. Đặt biến trong cửa sổ khác hoặc sau khi backend đã chạy không cập nhật cấu hình của backend đang chạy. `GET /health` trả `ok` chỉ xác nhận backend hoạt động, chưa xác nhận engine được cấu hình.

Trên bàn cờ, đi một nước Đỏ rồi bấm **Đen đi bằng máy**. Hiện tại nút này yêu cầu máy đánh từng lượt; máy chưa tự động đi sau mỗi nước của bạn. Chơi máy dùng engine UCI local, không cần API key LLM.

Backend không bật Uvicorn `--reload`: trên Windows, chế độ reload dùng Selector event loop không hỗ trợ asyncio subprocess mà UCI engine cần. Frontend vẫn có Vite HMR; sau khi sửa backend, khởi động lại `npm run dev`.

Tiến độ Phase 5 được lưu local tại `.local-data/learning.sqlite3` (gitignored). Có thể xuất/xóa tiến độ trong dashboard. API tiến độ chỉ dành cho app local; chưa có tài khoản/xác thực hoặc đồng bộ cloud. Lịch ôn mặc định 1, 3, 7 ngày, có thể đặt bằng `LEARNING_REVIEW_INTERVALS_DAYS`.

### Phase 6 — readiness và runbook local

Phase 6 chưa triển khai public. Xem [báo cáo beta readiness](docs/BETA_READINESS.md), [kiểm kê giấy phép](docs/RELEASE_LICENSE_AUDIT.md) và [runbook beta local](docs/LOCAL_BETA_RUNBOOK.md). Chỉ chạy beta local có giám sát; chưa có quyền phân phối nội dung/engine, cohort beta thật hay capacity measurement trên môi trường beta.

Đặt `pikafish.nnue` cạnh binary. Artifact này chỉ dành cho mục đích phi thương mại theo điều khoản upstream; không dùng cho dịch vụ thương mại. Fairy-Stockfish 14.0.1 XQ với NNUE Xiangqi tích hợp cũng đã được kiểm thử và có thể chọn bằng cách đổi `ENGINE_COMMAND`. Để chạy lại trong cửa sổ PowerShell mới, đặt lại biến. Khi chưa cấu hình binary, API trả `503 engine_unavailable`; ứng dụng không giả lập kết quả engine. Xem [`docs/ENGINE_LICENSE.md`](docs/ENGINE_LICENSE.md) và [`state/DECISIONS.md`](state/DECISIONS.md) để biết version, hash, kết quả spike và giấy phép.

### Ubuntu

```bash
npm install
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
npm run dev
```

`npm run build`, `npm run lint`, `npm run typecheck`, `npm test` chạy kiểm tra frontend. Với môi trường Python đã kích hoạt, `python -m pytest` chạy kiểm tra backend. `npm run dev` khởi chạy cả hai tiến trình; có thể dùng `npm run dev:frontend` và `npm run dev:backend` riêng.
