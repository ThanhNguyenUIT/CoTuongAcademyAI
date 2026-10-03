# Nguồn tham khảo được kiểm tra khi soạn bộ hồ sơ

Ngày kiểm tra: **2026-09-26**. Những nguồn dưới đây dùng để thiết kế **kế hoạch**, không khẳng định dự án đã code hoặc tích hợp bất kỳ thư viện nào. Codex phải kiểm tra lại version/license của artifact thực tế khi triển khai.

1. **Codex project instructions / AGENTS.md:** https://github.com/openai/codex/blob/main/docs/agents_md.md — tài liệu Codex dẫn đến hướng dẫn AGENTS.md chính thức. `AGENTS.md` ở thư mục dự án là nơi đặt quy tắc lâu dài; các Markdown khác phải được prompt yêu cầu đọc rõ ràng.
2. **Pikafish engine:** https://github.com/official-pikafish/Pikafish — engine Xiangqi UCI, mã nguồn GPLv3.
3. **Pikafish networks:** https://github.com/official-pikafish/Networks — điều kiện NNUE chính thức không thương mại nếu chưa có phép; thông tin về một số mạng Xiangqi Fairy-Stockfish CC0.
4. **Fairy-Stockfish:** https://github.com/fairy-stockfish/Fairy-Stockfish — Xiangqi, UCI/UCCI, GPLv3.
5. **Fairy-Stockfish WASM:** https://github.com/fairy-stockfish/fairy-stockfish.wasm — hướng triển khai client-side offline trong tương lai.
6. **xiangqi.js:** https://github.com/lengyanyu258/xiangqi.js — ứng viên luật di chuyển cờ tướng JS, chưa xác nhận đáp ứng toàn bộ luật giải đấu.

## Những điểm phải thẩm định thêm

- Bộ luật thi đấu cờ tướng cụ thể được sử dụng (giải quyết chiếu lặp và đuổi lặp, hòa cờ); xin đối chiếu một ruleset chính thức kèm test case.
- Nguồn dữ liệu khai cuộc và quyền biên soạn/phân phối. Mục tiêu có thư viện lớn không đồng nghĩa quyền tự động sao chép sách, video, cơ sở dữ liệu.
- Những ví dụ chiến thuật trong giáo trình cần engine proof hoặc biên tập viên có chuyên môn; không đưa ví dụ ngẫu nhiên vào tài liệu sản phẩm.
