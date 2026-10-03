import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import OpeningLab from './OpeningLab';

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe('Opening Lab', () => {
  it('navigates a transposition and supports wrong answer, counterplay, retry, and a reasoned choice', async () => {
    const keys = ['root r', 'one b', 'two r', 'three b', 'final r'];
    const fen = [
      'rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR r - - 0 1',
      'rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/4C2C1/9/RNBAKABNR b - - 0 1',
      'rnbakabnr/6n2/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/4C2C1/9/RNBAKABNR r - - 1 2',
      'rnbakabnr/6n2/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/2N1C2C1/9/RNBAKABNR b - - 2 2',
      'r1bakabnr/6n2/1cn4c1/p1p1p1p1p/9/9/P1P1P1P1P/2N1C2C1/9/RNBAKABNR r - - 3 3',
    ];
    const detail = {
      opening: {
        opening_id: 'cannon-vs-screen-horse', name_vi: 'Pháo đầu đối Bình phong mã',
        description: 'Nội dung thử nghiệm.', version: '0.1.0-experimental', review_status: 'experimental',
        source_refs: [{ id: 'source', title: 'Nguồn khai cuộc', url: 'https://example.com', note: 'Tham khảo' }],
        lines: [
          { id: 'line-a', label: 'Mã phải trước', moves_iccs: ['b2e2', 'h9g7', 'b0c2', 'b9c7'], review_status: 'experimental', version: '0.1' },
          { id: 'line-b', label: 'Mã trái trước', moves_iccs: ['b2e2', 'b9c7', 'b0c2', 'h9g7'], review_status: 'experimental', version: '0.1' },
        ],
        annotations: [],
        lesson: {
          id: 'lesson', title: 'Nhìn cấu trúc', outcomes: ['Dự đoán nước'], content_version: '0.1', review_status: 'experimental',
          steps: [{ id: 'step', title: 'Dự đoán', body: 'Chọn phản ứng và nói lý do.', moves_iccs: [], annotation_ids: [] }],
          exercises: [{
            id: 'exercise', fen: fen[1], question: 'Chọn phản ứng minh họa hợp lệ.', skill_tags: ['predict-response'],
            rubric: ['Nêu một lý do.'],
            hint_ladder: ['Quan sát trung tâm.', 'Tìm một Mã.', 'Thử h9g7.'],
            choices: [
              { id: 'wrong', text: 'a9a8 · Xe tiến một ô', move_iccs: 'a9a8', correct: false, feedback: 'Nước hợp lệ nhưng không trúng mục tiêu câu hỏi.', counterplay: 'Thử phản ứng Đỏ b0c2 để kiểm tra.', counterplay_moves_iccs: ['b0c2'] },
              { id: 'right', text: 'h9g7 · phát triển Mã', move_iccs: 'h9g7', correct: true, feedback: 'Nước minh họa hợp lệ.', counterplay: 'Nêu điều muốn kiểm tra tiếp.', counterplay_moves_iccs: ['b0c2'] },
            ],
          }],
        },
      },
      graph: {
        root_position_key: keys[0],
        positions: keys.map((position_key, index) => ({
          position_key, fen: fen[index], side_to_move: index % 2 ? 'b' : 'r',
          incoming_lines: index === 4 ? ['line-a', 'line-b'] : ['line-a'],
        })),
        edges: [
          { from_position_key: keys[0], move_iccs: 'b2e2', to_position_key: keys[1], line_ids: ['line-a', 'line-b'] },
          { from_position_key: keys[1], move_iccs: 'h9g7', to_position_key: keys[2], line_ids: ['line-a'] },
          { from_position_key: keys[2], move_iccs: 'b0c2', to_position_key: keys[3], line_ids: ['line-a'] },
          { from_position_key: keys[3], move_iccs: 'b9c7', to_position_key: keys[4], line_ids: ['line-a'] },
          { from_position_key: keys[1], move_iccs: 'b9c7', to_position_key: keys[2], line_ids: ['line-b'] },
          { from_position_key: keys[2], move_iccs: 'b0c2', to_position_key: keys[3], line_ids: ['line-b'] },
          { from_position_key: keys[3], move_iccs: 'h9g7', to_position_key: keys[4], line_ids: ['line-b'] },
        ],
      },
    };
    let attemptCount = 0;
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      if (String(input).includes('/v1/learning/progress/')) {
        const progress = { learner_id: 'local-user', total_attempts: attemptCount, due_reviews: attemptCount ? 1 : 0, updated_at: null,
          skills: attemptCount ? [{ skill_id: 'read_threats', name: 'Đọc mối đe dọa', attempts: attemptCount, focus_aligned: 0, sample_size: attemptCount, focus_rate: 0, repeated_errors: 1, next_review_at: '2026-09-28T12:00:00Z' }] : [] };
        return Promise.resolve(new Response(JSON.stringify(progress), { status: 200, headers: { 'Content-Type': 'application/json' } }));
      }
      if (String(input).includes('/v1/learning/next/')) {
        return Promise.resolve(new Response(JSON.stringify({ lesson_id: 'lesson', exercise_id: 'exercise', exercise_version: '0.1', question: 'Chọn phản ứng.', skill_ids: ['read_threats'], reason: 'Bài tiếp theo.', scheduled_for: null, include_experimental: true }), { status: 200, headers: { 'Content-Type': 'application/json' } }));
      }
      if (init?.method === 'POST' && String(input).includes('/v1/learning/attempts')) {
        attemptCount += 1;
        const request = JSON.parse(String(init.body)) as { selected_move: string; exercise_id: string; attempt_id: string };
        const aligned = request.selected_move === 'h9g7';
        return Promise.resolve(new Response(JSON.stringify({ attempt_id: request.attempt_id, game_id: 'game', lesson_id: 'lesson', exercise_id: request.exercise_id, exercise_version: '0.1', skill_ids: ['read_threats'], duplicate: false, outcome: { status: aligned ? 'focus_aligned' : 'needs_practice', focus_aligned: aligned, reason_submitted: true, points: aligned ? 2 : 1, points_possible: 2, rubric_self_checks: [], review_due_at: '2026-09-28T12:00:00Z', repeated_error_count: 0 } }), { status: 200, headers: { 'Content-Type': 'application/json' } }));
      }
      if (init?.method === 'POST' && String(input).includes('/v1/tutor/hint')) {
        const request = JSON.parse(String(init.body)) as { hint_level: number };
        return Promise.resolve(new Response(JSON.stringify({
          trace_id: 'trace-' + request.hint_level, context_digest: 'digest', hint_level: request.hint_level,
          question: 'Hãy quan sát trước khi chọn.',
          claims: [{ text: 'So sánh mục tiêu phát triển quân.', evidence_refs: ['rules:test'] }],
          candidate_moves: request.hint_level === 3 ? ['h9g7'] : [],
          evidence: [{ ref: 'rules:test', kind: 'rules', review_status: 'reviewed', moves_iccs: [] }],
          uncertainty: 'Chưa có bằng chứng cho nước tốt nhất.', provider: 'fallback', fallback: true, engine_status: 'unavailable',
        }), { status: 200, headers: { 'Content-Type': 'application/json' } }));
      }
      return Promise.resolve(new Response(JSON.stringify(detail), {
        status: 200, headers: { 'Content-Type': 'application/json' },
      }));
    });
    vi.stubGlobal('fetch', fetchMock);

    const { container } = render(<OpeningLab />);
    fireEvent.click(await screen.findByRole('button', { name: /Tiến một nước/ }));
    fireEvent.click(screen.getByRole('button', { name: /Tiến một nước/ }));
    fireEvent.click(screen.getByRole('button', { name: /Tiến một nước/ }));
    fireEvent.click(screen.getByRole('button', { name: /Tiến một nước/ }));
    expect(await screen.findByText(/Chuyển vị: vị trí này xuất hiện trong 2 đường/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /a9a8/ }));
    expect(screen.queryByText('Phản công / kiểm tra tiếp:')).not.toBeInTheDocument();
    fireEvent.change(screen.getAllByLabelText('Lý do của bạn')[0], { target: { value: 'Muốn so sánh phát triển quân.' } });
    fireEvent.click(screen.getAllByRole('button', { name: 'Kiểm tra câu trả lời' })[0]);
    expect(fetchMock).toHaveBeenCalledWith('/v1/learning/attempts', expect.objectContaining({ method: 'POST' }));
    await screen.findByText(/Đã lưu/);
    expect(container.querySelector('.attempt-receipt')).toHaveTextContent(/1\s*\/\s*2/);
    expect(await screen.findByText(/1 lượt trả lời · 1 bài đến lịch ôn/)).toBeInTheDocument();
    expect(screen.getByText('Đọc mối đe dọa')).toBeInTheDocument();
    expect(screen.getByText('Phản công / kiểm tra tiếp:')).toBeInTheDocument();
    expect(screen.getByText(/Thử phản ứng Đỏ b0c2/)).toBeInTheDocument();
    expect(container.querySelector('.counterplay-line')?.textContent).toContain('Chuỗi nước đã kiểm tra luật: a9a8 b0c2');
    fireEvent.click(screen.getByRole('button', { name: 'Thử lại' }));
    fireEvent.click(screen.getAllByRole('button', { name: /h9g7/ })[1]);
    fireEvent.change(screen.getAllByLabelText('Lý do của bạn')[0], { target: { value: 'Phát triển Mã để tham gia thế trận.' } });
    fireEvent.click(screen.getAllByRole('button', { name: 'Kiểm tra câu trả lời' })[0]);
    await screen.findByText(/Đã lưu/);
    expect(container.querySelector('.attempt-receipt')).toHaveTextContent(/2\s*\/\s*2/);
    expect(screen.getByText('Nước minh họa hợp lệ')).toBeInTheDocument();
    expect(screen.getByText(/Nêu điều muốn kiểm tra tiếp/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Gia sư · gợi ý 1' }));
    expect(await screen.findByText('Gia sư · tầng 1 · chế độ dự phòng')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Gia sư · gợi ý 2' }));
    expect(await screen.findByText('Gia sư · tầng 2 · chế độ dự phòng')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Gia sư · gợi ý 3' }));
    expect(await screen.findByText('Gia sư · tầng 3 · chế độ dự phòng')).toBeInTheDocument();
    expect(container.textContent).toContain('Biến được xác minh: h9g7');
  });
});
