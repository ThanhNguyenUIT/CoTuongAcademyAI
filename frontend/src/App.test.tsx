import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import App from './App';

const startingFen = 'rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR r - - 0 1';
const movedFen = 'rnbakabnr/9/1c5c1/p1p1p1p1p/9/4P4/P1P3P1P/1C5C1/9/RNBAKABNR b - - 0 1';
const movedTwiceFen = 'rnbakabnr/9/1c5c1/p1p3p1p/4p4/4P4/P1P3P1P/1C5C1/9/RNBAKABNR r - - 0 2';

afterEach(() => {
  cleanup();
  localStorage.clear();
  vi.unstubAllGlobals();
});

describe('board practice page', () => {
  it('uses server-validated moves and records a replayable move', async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const path = String(input);
      if (path.startsWith('/v1/learning/games/') && !path.split('?')[0].endsWith('/rematch')) return Promise.resolve(new Response(null, { status: 404 }));
      if (init?.method === 'POST' && path.endsWith('/v1/learning/games')) {
        const game = JSON.parse(String(init.body)) as { game_id: string; moves_iccs: string[] };
        return Promise.resolve(new Response(JSON.stringify({ game_id: game.game_id, ply_count: game.moves_iccs.length, saved: true }), { status: 200, headers: { 'Content-Type': 'application/json' } }));
      }
      if (path.includes('/v1/learning/games/') && path.split('?')[0].endsWith('/rematch')) {
        return Promise.resolve(new Response(JSON.stringify({ game_id: 'game', engine_status: 'available', candidates: [{ game_id: 'game', ply: 1, fen: startingFen, move_iccs: 'e3e4', reason: 'Mốc mẫu.', engine_marked: true, evidence: 'Mock engine depth 6' }] }), { status: 200, headers: { 'Content-Type': 'application/json' } }));
      }
      const isApply = path.endsWith('/apply-move');
      const body = JSON.parse(String(init?.body ?? '{}')) as { fen: string; move?: string };
      return Promise.resolve(new Response(JSON.stringify({
        fen: isApply ? (body.fen === movedFen ? movedTwiceFen : movedFen) : body.fen,
        moves: isApply ? (body.fen === movedFen ? ['e3e4'] : ['e6e5']) : (body.fen === movedFen ? ['e6e5'] : ['e3e4']),
        status: 'active',
        in_check: false,
        checked_general: null,
      }), { status: 200, headers: { 'Content-Type': 'application/json' } }));
    });
    vi.stubGlobal('fetch', fetchMock);

    render(<App />);
    await screen.findByText('Lượt Đỏ');
    fireEvent.click(screen.getByRole('button', { name: /^e3,/ }));
    fireEvent.click(screen.getByRole('button', { name: /^e4,/ }));

    expect(await screen.findByText('Lượt Đen')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /^e6,/ }));
    fireEvent.click(screen.getByRole('button', { name: /^e5,/ }));
    expect(await screen.findByText('Lượt Đỏ')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '1. e3 → e4' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '1… e6 → e5' })).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith('/v1/rules/apply-move', expect.objectContaining({ method: 'POST' }));
    expect(await screen.findByText('2/2 ply đã lưu')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Tìm thời điểm để đánh lại' }));
    fireEvent.click(await screen.findByRole('button', { name: 'Đánh lại từ đây' }));
    expect(await screen.findByText(/Đánh lại từ trước nước 1: e3e4/)).toBeInTheDocument();
  });

  it('supports orientation, undo, replay, redo, and FEN round-trip controls', async () => {
    vi.stubGlobal('fetch', vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const path = String(input);
      if (path.startsWith('/v1/learning/games/') && !path.split('?')[0].endsWith('/rematch')) return Promise.resolve(new Response(null, { status: 404 }));
      const isApply = path.endsWith('/apply-move');
      const body = JSON.parse(String(init?.body ?? '{}')) as { fen: string; move?: string };
      return Promise.resolve(new Response(JSON.stringify({
        fen: isApply ? (body.fen === movedFen ? movedTwiceFen : movedFen) : body.fen,
        moves: isApply ? (body.fen === movedFen ? ['e3e4'] : ['e6e5']) : (body.fen === movedFen ? ['e6e5'] : ['e3e4']),
        status: 'active', in_check: false, checked_general: null,
      }), { status: 200, headers: { 'Content-Type': 'application/json' } }));
    }));
    const { container } = render(<App />);
    await screen.findByText('Lượt Đỏ');
    const board = container.querySelector('.xiangqi-board');
    expect(board?.querySelector('[role="button"]')?.getAttribute('aria-label')).toMatch(/^a9,/);

    fireEvent.click(screen.getByRole('button', { name: '⟳ Xoay bàn' }));
    expect(board?.querySelector('[role="button"]')?.getAttribute('aria-label')).toMatch(/^i0,/);
    fireEvent.click(screen.getByRole('button', { name: '⟳ Xoay bàn' }));
    fireEvent.click(screen.getByRole('button', { name: /^e3,/ }));
    fireEvent.click(screen.getByRole('button', { name: /^e4,/ }));
    await screen.findByText('Lượt Đen');
    fireEvent.click(screen.getByRole('button', { name: /^e6,/ }));
    fireEvent.click(screen.getByRole('button', { name: /^e5,/ }));
    await screen.findByText('Lượt Đỏ');

    fireEvent.click(screen.getByRole('button', { name: 'Lùi một nước' }));
    expect(await screen.findByText('Lượt Đen')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Đến cuối ván' }));
    expect(await screen.findByText('Lượt Đỏ')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: '1… e6 → e5' }));
    expect(screen.getByRole('button', { name: '1… e6 → e5' })).toHaveAttribute('aria-current', 'step');
    expect(screen.getByLabelText('FEN ICCS')).toHaveValue(movedTwiceFen);
  });

  it('restores a saved game on refresh and appends the next move under the same game ID', async () => {
    const learnerId = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';
    const gameId = '11111111-1111-4111-8111-111111111111';
    localStorage.setItem('xiangqi-learning-learner-id', learnerId);
    localStorage.setItem('xiangqi-learning-board-game-id', gameId);
    const nextFen = movedTwiceFen.replace('P1P3P1P', 'P1P1P1P1P');
    let savedMoves: string[] = [];
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const path = String(input);
      const route = path.split('?')[0];
      if (route === `/v1/learning/games/${gameId}`) {
        return Promise.resolve(new Response(JSON.stringify({
          learner_id: learnerId, game_id: gameId, starting_fen: startingFen,
          moves_iccs: ['e3e4', 'e6e5'], positions_fens: [startingFen, movedFen, movedTwiceFen],
          ended: false, updated_at: '2026-09-28T00:00:00Z',
        }), { status: 200, headers: { 'Content-Type': 'application/json' } }));
      }
      if (init?.method === 'POST' && route === '/v1/learning/games') {
        const payload = JSON.parse(String(init.body)) as { moves_iccs: string[] };
        savedMoves = payload.moves_iccs;
        return Promise.resolve(new Response(JSON.stringify({ game_id: gameId, ply_count: savedMoves.length, saved: true }), { status: 200, headers: { 'Content-Type': 'application/json' } }));
      }
      const isApply = route.endsWith('/apply-move');
      const body = JSON.parse(String(init?.body ?? '{}')) as { fen?: string };
      const responseFen = isApply ? nextFen : (body.fen ?? startingFen);
      const moves = isApply ? [] : (responseFen === movedTwiceFen ? ['a3a4'] : ['e3e4']);
      return Promise.resolve(new Response(JSON.stringify({ fen: responseFen, moves, status: 'active', in_check: false, checked_general: null }), { status: 200, headers: { 'Content-Type': 'application/json' } }));
    });
    vi.stubGlobal('fetch', fetchMock);

    render(<App />);
    expect(await screen.findByRole('button', { name: '1. e3 → e4' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '1… e6 → e5' })).toBeInTheDocument();
    expect(await screen.findByText('2/2 ply đã lưu')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /^a3,/ }));
    fireEvent.click(screen.getByRole('button', { name: /^a4,/ }));
    expect(await screen.findByText('3/3 ply đã lưu')).toBeInTheDocument();
    expect(savedMoves).toEqual(['e3e4', 'e6e5', 'a3a4']);
  });

  it('selects a piece from the keyboard and announces legal destinations', async () => {
    vi.stubGlobal('fetch', vi.fn((input: RequestInfo | URL) => String(input).startsWith('/v1/learning/games/')
      ? Promise.resolve(new Response(null, { status: 404 }))
      : Promise.resolve(new Response(JSON.stringify({
      fen: startingFen, moves: ['e3e4'], status: 'active', in_check: false, checked_general: null,
    }), { status: 200, headers: { 'Content-Type': 'application/json' } }))));
    render(<App />);
    await screen.findByText('Lượt Đỏ');
    fireEvent.keyDown(screen.getByRole('button', { name: /^e3,/ }), { key: 'Enter' });

    expect(screen.getByRole('button', { name: /e3.*đang chọn/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /e4.*nước đi hợp lệ/ })).toBeInTheDocument();
  });

  it('shows engine provenance and lets the engine make Black’s move', async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const path = String(input);
      if (path.startsWith('/v1/learning/games/') && !path.split('?')[0].endsWith('/rematch')) return Promise.resolve(new Response(null, { status: 404 }));
      const body = JSON.parse(String(init?.body ?? '{}')) as { fen: string; move?: string };
      if (path.endsWith('/engine/analyze') || path.endsWith('/engine/best-move')) {
        const move = body.fen === movedFen ? 'e6e5' : 'a3a4';
        return Promise.resolve(new Response(JSON.stringify({
          engine_id: 'Fairy-Stockfish', engine_version: '14.0.1', protocol: 'uci',
          position_fen: body.fen, limits: { time_ms: 1000, depth: 12 }, score_perspective: 'side_to_move',
          elapsed_ms: 250, is_complete: true, best_move: move,
          lines: [{ multipv: 1, depth: 12, score_cp_side_to_move: 42, mate_in_side_to_move: null, score_cp_red: 42, mate_in_red: null, pv: [move] }],
        }), { status: 200, headers: { 'Content-Type': 'application/json' } }));
      }
      const isApply = path.endsWith('/apply-move');
      const nextFen = isApply ? (body.fen === startingFen ? movedFen : movedTwiceFen) : body.fen;
      const moves = nextFen === movedFen ? ['e6e5'] : ['e3e4'];
      return Promise.resolve(new Response(JSON.stringify({ fen: nextFen, moves, status: 'active', in_check: false, checked_general: null }), { status: 200, headers: { 'Content-Type': 'application/json' } }));
    });
    vi.stubGlobal('fetch', fetchMock);
    render(<App />);
    await screen.findByText('Lượt Đỏ');

    fireEvent.click(screen.getByRole('button', { name: 'Phân tích · 1 giây' }));
    expect(await screen.findByText(/Fairy-Stockfish · 14.0.1 · UCI/)).toBeInTheDocument();
    expect(screen.getByText('+0.42')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /^e3,/ }));
    fireEvent.click(screen.getByRole('button', { name: /^e4,/ }));
    await screen.findByText('Lượt Đen');
    fireEvent.click(screen.getByRole('button', { name: 'Đen đi bằng máy' }));
    expect(await screen.findByText('Lượt Đỏ')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '1… e6 → e5' })).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith('/v1/engine/best-move', expect.objectContaining({ method: 'POST' }));
  });
});
