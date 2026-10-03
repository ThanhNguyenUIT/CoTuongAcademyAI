# Hướng dẫn chạy app cờ tướng trên Windows

Hướng dẫn này dành cho việc học cá nhân trên PC tại thư mục:

```text
C:\Users\PC\Documents\CoTuongAcademyAI
```

App gồm giao diện web, backend kiểm tra luật cờ và engine Pikafish đánh cờ. **Mở được giao diện chưa có nghĩa là máy đã đánh được.** Cần đặt `ENGINE_COMMAND` trước khi khởi động app.

## 1. Cài đặt lần đầu

Cần Node.js 20+ và Python 3.11+. Mở **Windows PowerShell**, rồi chạy:

```powershell
cd C:\Users\PC\Documents\CoTuongAcademyAI
npm install
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
```

Chờ từng lệnh hoàn tất. Nếu đã cài thành công trên máy này, bỏ qua phần này và sang phần 2.

Engine trong workspace hiện tại gồm hai file:

```text
.local-engines\Pikafish-Windows-x86-64-universal.exe
.local-engines\pikafish.nnue
```

Hai file phải nằm cạnh nhau. Chúng đã có trên máy được kiểm tra ngày 2026-10-03; chúng không được đóng gói trong source/ZIP. Nếu chuyển app sang máy khác mà thiếu engine, xem [tài liệu engine](docs/ENGINE_LICENSE.md) để cấu hình artifact phù hợp. Bộ Pikafish hiện tại dùng cho học cá nhân phi thương mại theo phạm vi đã ghi trong dự án.

## 2. Mỗi lần mở app

Nếu app đang chạy, nhấn **Ctrl+C trong cửa sổ đang chạy `npm run dev`** để dừng trước. Sau đó chạy các lệnh dưới đây trong **cùng một cửa sổ PowerShell**:

```powershell
cd C:\Users\PC\Documents\CoTuongAcademyAI
.\.venv\Scripts\Activate.ps1
$env:ENGINE_COMMAND = (Resolve-Path '.local-engines/Pikafish-Windows-x86-64-universal.exe' -ErrorAction Stop).Path
npm run dev
```

Nếu có dòng báo lỗi, xử lý lỗi trước khi tiếp tục. Giữ cửa sổ PowerShell này mở trong lúc dùng app.

Mở trình duyệt tại **http://127.0.0.1:5173**.

Trong terminal, cần thấy Vite khởi động và backend chạy tại `http://127.0.0.1:8000`. Nếu Vite tự chọn cổng khác, dừng app và đóng phiên cũ đang dùng cổng 5173 rồi chạy lại; cấu hình local hiện tại dùng cổng 5173.

> `ENGINE_COMMAND` chỉ có hiệu lực trong cửa sổ PowerShell nơi bạn đặt biến và các tiến trình khởi động từ cửa sổ đó. Mở cửa sổ mới thì phải đặt lại. Đặt biến sau khi app đã chạy không cập nhật backend đang chạy.

## 3. Cho máy đánh

1. Vào bàn cờ và đi một nước của bên **Đỏ**.
2. Khi tới lượt Đen, bấm **Đen đi bằng máy** trong khung **Engine local**.
3. Chờ máy tính xong và đi nước Đen, rồi tiếp tục nước Đỏ của bạn.

Hiện tại phải bấm nút cho mỗi lượt Đen; máy chưa tự động đi ngay sau nước Đỏ. Nút bị khóa khi chưa tới lượt Đen hoặc ván đã kết thúc.

Nút **Phân tích · 1 giây** dùng để xem phân tích thế cờ. Chơi máy và phân tích bằng Pikafish **không cần API key LLM**. Gia sư AI là một phần riêng; khi chưa cấu hình LLM, bài học dùng gợi ý đã viết sẵn và hiển thị chế độ fallback.

## 4. Nếu máy không đánh và báo lỗi

### `Set ENGINE_COMMAND to a local UCI engine executable…` hoặc `503 engine_unavailable`

Backend đang chạy chưa nhận cấu hình engine. Đây là lỗi đã xác nhận trên API local ngày 2026-10-03.

