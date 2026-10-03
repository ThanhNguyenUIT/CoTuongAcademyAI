# HANDOFF — bản bàn giao gần nhất

## Phase 6 — Giải thích cảnh báo IDE (2026-10-03)

- Người dùng hỏi ảnh hưởng của hai cảnh báo SQL thiếu data source, anchor #home, đường dẫn entry Vite và throw caught locally. Chỉ chẩn đoán, không sửa source hoặc cấu hình IDE.
- Đọc App.tsx xác nhận href="#home" có section id="home" ngay trong cùng component. `Test-Path frontend/src/main.tsx` → True; index.html dùng /src/main.tsx, phù hợp root frontend của Vite. Nguyên nhân cụ thể IDE không resolve chưa được xác minh bằng UI.
- Board.tsx: throw khi engine trả FEN khác hoặc nước không nằm trong legal moves; catch hiển thị message, finally gọi setEngineBusy(false). Luồng này có chủ đích và không làm lỗi thoát ra ngoài handler.
- `npm run build` → exit 0, PASS: tsc -b và Vite 6.4.3, 34 modules, build 711ms. `npm run lint` → exit 0, PASS. Không chạy lại unit/integration/typecheck riêng vì chưa đổi hành vi và build đã gồm TypeScript.
- PowerShell here-string chuyển vào `.\.venv\Scripts\python.exe -`: chạy riêng mỗi migration bằng sqlite3.connect(':memory:') / executescript, assert có bảng → exit 0, PASS cho cả 001_learning.sql và 001_opening_knowledge.sql. Không kết nối hoặc ghi database học thật.
- Đối chiếu tài liệu chính thức [JetBrains inspection](https://www.jetbrains.com/help/inspectopedia/SqlNoDataSourceInspection.html) và [Vite guide](https://vite.dev/guide/). Các cảnh báo đã nêu không chứng minh lỗi runtime trong source hiện tại; chưa kiểm tra lại browser/manual hoặc cấu hình IDE. Cập nhật ba file trạng thái, không có ADR, Phase 6 giữ IN_PROGRESS.

## Phase 6 — Bổ sung `.gitignore` (2026-10-03)

- Người dùng yêu cầu sửa theo kết quả rà soát trước. Thêm `.env.*`, ngoại lệ `!.env.example`, `*.py[cod]`, `.coverage`, `.coverage.*`, `coverage/`, `htmlcov/`, `*.log` và `.idea/`; giữ các quy tắc cũ, thêm newline cuối file.
- Trạng thái đầu phiên khác phiên rà soát: file dự án đã được staged, bao gồm năm file .idea. `git ls-files -- .idea` và `git diff --cached --stat -- .idea` → exit 0, xác nhận đúng năm file IDE được thêm vào index.
- `git rm -r --cached -- .idea` → exit 0: chỉ gỡ năm file IDE khỏi index để ignore có hiệu lực; không xóa file trên máy, không gỡ các file dự án khác hoặc tự stage thay đổi .gitignore.
- PowerShell here-string chuyển vào `.\.venv\Scripts\python.exe -`, dùng `subprocess.run(['git', 'check-ignore', '--no-index', '-q', '--', path])` và assert mã thoát cho từng mẫu → exit 0, **PASS: 22 đường dẫn ignore, 5 đường dẫn giữ**. Bao gồm .env ở root/frontend, dependency/build/cache/engine/data/backup, bytecode, coverage/log/IDE; giữ .env.example ở root/frontend, package-lock và source Python/TypeScript.
- Cùng kiểm tra xác nhận `git ls-files -- .idea` rỗng và cả năm file IDE vẫn tồn tại trên đĩa. `git diff -- .gitignore` → exit 0, chỉ thêm chín quy tắc và newline cuối file; Git thông báo LF sẽ đổi sang CRLF khi chạm file theo cấu hình hiện tại.
- Không chạy lint/typecheck/unit/integration ứng dụng vì chỉ sửa ignore và Markdown, không đổi hành vi runtime; kiểm tra liên quan trực tiếp đã PASS. Cập nhật ba file trạng thái, không thêm ADR, commit/push hoặc đóng phase. Phase 6 giữ `IN_PROGRESS` theo các release gate cũ.

## Phase 6 — Kiểm tra `.gitignore` (2026-10-03)

- Yêu cầu chỉ kiểm tra chất lượng ignore; không sửa `.gitignore` hoặc source. Cập nhật ba file trạng thái theo AGENTS.md; không có ADR mới, Phase 6 giữ `IN_PROGRESS`.
- `git status --short` và `git rev-parse --show-toplevel` → exit 0; Git root đúng workspace, các file dự án chưa tracked; `.idea/` hiện trong danh sách untracked. Git metadata đã tồn tại, khác ghi nhận lịch sử ngày 2026-09-27; không tự tạo hoặc thay đổi metadata.
- PowerShell here-string chứa đường dẫn mẫu chuyển vào `git check-ignore --no-index -v --stdin` → exit 0: ignore đúng `.env`, node_modules ở root/frontend, frontend/dist, .venv, __pycache__, .pytest_cache, .local-engines và .local-data (bao gồm backup). `.idea/workspace.xml` được ignore bởi `.idea/.gitignore`.
- Các mẫu `.env.local`, `.env.production`, `frontend/.env.local`, `backend/app/main.pyc`, `frontend/coverage/index.html`, `.coverage`, `htmlcov/index.html`, `app.log` chưa được ignore. `.env.example` và `package-lock.json` không bị ignore, phù hợp giữ mẫu cấu hình và lockfile. `tsbuildinfo` hiện nằm trong node_modules nên đã được bao phủ.
- `git ls-files` → exit 0, không có đầu ra (chưa có tracked file); `git ls-files --others --exclude-standard` → exit 0, chỉ liệt kê file dự án và một số cấu hình .idea, không liệt kê engine/dữ liệu học/dependency/build/cache đang tồn tại.
- Đề xuất thêm `.env.*` với ngoại lệ `!.env.example`, `*.py[cod]`, `.coverage`, `.coverage.*`, `coverage/`, `htmlcov/`, `*.log`; cân nhắc `.idea/` nếu không chia sẻ cấu hình IDE. Dữ liệu SQLite/backup phải tiếp tục đặt trong `.local-data/`; chưa có quy tắc chặn đường dẫn tùy chỉnh ngoài đó.
- Không chạy lint/typecheck/unit/integration vì chỉ rà ignore và ghi nhận Markdown, không thay đổi hành vi ứng dụng; kết quả test các phiên trước không được coi là test mới. Chưa đóng exit criteria beta/release.
- Kiểm tra ghi nhận bằng PowerShell here-string chuyển vào `.\.venv\Scripts\python.exe -`: lần đầu exit 1 vì so sánh chuỗi giả định `.gitignore` có newline cuối file; kiểm tra lại bằng `splitlines()` → exit 0, PASS, tám quy tắc gốc được giữ và ba file trạng thái có entry rà soát.

## Phase 6 — Hướng dẫn học với app và hiểu UI (2026-10-03)

- Yêu cầu: người dùng chưa hiểu các khối UI, chơi theo bản năng và chưa biết dùng app để học; tạo một file Markdown hướng dẫn luyện nâng cao trình độ. Chỉ làm tài liệu trong Phase 6, không sửa source hoặc mở curriculum mới.
- Thêm [`../HUONG_DAN_HOC_CO_TUONG.md`](../HUONG_DAN_HOC_CO_TUONG.md), link trong README: buổi đầu 30 phút, bảng UI, nhận diện quân/ICCS/FEN, tải hai thế bài lên bàn, ví dụ dựa trên YAML experimental, gợi ý 3 tầng, kiểm tra dự đoán bằng engine, luyện đoạn ván ngắn/đánh lại, dashboard, bảy buổi luyện và mẫu nhật ký.
- Đối chiếu `App.tsx`, `Board.tsx`, `OpeningLab.tsx`, `LearningDashboard.tsx`, `learningApi.ts`, học liệu `cannon-vs-screen-horse.yaml`, `learning/service.py`, `learning/taxonomy.json` và `tutor/service.py`. Tài liệu nêu rõ UI chưa tự đồng bộ thế của Opening Lab lên Board, tutor trên UI không tư vấn mọi thế tự do, engine chỉ có nút đi Đen, PV chưa tự replay, chưa có danh sách mở lại ván cũ hoặc nhập JSON đã xuất.
- Không hứa nước tốt nhất/tăng Elo. Các lựa chọn “correct” phản ánh trọng tâm bài, có thể có lựa chọn khác vẫn hợp lệ; số điểm chỉ tính khớp mục tiêu và có lý do. Rematch chỉ lấy mẫu tối đa ba mốc, không rà mọi nước. Ghi chú ván tự do và việc theo dõi dùng gợi ý/dự đoán phải thực hiện ngoài app.
- Kiểm tra tài liệu bằng PowerShell here-string chuyển vào `.\.venv\Scripts\python.exe -`: so sánh chính xác hai FEN trong guide với YAML; `xiangqi.apply_move` xác nhận cả năm chuỗi lựa chọn/counterplay hợp lệ; replay line A/B xác nhận cùng FEN bài thứ hai; kiểm tra link Markdown local của guide/README → exit 0, **PASS**. Không gọi engine thật hoặc ghi database học của người dùng.
- `$guideTestPath = Join-Path (Get-Location).Path ('.local-data/pytest-guide-' + [guid]::NewGuid().ToString('N')); if (Test-Path -LiteralPath $guideTestPath) { throw 'Temporary test path already exists' }; .\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp $guideTestPath backend/tests/test_knowledge.py backend/tests/test_learning.py backend/tests/test_engine_api.py` → exit 0, **31 passed**, 21 deprecation warnings, 1.83s.
- `npm test` (quyền cho esbuild đọc thư mục cha workspace) → exit 0, **6 passed / 2 files**, 2.43s. `npm run lint`, `npm run typecheck` → exit 0, **PASS**. Không thêm test mới hoặc chạy lại full backend/build vì chỉ thêm Markdown; kết quả full suite/build của yêu cầu chạy app trước đó giữ riêng ở mục dưới.
- Chưa thực hiện browser/manual hoặc đo hiệu quả giáo dục. Lịch luyện là đề xuất dùng tính năng hiện tại; chưa có kết quả chứng minh nâng trình độ. Phase 6 tiếp tục `IN_PROGRESS`, các exit criteria beta/release còn mở; không có ADR mới.

## Phase 6 — Chẩn đoán máy không đánh và hướng dẫn chạy app (2026-10-03)

- Yêu cầu: chạy theo README mở được UI nhưng máy đánh lỗi; sau đó yêu cầu tạo một file Markdown hướng dẫn chạy app đúng. Phạm vi: chẩn đoán startup local và tài liệu, không sửa source/hành vi, kiến trúc hoặc mở phase.
- Đã xác nhận trực tiếp phiên local: `GET http://127.0.0.1:8000/health` HTTP 200; `POST /v1/engine/best-move` HTTP 503, `engine_unavailable`, message `Set ENGINE_COMMAND to a local UCI engine executable to enable engine analysis.` UI tại 5173 trả HTTP 200. Không dừng phiên app của người dùng.
- Nguyên nhân trong hướng dẫn: block chạy nhanh Windows trước đây chưa đặt biến engine; bước bật engine ở mục riêng. Biến cần được đặt trong cùng terminal trước khi khởi động backend; cửa sổ PowerShell mới cần đặt lại. Board hiện yêu cầu bấm `Đen đi bằng máy` mỗi lượt, không tự đánh.
- Thêm [`../HUONG_DAN_CHAY_APP.md`](../HUONG_DAN_CHAY_APP.md): cài lần đầu, chạy hằng ngày, bật engine, nút chơi, kiểm tra API, troubleshooting và giữ dữ liệu. README có link và bổ sung biến trong block Windows. Binary/weights hiện có; không tải/cài engine hay LLM.
- `$env:ENGINE_COMMAND = (Resolve-Path '.local-engines/Pikafish-Windows-x86-64-universal.exe').Path; .\.venv\Scripts\python.exe -m pytest -q -s -p no:cacheprovider backend/tests/test_engine_integration.py` → exit 0, **2 passed**, 21 deprecation warnings, 2.33s; Pikafish 2026-09-06, depth 12, MultiPV 3, 544 ms; reuse/stop/restart và provenance PASS.
- HTTP smoke: `$env:ENGINE_COMMAND = (Resolve-Path '.local-engines/Pikafish-Windows-x86-64-universal.exe' -ErrorAction Stop).Path; .\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8765`. `Invoke-RestMethod` GET health; POST rules/apply-move `e3e4`; POST engine/best-move (1000 ms, depth 12, MultiPV 1); POST rules/apply-move nước engine → **tất cả HTTP 200**, Pikafish trả `b7e7`, 239 ms, trạng thái `active`, lượt kế tiếp `r`. Server thử đã dừng; kiểm tra 8765 không còn kết nối được. Không ghi tiến độ học của người dùng.
- Lần thử `npm run dev` trong sandbox sau activate, bỏ biến engine ở process thử → exit 1: esbuild bị từ chối đọc thư mục cha và cổng 8000 bị phiên đang chạy chiếm. Đây là hạn chế lần thử, không phải nguyên nhân của lỗi engine trên phiên người dùng. Luồng engine được kiểm chứng bằng server độc lập 8765 thay vì chạy thêm phiên trên cổng 8000.
- `.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` → exit 1, 86 passed/2 skipped/14 setup errors do không được đọc `C:\Users\PC\AppData\Local\Temp\pytest-of-PC`. Chạy lại với thư mục tạm mới trong workspace: `$pytestTaskPath = Join-Path (Get-Location).Path ('.local-data/pytest-run-' + [guid]::NewGuid().ToString('N')); if (Test-Path -LiteralPath $pytestTaskPath) { throw 'Temporary test path already exists' }; .\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp $pytestTaskPath` → exit 0, **100 passed, 2 skipped**, 21 warnings, 2.74s. Hai test engine tích hợp skip trong suite mặc định; đã chạy riêng ở trên.
- `npm test` → exit 0, **6 passed / 2 files**; `npm run lint`, `npm run typecheck`, `npm run build` → exit 0, PASS (Vite 6.4.3, 34 modules). Test/build được chạy với quyền cho esbuild đọc thư mục cha workspace. Không thêm regression test vì chỉ sửa tài liệu.
- Phase 6 giữ `IN_PROGRESS`; exit criteria beta/release vẫn còn mở. Chưa kiểm tra thao tác bấm nút trong browser hoặc xác nhận người dùng đã restart phiên app cũ; bước tiếp theo là dừng terminal cũ và chạy đúng phần 2 trong hướng dẫn. Không có ADR mới.

## Phase 6 — Rà tài liệu nâng cấp/cải thiện (2026-09-30)

- Yêu cầu: đọc lại để tìm tài liệu nói về nâng cấp/cải thiện. Chỉ rà Markdown trong docs/plans/state và điều hướng, không sửa source hoặc chạy test mới.
- Kế hoạch trực tiếp nhất: [`../plans/PHASE_6_LOCAL_APP_REVIEW_PLAN.md`](../plans/PHASE_6_LOCAL_APP_REVIEW_PLAN.md), ngày 2026-09-28. Phải đọc phần implementation/results cùng review findings: resume, rules/cache/save/tutor/queue đã được xử lý; findings ban đầu không phải toàn bộ lỗi vẫn còn mở.
- Còn chờ: manual PC flow; profile HTTP/browser/tutor/dashboard; tối ưu dashboard và graph lookup chỉ khi có bằng chứng bottleneck. Full new-game replay còn tỷ lệ theo độ dài ván.
- PRODUCT_SPEC ghi vòng học quan sát/dự đoán/phản công/giải thích/luyện lại và Master Campaign sau Phase 6 cần quyết định riêng. CONTENT_GUIDE ghi đa dạng bài tập, quy trình duyệt, mở rộng theo lỗi người học sau khi có số liệu MVP.
- ARCHITECTURE ghi ký pháp Việt Nam, cache/streaming khi có nhu cầu, khả năng đóng gói desktop; auth/PostgreSQL/worker chỉ khi có scope multi-user/cloud hoặc tải thực tế. DECISIONS ghi giới hạn luật thi đấu, LLM provider, rubric/rematch heuristic.
- PHASE_6/BETA_READINESS tập trung chất lượng và release gates; không thay thế phạm vi học cá nhân trên PC đã xác nhận. Không thấy plan Phase 7 hoặc roadmap nâng cấp riêng khác trong tập Markdown dự án đã liệt kê.
- Phase 6 giữ `IN_PROGRESS`; không có kết quả kiểm thử mới, không có ADR/kiến trúc mới. Bằng chứng kiểm thử phiên trước giữ nguyên ở mục dưới.

## Phase 6 — Kiểm tra hiện trạng (2026-09-30)

- Yêu cầu: xác định dự án đang làm tới đâu; đọc điều hướng/status/handoff, đối chiếu plan Phase 6 và source. Không sửa hành vi ứng dụng, không triển khai thêm tính năng hoặc chuyển phase.
- Phase 0–5 giữ `DONE` cho prototype local; Phase 6 giữ `IN_PROGRESS`. Code hiện có các module rules/engine/knowledge/tutor/learning, game restore và tối ưu đã ghi ngày 2026-09-28.
- Phát hiện chênh lệch nhỏ: `frontend/src/App.tsx` còn hiển thị “PHASE 5”, trong khi status hiện hành là Phase 6. Chỉ ghi nhận; chưa sửa nhãn.
- `.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` → exit 0, 100 passed, 2 skipped, 21 deprecation warnings, 3.26s. Hai test skip do suite mặc định chưa đặt `ENGINE_COMMAND`.
- `npm test` → exit 0, 6 passed/2 files; `npm run lint`, `npm run typecheck`, `npm run build` → exit 0, PASS. Build Vite 6.4.3, 34 modules. `.\.venv\Scripts\python.exe -m pip check` → exit 0, no broken requirements.
- `$env:ENGINE_COMMAND = (Resolve-Path '.local-engines/Pikafish-Windows-x86-64-universal.exe').Path; .\.venv\Scripts\python.exe -m pytest -q -s -p no:cacheprovider backend/tests/test_engine_integration.py` → exit 0, 2 passed, 21 warnings, 2.37s. Pikafish 2026-09-06: depth 12, MultiPV 3, 495 ms; tái sử dụng process cho 3 request, stop/cancel, restart sau crash và API provenance PASS. Đây là integration smoke local, không phải Elo/SLO.
- Chưa có kiểm tra browser/manual mới, live LLM provider, audit bảo mật mới hoặc profile mới. Học liệu vẫn experimental/chưa được chuyên gia duyệt. Các release gate cũ còn mở; mục tiêu sử dụng riêng trên PC được giữ nguyên.
- Bước tiếp theo: xác nhận luồng học trên PC, đặc biệt move → refresh → resume, import và rematch; xử lý vấn đề cụ thể trong Phase 6. Không đánh dấu DONE chỉ vì automated checks đạt.

## Phase 6 — Local logic/performance implementation (2026-09-28)

- Phạm vi đã làm rõ: chủ dự án chỉ dùng web app để tự học trên PC, không chia sẻ. Không tiếp tục xử lý iPhone/Wi-Fi hoặc public beta trong scope này.
- Sửa lỗi refresh có thể ghi đè lịch sử: frontend đọc game theo learner trước khi mở bàn, khôi phục history/cursor, retry nếu lỗi; game import/rematch lưu starting FEN và dùng ID mới. Thêm route `GET /v1/learning/games/{game_id}` có kiểm tra owner.
- Save game chỉ replay suffix sau common prefix đã lưu, hỗ trợ cắt nhánh có chủ đích và từ chối đổi starting FEN của game đã có lịch sử. Rules API dùng một lần `analyze_position`; knowledge YAML/graph được cache theo fingerprint và trả bản sao; tutor bỏ PV validation trùng sau EngineService; engine queue có timeout riêng 10 giây, search timeout bắt đầu sau khi lấy lock.
- Thêm `scripts/profile_local.py`. Cùng PC, 15 iterations: legal moves median 4.179→2.103 ms (p95 4.315→2.196); apply move 5.757→3.959 ms (p95 6.042→3.979); warm opening lookup 104.953→0.312 ms (p95 105.848→0.344). Append 1 ply vào game 300 ply mới đo 5.111 ms median / 6.894 p95; baseline cũ full-replay khoảng 411.096/420.098 ms nên workload không hoàn toàn tương đương. Tạo mới/replay đủ 300 ply sau sửa: 412.473/448.098 ms. Đây là in-process microbench, không phải browser/HTTP/engine/hosted SLO.
- Kiểm tra thực tế: `\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` → PASS, 100 passed, 2 skipped, 21 warnings (4.28s); `npm test` → PASS, 6 tests (2 files); `npm run lint`, `npm run typecheck`, `npm run build` → PASS; `\.venv\Scripts\python.exe -m pip check` → no broken requirements.
- Regression tests bao phủ resume/append/branch/start-FEN/owner, knowledge cache hit/invalidation/copy isolation và engine queue/search budget. Local browser smoke bằng SQLite tạm xác nhận trang, opening, dashboard tải và API luật trả 44 nước hợp lệ; thao tác click trên bàn qua browser controller ánh xạ sang ô khác nên chưa xác nhận được nước đi + refresh/resume thủ công. Database học hiện tại không bị dùng. Chưa đo tutor latency, HTTP p50/p95, browser long tasks, engine live search hoặc dashboard. Dashboard/graph-index micro-optimization được hoãn do chưa có bằng chứng cần thiết.
- Phase 6 vẫn `IN_PROGRESS`: điều kiện beta/release cũ như rights clearance, full SBOM, beta pre/post và deployment rollback chưa hoàn tất. Theo mục tiêu riêng hiện tại, bước phù hợp tiếp theo là dùng app trên PC, xác nhận refresh/resume và luồng import/rematch bằng thao tác thật, rồi xử lý lỗi học/UI cụ thể nếu gặp. Không cần mobile hoặc public deployment.
- Kế hoạch và profile: [`../plans/PHASE_6_LOCAL_APP_REVIEW_PLAN.md`](../plans/PHASE_6_LOCAL_APP_REVIEW_PLAN.md); API contract: [`../docs/DATA_API.md`](../docs/DATA_API.md).

## Phase 6 — Static source review and personal-local improvement plan

- Thời điểm: 2026-09-28. Phạm vi mục tiêu đã làm rõ: học một mình trên PC local; không tiếp tục xử lý iPhone, cohort hay deployment.
- Rà soát tĩnh frontend/backend, không sửa source và không chạy tests/profiler trong phiên này. Vì vậy các nhận định hiệu năng là điểm nóng suy ra từ code; chưa có số đo route-level.
- Finding cần ưu tiên trước: sau refresh, Board bắt đầu lại từ FEN đầu nhưng `currentBoardGameId()` giữ ID cũ; lần lưu nước tiếp theo gửi lịch sử ngắn mới và upsert có thể ghi đè game đã lưu. Cần thêm regression test và luồng resume trước khi tối ưu.
- Các điểm nóng hiệu năng được thấy: API rules lặp legal/check calculation; YAML knowledge bị đọc/validate và graph dựng lại mỗi request; mỗi nước cờ gửi/replay toàn bộ lịch sử; tutor xác thực PV lặp; engine semaphore cho 3 request nhưng adapter một process khóa tuần tự và timeout tính cả thời gian chờ khóa.
- Cơ hội thấp hơn: progress/recommendation đọc và quét toàn bộ attempts nhiều lần; OpeningLab tìm trong mảng graph mỗi lần điều hướng. Chỉ làm nếu profile chứng minh đáng kể.
- Kế hoạch theo thứ tự: baseline → sửa resume/overwrite game → gộp tính trạng thái luật → cache knowledge có invalidation → bỏ xác thực PV lặp và đo queue engine → lưu suffix incremental nếu benchmark xác nhận → đo lại và chỉ tối ưu dashboard/UI theo profile.
- Plan chi tiết và acceptance criteria: [`../plans/PHASE_6_LOCAL_APP_REVIEW_PLAN.md`](../plans/PHASE_6_LOCAL_APP_REVIEW_PLAN.md). Phase 6 tiếp tục `IN_PROGRESS`; không có kết quả test mới.

## Ghi nhận tiếp theo — phạm vi dùng cá nhân và kiểm tra iPhone

- Chủ dự án xác nhận chỉ dùng app trên máy cá nhân để học, không chia sẻ; ưu tiên hiện tại là dùng trên máy tính. Không tiếp tục xử lý truy cập mobile/Wi-Fi trừ khi được yêu cầu lại.
- Kiểm tra Vite: bind nhầm IP ví dụ `192.168.1.25` trả `EADDRNOTAVAIL`; bind địa chỉ Wi-Fi đúng `192.168.0.147` khởi động thành công và trang mở được trên PC.
- iPhone `192.168.0.140` vẫn không truy cập được `http://192.168.0.147:5173`, dù đã thử hướng dẫn firewall giới hạn theo IP. Chưa có bằng chứng xác nhận nguyên nhân; mobile UAT chưa đạt.
- Kết quả trên chỉ là thử truy cập dev server; không thay đổi source, firewall state chưa được xác minh, không chạy lại automated tests trong phiên hỗ trợ này.
- Bước kế tiếp phù hợp mục tiêu hiện tại: người dùng học thử luồng bài học trên PC; ghi lại lỗi học tập/UI gặp phải rồi xử lý trong Phase 6. Phase 6 vẫn `IN_PROGRESS` theo plan beta/release hiện hành.

## Phase 6 — Beta, Quality & Release | PENDING → IN_PROGRESS (chưa nghiệm thu)

- Thời điểm: 2026-09-27
- Phạm vi phiên này: readiness beta có kiểm soát; không tạo Git metadata, release package, tài khoản/provider trả phí, beta cohort hoặc deployment public.
- Đánh giá threat model/phạm vi: chỉ local trusted user, loopback; learner UUID không phải auth, learning route chặn `APP_ENV=production`; `LLM_PROVIDER=none` mặc định, provider tùy chọn sẽ nhận context/lời giải và cần chấp thuận riêng. Đã ghi privacy notice, quota/timeout/bounds, điều kiện dừng pilot và beta study protocol ở `docs/BETA_READINESS.md`.
- Kiểm kê license/dependency ở `docs/RELEASE_LICENSE_AUDIT.md`: hash/version Pikafish/NNUE/Fairy được đối chiếu; binary và data đang gitignore/không ship. Nguồn học liệu chưa có redistribution grant/educator approval; Pikafish NNUE chỉ cho mục đích local phi thương mại nếu chưa có phép. Dependency npm 366 lock entries: các SPDX/license metadata có thống kê; một entry là workspace riêng của dự án. `.venv` có 27 distributions. `npm sbom --sbom-format=spdx --package-lock-only` chưa tạo được SBOM do lockfile có platform-optional WASI packages không cài trên Windows; quyền phân phối chưa được xác nhận.
- Security/dependencies: lần audit đầu có 3 moderate advisory gián tiếp qua Vitest. Nâng `vitest` và `@vitest/coverage-v8` lên 4.1.11, đặt Vitest root-level để workspace resolve đúng; `npm audit` cuối cùng báo 0 vulnerabilities. Secret-pattern scan không thấy khóa/token private-key dạng phổ biến; `.env` vắng mặt và được gitignore. `pip check` sạch, nhưng không có Python CVE scanner. Đây không phải pentest.
- Công cụ thêm: `scripts/load_smoke.py` đo loopback p50/p95/status; `scripts/backup_learning_db.py` tạo SQLite snapshot mới không ghi đè và chạy `PRAGMA integrity_check`. `docs/LOCAL_BETA_RUNBOOK.md` mô tả start/stop, smoke, backup/recovery thủ công và rollback local.
- Local load evidence cuối: health 20 requests/concurrency 5 → 20×HTTP 200, client p50 8.8 ms/p95 19.5 ms/max 39.5 ms; engine 12 requests/concurrency 2, 300 ms/depth 6 → 12×HTTP 200, client p50 121.3 ms/p95 141.4 ms, engine p50 50 ms/p95 63 ms. Chỉ đo loopback trên máy hiện tại, không suy rộng sang beta/SLO/capacity.
- Backup smoke với SQLite fixture dùng một lần → `Backup verified`, integrity `ok`, một hàng được giữ; source/backup fixture đã xóa. Kiểm thử keyboard board, malformed rules, tutor sanitization/fallback, engine cancel/restart và learner export/delete hiện có trong automated suites; chưa thực hiện touch/mobile/screen-reader UAT hoặc independent WCAG audit.
- Kiểm tra cuối: `.\\.venv\\Scripts\\python.exe -m pytest -q -p no:cacheprovider` → 95 passed, 2 skipped, 20 deprecation warnings; `npm test` → 5 passed (Vitest 4.1.11); `npm run typecheck`, `npm run lint`, `npm run build` → PASS; `npm audit --json` → 0 vulnerabilities; `pip check` → no broken requirements.
- Blockers: chưa có môi trường beta thật/consenting learner cohort; chưa đo pre/post held-out tactics; chưa có quyền phân phối rõ cho nội dung hoặc written permission thương mại cho Pikafish NNUE; chưa hoàn tất full SBOM, touch/mobile UAT hay rollback trên deployment. Workspace không có `.git`, nên chưa thể trỏ đến source tag/release revision. Public release không được thực hiện.
- Phase 6 giữ `IN_PROGRESS`. Disposition cho artifact hiện tại là `READY_FOR_APPROVAL` cho **supervised local evaluation only**; public/hosted beta chưa sẵn sàng. Chỉ tiếp tục đóng phase khi blocker beta thật/quyền phân phối/kiểm thử còn thiếu có bằng chứng; không triển khai public nếu chưa được yêu cầu rõ.

## Phase 5 — Adaptive Learning & Rematch | PENDING → IN_PROGRESS → DONE

- Thời điểm: 2026-09-27
- Phạm vi: taxonomy/rubric MVP, local learning store/API, heuristic luyện và ôn, dashboard, export/delete và rematch. Không mở tài khoản/cloud hoặc bắt đầu Phase 6.
- Backend: `backend/app/learning/` có SQLite migration `001_learning.sql`, taxonomy 6 kỹ năng và mapping tag rõ ràng, xác nhận lại toàn bộ game qua RulesService, attempt lưu game/hint/lý do/self-check/content version, idempotency theo learner + attempt ID, dashboard/next/reviews/rematch/export/delete API. Toàn bộ route learning từ chối `APP_ENV=production` khi chưa có xác thực.
- Rubric chỉ tự chấm hai observable (lựa chọn khớp trọng tâm do bài tập đánh dấu: 1 điểm; đã nhập lý do: 1 điểm). Self-check là lời tự báo cáo, lý do không chấm ngữ nghĩa, không suy ra mastery/Elo. Heuristic ưu tiên review đã đến hạn → lỗi lặp → exercise chưa làm; khoảng ôn mặc định/configurable 1, 3, 7 ngày.
- Rematch engine đánh giá tối đa 3 ply mẫu; giảm ≥100 cp đánh dấu candidate để người học tự chọn checkpoint. Đây là heuristic, không phải nhãn blunder/chuyên môn. Test dùng adapter giả có suy giảm nhân tạo xác nhận đánh dấu/chọn checkpoint; trong browser bằng Pikafish, ván mẫu ba ply trước đó không có checkpoint vượt ngưỡng và UI nói rõ không gán nhãn lỗi.
- Browser E2E local đã gửi câu sai `a9a8` kèm lý do: receipt 1/2 observable points, dashboard tăng lên 1 attempt và 1 lỗi lặp, gợi ý lại `predict-black-response`, due date ngày kế tiếp. UI rematch với ván thật đã lưu được gọi; kết quả không có mốc đạt 100 cp được thông báo trung thực. Các ngày mô phỏng và đường đúng/lặp được kiểm tra bằng đồng hồ deterministic trong backend tests.
- `backend/tests/test_learning.py` chứng minh: hai learner có lỗi khác nhau nhận exercise khác nhau; không rò game/attempt; duplicate idempotent và payload conflict; content-version stale bị từ chối nhưng attempt cũ còn; lịch ôn 1/3 ngày; rematch threshold; export/delete và API isolation. Dữ liệu learner thử nghiệm trong E2E trước được xóa, còn dashboard local hiện 0 attempt.

### Exit criteria Phase 5

| Điều kiện | Kết quả thực tế |
| --- | --- |
| Taxonomy/rubric, game/attempt/version, duplicate và migration | PASS — `backend/app/learning/taxonomy.json`, migration SQL; version conflict/idempotency tests |
| Heuristic cá nhân hóa và lịch ôn deterministic | PASS — due/repeated-error/first exercise; config interval; đồng hồ mô phỏng trong `test_learning.py` |
| Hai learner có lỗi khác nhau; dữ liệu cách ly | PASS — learner A/B nhận bài khác nhau; API/store kiểm tra ownership và export/delete theo learner ID |
| Rematch engine candidate và người học chọn thời điểm | PASS — service/API/UI; adapter test xác nhận score-drop threshold; Pikafish browser smoke xác nhận không gắn nhãn khi mẫu thật không đủ ngưỡng |
| E2E sai/lý do → tiến độ/recommendation/review | PASS — browser local có thật; sai `a9a8`, nhập lý do, receipt 1/2, dashboard/recommendation/due date cập nhật; due schedule mô phỏng trong test deterministic |
| Nguồn gốc chỉ số và quyền dữ liệu | PASS — UI/docs nêu rubric/sample size/local-only; export JSON và DELETE; `APP_ENV=production` chặn learning API khi chưa auth |

### Lệnh và kết quả Phase 5

| Lệnh/thao tác | Kết quả |
| --- | --- |
| `.\\.venv\\Scripts\\python.exe -m pytest -q -p no:cacheprovider` | PASS — 95 passed, 2 skipped (engine integration cần bật riêng), 20 deprecation warnings Starlette/FastAPI/Python 3.14 |
| `npm test` | PASS — 5 frontend tests, gồm lưu replay game/rematch UI và Opening Lab attempt/dashboard |
| `npm run typecheck` | PASS |
| `npm run lint` | PASS |
| `npm run build` | PASS — Vite production bundle |
| Local HTTP smoke: `GET /health`, frontend `/`, `POST /v1/engine/analyze` trên `127.0.0.1` | PASS — health `ok`, frontend 200, Pikafish 2026-09-06 trả `b0c2`, PV hợp lệ, depth 6, 44 ms |
| Browser local Phase 5 E2E | PASS — sai câu trả lời, lý do, cập nhật dashboard/recommendation; game rematch không đạt threshold hiển thị đúng thông báo |

- Lúc đóng phase, frontend ở `http://127.0.0.1:5173/`, backend ở `http://127.0.0.1:8000/`; dashboard trong browser sạch, 0 attempts. Để tự chạy lại trên Windows, kích hoạt `.venv`, đặt `ENGINE_COMMAND` theo README rồi chạy `npm run dev`.
- Phase 5: `DONE` cho prototype local. Giới hạn đã biết: không auth/cloud; review date logic là heuristic; bài học còn experimental; rubric không đánh giá nội dung lời giải; chưa có Elo/mastery. Phase 6 chuyển `LOCKED → PENDING`; dừng ở đây.

## Phase 4 — Evidence-grounded AI Tutor | IN_PROGRESS → DONE

- Thời điểm: 2026-09-27
- Phạm vi: Tutor API/UI, provider boundary, ba tầng gợi ý, evidence filtering, engine PV validation, fallback, eval và Opening Lab E2E. Không triển khai Phase 5.
- Đã thêm schema `TutorContext`/`TutorAnswer`/draft, provider mock và OpenAI-compatible cấu hình qua env, tutor service/API, cache/quota, trace ID/context digest; key không gửi xuống frontend và log không chứa lời giải/lý do người học.
- Policy kiểm tra FEN, legal moves, lesson/engine evidence, provenance cho claim/candidate; loại forced-win/best claim thiếu proof và nước ngoài lesson/PV. Production chỉ nhận nội dung reviewed/published. Experimental vẫn chỉ dùng khi local opt-in; nội dung bài mẫu hiện chưa được chuyên gia duyệt.
- UI Opening Lab yêu cầu đi tuần tự hint 1 → 2 → 3; tier 3 mới nêu nước candidate sau khi người học chọn nước và giải thích lý do. Khi không có LLM, fallback viết sẵn hoạt động; tầng 2–3 vẫn có thể gắn PV engine đã xác thực.
- Eval set có 20 ca: 5 prompt injection, 5 off-theory/thiếu dữ kiện, 5 engine/narrative conflict, 5 claim thắng/best chưa chứng minh. `backend/tests/test_tutor.py::test_twenty_tutor_evaluation_cases` đạt 20/20.
- Rà thủ công mẫu `engine-conflict-01`: provider giả nói “Engine xác nhận b9c7” nhưng PV mock chỉ chứa `a9a8`; output cuối bỏ claim provider, không trả candidate move, giữ fallback gắn evidence lesson, đánh dấu thiếu provenance và PV engine hiển thị đúng `a9a8`.
- Browser E2E local `http://127.0.0.1:5173/`: chọn phản ứng `h9g7`, nhập lý do, nhận đủ hint 1 “Quan sát Pháo…”, hint 2 “Tìm một Mã Đen…”, hint 3 giải thích `h9g7`; UI hiển thị fallback rõ ràng vì LLM chưa cấu hình, và evidence Pikafish depth 8 ở tier 2–3. Không có LLM credentials, nên live provider smoke chưa xác minh.

### Exit criteria Phase 4

| Điều kiện | Kết quả thực tế |
| --- | --- |
| Schema, prompt snapshot, mọi move đã validate, forced-win thiếu proof bị chặn | PASS — `backend/tests/test_tutor.py`; schema/provenance/candidate/claim tests |
| 20 eval và rà tay mẫu sai | PASS — 20/20; engine conflict `b9c7` bị từ chối khi PV chỉ có `a9a8` |
| Không lộ API key; injection không đổi policy | PASS — prompt snapshot, annotation/learner injection, upstream error sanitization và log privacy tests |
| Opening Lab E2E đủ 3 tầng với LLM không cấu hình | PASS — browser local, fallback hiển thị; Pikafish evidence xuất hiện ở tầng 2–3 |
| Live provider smoke | Chưa xác minh — không có provider credentials; mock/local provider tests đạt |

### Lệnh và kết quả Phase 4

| Lệnh/thao tác | Kết quả |
| --- | --- |
| `.\\.venv\\Scripts\\python.exe -m pytest -q -p no:cacheprovider` | PASS — 83 passed, 2 skipped (engine integration cần bật riêng), 12 deprecation warnings Starlette/FastAPI/Python 3.14 |
| `npm test` | PASS — 5 frontend tests |
| `npm run typecheck` | PASS |
| `npm run lint` | PASS, không warning |
| `npm run build` | PASS — Vite transform 32 modules |
| Browser local manual E2E | PASS — Opening Lab, lý do, lựa chọn `h9g7`, 3 tầng fallback và engine evidence |
| Provider conflict sample `engine-conflict-01` | PASS — `b9c7` claim/candidate bị loại; PV evidence vẫn là `a9a8` |

- Phase 4: `DONE` theo exit criteria; giới hạn live provider và trạng thái experimental được ghi rõ. Phase 5 chuyển sang `PENDING`; dừng tại đây.

## Chạy local — sửa lỗi khởi động Windows

- Thời điểm: 2026-09-27
- Lỗi ban đầu: `npm run dev` gọi Python 3.14 hệ thống do chưa kích hoạt `.venv`, nên không tìm thấy `uvicorn`. Frontend bị `concurrently -k` dừng theo khi backend thoát.
- Sau khi dùng `.venv`, Uvicorn `--reload` trên Windows chọn `WindowsSelectorEventLoopPolicy`; loop này không hỗ trợ asyncio subprocess của engine UCI. Bỏ `--reload` khỏi `dev:backend` để chạy với Proactor event loop.
- Cập nhật `README.md` để lệnh PowerShell kích hoạt `.venv` trước khi chạy và ghi rõ cần restart backend sau khi sửa.
- Xác minh thực tế: `npm run dev` sau `.\.venv\Scripts\Activate.ps1` khởi động cả frontend/backend; `GET /health` trả `ok`, UI trả HTTP 200, `POST /v1/engine/analyze` trả best move `h2e2` và 3 PV.
- Phase statuses không đổi. Chi tiết: lần chạy đầu thiếu `.venv`; lần chạy với reload gặp lỗi subprocess; lần chạy cuối với `.venv` và không reload thành công.

## Phiên gần nhất

- Thời điểm: 2026-09-27
- Phase: `3 / PENDING → IN_PROGRESS → DONE`
- Phạm vi: Opening Lab, knowledge graph có transposition, importer/validator YAML/JSON, SQLite migration schema và một chương Learn/Practice.
- Kết quả: thêm Pydantic schema cho Position/Edge/Opening/Line/Annotation/Lesson/Exercise, migration `001_opening_knowledge.sql`, key chuẩn hóa gồm placement + lượt đi. Runtime prototype đọc YAML; migration được chạy/test trên SQLite in-memory, chưa chuyển lưu học liệu sang database.
- Đã thêm 3 line Pháo đầu đối Bình phong mã, graph gộp vị trí chung nhưng giữ sequence và source riêng, endpoint catalog/detail/branches/lesson. Catalog ẩn nội dung chưa published; muốn đọc experimental phải đặt `include_experimental=true`.
- Bài học có 3 bước, câu hỏi bắt ghi lý do trước khi mở feedback, rubric tự kiểm tra, bài transfer, và counterplay moves đã qua RulesService. YAML chứa nguồn/version/review status cho opening, lines, annotations và exercises.
- Trạng thái nội dung: toàn chương và mọi line là `experimental`, chưa có biên tập viên cờ tướng duyệt; không line nào được publish. Source links là tài liệu tra cứu, không phải chứng cứ engine cho tuyên bố nước tốt nhất. Phase này không chạy phân tích engine; các line và phản ứng trong data đã được kiểm tra luật.

### Exit criteria Phase 3

| Điều kiện | Kết quả thực tế |
| --- | --- |
| Mọi published line hợp lệ | Chưa có line published; mọi line experimental qua RulesService trong importer và unit tests |
| Hai đường khác nhau tới cùng canonical position và UI nhận diện | PASS — hai thứ tự mã khác nhau hợp nhất; test graph/API và browser hiển thị node chung với 3 đường |
| Từ chối dữ liệu giả, thiếu nguồn, FEN/nước sai, cycle; draft bị ẩn | PASS — importer tests; catalog mặc định rỗng với nội dung experimental; endpoint detail/lesson mặc định 404 |
| Manual E2E: học, trả lời sai, xem counterplay, retry | PASS — browser local: hoàn tất 3 bước, chọn Xe, nhập lý do, xem phản hồi + line `a9a8 b0c2`, retry và thử phương án khác; rubric/transfer cũng được kiểm tra |
| Có người duyệt hoặc experimental rõ ràng | PASS theo fallback của plan — nguồn liên kết và nội dung gắn experimental trên UI; chưa có human reviewer |

### Lệnh và kết quả

| Lệnh | Kết quả |
| --- | --- |
| `.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` | PASS — 50 passed, 2 skipped (engine integration mặc định cần bật riêng), 11 cảnh báo deprecation Starlette/FastAPI/Python |
| `npm test` | PASS — 5 frontend tests (4 board/engine tests + 1 Opening Lab E2E component test) |
| `npm run typecheck` | PASS |
| `npm run lint` | PASS, không warning |
| `npm run build` | PASS — Vite transform 32 modules |
| `npm run dev` + browser local | PASS — UI load API `GET /v1/openings/cannon-vs-screen-horse?include_experimental=true` 200; thủ công hoàn tất chương, transposition, reason, wrong answer/counterplay/retry |

- Phase 3 `DONE` cho prototype; nội dung chưa phải khai cuộc được chuyên gia xác nhận. Phase 4 chuyển `LOCKED → PENDING`; phiên tới bắt đầu bằng `prompts/PHASE_4.md`. Không triển khai Phase 4 trong phiên này.

## Phiên trước — Phase 2

- Thời điểm: 2026-09-27
- Phase: `2 / PENDING → IN_PROGRESS → DONE`
- Phạm vi: engine adapter UCI local, chơi máy/phân tích, validate PV, giới hạn tài nguyên, benchmark và giấy phép local phi thương mại.
- Kết quả: thêm `EngineAdapter`, `UciEngineAdapter`, `MockEngine`, API analyze/best-move/stop và panel engine trên board. FEN `r/b` được đổi sang `w/b` cho Pikafish; Fairy UCI rank `1–10` được đổi sang ICCS `0–9`. Engine binary/weights để trong `.local-engines/` (gitignore), không bundle source.
- Engine chọn cho local: Pikafish 2026-09-06 (`4c17cee`), UCI. Binary SHA-256 `0D57D64C212E78F96CBA9E5E4F140D8872F8FAA42EA631A27AB6C5DB08509DA3`; `pikafish.nnue` SHA-256 `7D13D73569A9B571BA0EB20CF1596247BC2A42738967E61AFEF6482B231E900E`. Weights không thương mại nếu chưa xin phép; chỉ cấu hình local phi thương mại.
- So sánh cùng FEN, 1000 ms, depth 12, MultiPV 3: các lượt smoke đo Pikafish 428–467 ms và Fairy-Stockfish 14.0.1 XQ 795–911 ms. Chỉ là smoke trên máy hiện tại, không phải benchmark Elo. Bằng chứng license/artifact đầy đủ ở [`docs/ENGINE_LICENSE.md`](../docs/ENGINE_LICENSE.md), quyết định tại ADR-007.
- Log kiểm soát chỉ ghi engine ID/version, thời gian, depth và số PV; không ghi FEN/biến cờ. Chưa thêm cache vì prototype local không có tải phân tích lặp cần tối ưu.

### Exit criteria Phase 2

| Điều kiện | Kết quả thực tế |
| --- | --- |
| MockEngine normal/timeout/hang/crash/invalid PV/cancel | PASS trong `backend/tests/test_engine_service.py`; API FEN/limits/provenance/perspective trong `backend/tests/test_engine_api.py` |
| Engine thật localhost trả best move hợp lệ + MultiPV | PASS cho Pikafish và Fairy trong `backend/tests/test_engine_integration.py`; mỗi engine 2 tests PASS (UCI trực tiếp + API) |
| Orientation score Đỏ/Đen | PASS API tests: 42 cp cho Đỏ khi Đỏ đi; 57 cp cho Đen đổi thành -57 theo Đỏ |
| Stress 3 request, stop, crash restart | PASS cả hai engine: tái dùng cùng PID cho 3 request, `stop` rồi search tiếp, kill process rồi tự restart bằng PID mới |
| License/version/hash binary và weights | PASS; ADR-007 và `docs/ENGINE_LICENSE.md`; artifacts cụ thể và điều kiện local-only ghi rõ |

### Lệnh và kết quả

| Lệnh | Kết quả |
| --- | --- |
| `.\\.venv\\Scripts\\python.exe -m pytest -q` | PASS — 38 passed, 2 engine integration tests skipped do env mặc định không bật; 7 cảnh báo deprecation của Starlette/FastAPI/Python |
| `$env:ENGINE_COMMAND = (Resolve-Path '.local-engines/Pikafish-Windows-x86-64-universal.exe').Path; .\\.venv\\Scripts\\python.exe -m pytest -q -s backend/tests/test_engine_integration.py` | PASS — 2; latest benchmark 455 ms; 3 concurrent, stop và restart PASS |
| `$env:ENGINE_COMMAND = (Resolve-Path '.local-engines/fairy-stockfish-largeboard_x86-64.exe').Path; .\\.venv\\Scripts\\python.exe -m pytest -q -s backend/tests/test_engine_integration.py` | PASS — 2; latest benchmark 795 ms; 3 concurrent, stop và restart PASS |
| Uvicorn với Pikafish tại `127.0.0.1:8765`; `Invoke-RestMethod GET /health` + `POST /v1/engine/analyze` | PASS — HTTP 200; `Pikafish 2026-09-06`, best move `h2e2`, 3 PV, depth 12, 491 ms |
| `npm test` | PASS — 4 frontend tests, gồm phân tích/provenance và máy đi quân Đen |
| `npm run lint` | PASS |
| `npm run typecheck` | PASS |
| `npm run build` | PASS — Vite transform 31 modules; production bundle thành công |

- Local HTTP smoke đã chạy bằng: `$env:ENGINE_COMMAND = (Resolve-Path '.local-engines/Pikafish-Windows-x86-64-universal.exe').Path; .\\.venv\\Scripts\\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8765`; sau đó gọi `Invoke-RestMethod -Uri 'http://127.0.0.1:8765/health'` và `Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8765/v1/engine/analyze' -ContentType 'application/json' -Body '{"fen":"rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR r - - 0 1","time_ms":1000,"depth":12,"multipv":3,"job_id":"http-smoke"}'`. Kết quả: `health=ok`, HTTP 200, Pikafish 2026-09-06, `best_move=h2e2`, 3 PV, depth 12, 491 ms. Server/process đã được dừng sau smoke.
- Frontend test/build cần chạy với quyền cho phép esbuild đọc thư mục cha của workspace; chạy thường trong sandbox báo Access denied.
- Phase 2: `DONE` cho phạm vi local phi thương mại. Chưa hiệu chuẩn Elo; không tuyên bố engine move “tốt nhất” ngoài phân tích do engine trả về. Phiên tới: bắt đầu Phase 3 qua `prompts/PHASE_3.md`; phiên này không triển khai Phase 3.

## Phiên trước — Phase 1

- Thời điểm: 2026-09-26
- Phase: `1 / IN_PROGRESS → DONE`
- Phạm vi: bàn cờ SVG tương tác, rules service/API backend, FEN/ICCS, lịch sử/undo/replay, kiểm thử luật và UI.
- Người/agent: Codex

## Kết quả đã có

- Backend Python là nguồn sự thật cho FEN, nước hợp lệ, áp dụng nước và trạng thái check/checkmate/stalemate. API: `POST /v1/rules/legal-moves`, `POST /v1/rules/apply-move`.
- Frontend có board responsive 9×10, click/touch, chọn đích hợp lệ, bàn phím cơ bản, xoay bàn, nước vừa đi, cảnh báo chiếu, import/copy FEN, lịch sử và tua ván.
- Ván lưu danh sách FEN sau mỗi nước và ICCS; hỗ trợ lùi/tiến, về đầu/cuối, replay nước trong history. Khi nhánh mới được đi từ vị trí cũ, phần history tương lai được thay thế.
- FEN đầu ván được round-trip và có 44 nước mở đầu; đối chiếu danh sách với ví dụ API trong README của `xiangqi.js`. Không dùng dependency này trong runtime.
- Pháo, Mã, Tượng, Sĩ, Tướng, Binh, cung, sông, chiếu, tự chiếu, hết nước, và FEN/API sai đều có fixtures.
- Lặp vị trí lần thứ ba được phát hiện và trả trạng thái `repetition_review_required`; UI dừng ván và yêu cầu trọng tài đánh giá.

## Bằng chứng thực tế

| Lệnh/test | Kết quả | Ghi chú |
| --- | --- | --- |
| `python -m pytest -q` | PASS — 29 tests | Có 4 cảnh báo deprecation từ Starlette/FastAPI trong môi trường Python 3.14; không có test fail. |
| `npm run build` | PASS | TypeScript build và Vite production build; 31 modules. Cần chạy ngoài sandbox mặc định vì esbuild bị chặn đọc thư mục cha của workspace. |
| `npm run lint` | PASS | ESLint sạch. |
| `npm run typecheck` | PASS | `tsc -b --pretty` thành công. |
| `npm test` | PASS — 3 tests | UI hai lượt Đỏ–Đen với mock API, orientation, undo/replay/redo, FEN và bàn phím. |
| Browser manual interaction | Chưa xác nhận | Đã xem render ban đầu; thao tác chuột thực tế chưa được xác nhận qua browser automation. |

## Đối chiếu exit criteria Phase 1

- Fixture luật quân/cung/sông/chiếu/hóa giải/chiếu bí/hết nước/FEN: đạt trong `backend/tests/test_xiangqi_rules.py` và `backend/tests/test_rules_api.py`.
- Orientation, replay và ván hai lượt cùng bàn: đạt trong `frontend/src/App.test.tsx`; backend từ chối nước sai được kiểm tra trong API tests.
- Lặp: lần lặp thứ ba có API/UI cảnh báo và test. Chưa phân xử chiếu liên tục hay đuổi liên tục; không tuyên bố luật thi đấu đầy đủ.
- Phase 1 được đánh dấu DONE cho phạm vi prototype đã nêu và các giới hạn còn lại được ghi thành issue theo dõi. Cần chốt ruleset thi đấu trước khi dùng cho giải đấu/đối kháng có kết quả chính thức.

## Giới hạn và việc theo dõi

- `xiangqi.js` chỉ được spike/đối chiếu; giấy phép BSD-2-Clause và API trong upstream README/package đã được xem xét. Repository tự ghi nhận FEN validation còn cần cải thiện; không dùng nó làm trọng tài runtime. Nguồn: [README/API](https://github.com/lengyanyu258/xiangqi.js), [package metadata](https://github.com/lengyanyu258/xiangqi.js/blob/dev/package.json).
- Bộ luật hiện tại chưa phân xử perpetual check/chase theo AXF/luật giải đấu; chưa xử lý giới hạn nước không bắt quân. Đây là **issue mở** trước khi tuyên bố tuân thủ luật thi đấu: xác định ruleset/version, thêm fixtures chiếu/đuổi và lặp theo bên gây lặp, sau đó cập nhật ADR-006.
- Không có engine, opening knowledge hay AI tutor trong Phase 1.
- Nguồn luật để rà soát tiếp: [Asian Xiangqi Federation rules (HTML)](https://www.asianxiangqi.org/English/AXFrulesEng.htm), [bản PDF](https://www.asianxiangqi.org/English/AXF_rules_Eng.pdf).

## Trạng thái và bước kế tiếp

- Phase 1: `DONE` cho prototype với giới hạn trên.
- Tại thời điểm handoff Phase 1, Phase 2 ở `PENDING`, đủ cổng bắt đầu; chưa triển khai trong phiên đó.