Nhấn **Ctrl+C ở terminal đang chạy app**, rồi chạy lại toàn bộ các lệnh ở phần 2. Đừng chỉ đặt biến trong terminal khác khi phiên cũ vẫn chạy.

### `Resolve-Path` báo không tìm thấy engine

Kiểm tra đã ở đúng thư mục và đủ hai file:

```powershell
cd C:\Users\PC\Documents\CoTuongAcademyAI
Test-Path '.local-engines/Pikafish-Windows-x86-64-universal.exe'
Test-Path '.local-engines/pikafish.nnue'
```

Cả hai phải trả `True`. Nếu trả `False`, cần bổ sung đúng artifact local; cài `npm install` hoặc cài thư viện Python không tự cài engine.

### Không chạy được `Activate.ps1` vì PowerShell chặn script

Chỉ cho phép script trong **phiên PowerShell hiện tại**, rồi chạy lại phần 2:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### `No module named uvicorn`

Kiểm tra đã kích hoạt `.venv`, rồi cài dependency bằng đúng Python của dự án:

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.\.venv\Scripts\Activate.ps1
```

Sau đó chạy lại phần 2.

### Cổng 8000 bị chiếm (`WinError 10048` / `address already in use`)

Một backend khác đang chạy. Tìm cửa sổ PowerShell chạy phiên app cũ và nhấn **Ctrl+C**, rồi chạy lại phần 2. Không chạy hai phiên `npm run dev` cùng lúc.

### Lỗi subprocess khi tự chạy backend với `--reload`

Dùng `npm run dev` như phần 2. Script dự án không bật `--reload`, vì chế độ này trên Windows không hỗ trợ asyncio subprocess mà engine cần. Sau khi sửa code backend, dừng và khởi động lại app.

### UI báo không kết nối được backend

Kiểm tra terminal chạy app còn mở và backend không bị thoát. Mở **http://127.0.0.1:8000/health**; bình thường trả:

```json
{"status":"ok"}
```

Kết quả này xác nhận backend hoạt động; để kiểm tra engine, dùng phần 5.

## 5. Kiểm tra engine trực tiếp nếu vẫn còn lỗi

Giữ app chạy theo phần 2. Mở **một cửa sổ PowerShell khác** và chạy:

```powershell
$body = @{
    fen = 'rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR r - - 0 1'
    time_ms = 1000
    depth = 12
    multipv = 1
} | ConvertTo-Json

Invoke-RestMethod -Uri 'http://127.0.0.1:8000/v1/engine/best-move' -Method Post -ContentType 'application/json' -Body $body | Select-Object engine_id, best_move, elapsed_ms
```

Thành công sẽ có `engine_id` chứa Pikafish, `best_move` là một nước cờ và `elapsed_ms`. Nước cụ thể có thể khác nhau giữa các lần chạy.

Nếu vẫn lỗi, giữ lại **nguyên văn thông báo trên UI và lỗi trong terminal chạy app** để chẩn đoán tiếp.

## 6. Dừng app và dữ liệu học tập

Nhấn **Ctrl+C trong terminal chạy app** để dừng. Lần sau mở lại theo phần 2.

Tiến độ học được lưu tại `.local-data/learning.sqlite3`; định danh người học/ván cờ được giữ trong trình duyệt. Giữ nguyên địa chỉ `http://127.0.0.1:5173` và dùng cùng hồ sơ trình duyệt để tiếp tục. Tránh xóa dữ liệu trình duyệt hoặc file SQLite nếu muốn giữ tiến độ.

## Bằng chứng kiểm tra hướng dẫn

Ngày 2026-10-03: API local chưa đặt biến trả `503 engine_unavailable`; sau khi cấu hình Pikafish và chạy backend thử tại cổng 8765, luồng **Đỏ đi `e3e4` → máy trả nước Đen → backend áp dụng nước Đen hợp lệ → tới lượt Đỏ** trả HTTP 200. Hai test tích hợp engine thật đạt 2/2. Đây là kiểm tra API/engine; chưa thực hiện thao tác bấm nút thủ công trong trình duyệt ở phiên này.
