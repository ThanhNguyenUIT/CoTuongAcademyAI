import { useEffect, useMemo, useRef, useState, type KeyboardEvent } from 'react';
import { requestApplyMove, requestEngineAnalysis, requestEngineMove, requestLegalMoves, type EngineAnalysis, type RulesResponse } from './rulesApi';
import { currentBoardGameId, getRematchCandidates, getSavedLearningGame, localLearnerId, newLearningId, rotateBoardGameId, saveLearningGame, type RematchCandidate } from './learningApi';

const INITIAL_FEN = 'rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR r - - 0 1';
const pieceGlyph: Record<string, string> = { r: '車', n: '馬', b: '象', a: '士', k: '將', c: '砲', p: '卒', R: '俥', N: '傌', B: '相', A: '仕', K: '帥', C: '炮', P: '兵' };
const pieceName: Record<string, string> = { r: 'Xe đen', n: 'Mã đen', b: 'Tượng đen', a: 'Sĩ đen', k: 'Tướng đen', c: 'Pháo đen', p: 'Tốt đen', R: 'Xe đỏ', N: 'Mã đỏ', B: 'Tượng đỏ', A: 'Sĩ đỏ', K: 'Tướng đỏ', C: 'Pháo đỏ', P: 'Binh đỏ' };
const files = 'abcdefghi';
type Game = { fens: string[]; moves: string[] };

function readBoard(fen: string): (string | null)[][] {
  const placement = fen.split(' ')[0];
  return placement.split('/').map((row) => {
    const cells: (string | null)[] = [];
    for (const char of row) {
      if (/\d/.test(char)) cells.push(...Array.from({ length: Number(char) }, () => null));
      else cells.push(char);
    }
    return cells;
  });
}

function currentTurn(fen: string): string {
  return fen.split(' ')[1] === 'r' ? 'Đỏ' : 'Đen';
}

function moveLabel(move: string, index: number): string {
  const from = `${move[0]}${move[1]}`;
  const to = `${move[2]}${move[3]}`;
  return `${Math.floor(index / 2) + 1}${index % 2 === 0 ? '.' : '…'} ${from} → ${to}`;
}

function explainStatus(result: RulesResponse): string {
  if (result.status === 'checkmate') return 'Chiếu bí · ván cờ kết thúc';
  if (result.status === 'stalemate') return 'Hết nước hợp lệ · ván cờ kết thúc';
  if (result.status === 'repetition_review_required') return 'Thế cờ lặp lại · cần trọng tài xác định chiếu/đuổi';
  if (result.in_check) return `Đang chiếu ${result.checked_general ?? ''}`;
  return `Lượt ${currentTurn(result.fen)}`;
}

export default function Board() {
  const [game, setGame] = useState<Game>({ fens: [INITIAL_FEN], moves: [] });
  const [cursor, setCursor] = useState(0);
  const [position, setPosition] = useState<RulesResponse | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [rotated, setRotated] = useState(false);
  const [message, setMessage] = useState('Đang tải luật cờ…');
  const [fenInput, setFenInput] = useState(INITIAL_FEN);
  const [busy, setBusy] = useState(false);
  const [engineBusy, setEngineBusy] = useState(false);
  const [analysis, setAnalysis] = useState<EngineAnalysis | null>(null);
  const [learnerId] = useState(localLearnerId);
  const [gameId, setGameId] = useState(currentBoardGameId);
  const [rematchCandidates, setRematchCandidates] = useState<RematchCandidate[]>([]);
  const [rematchMessage, setRematchMessage] = useState('');
  const [rematchBusy, setRematchBusy] = useState(false);
  const [savedPly, setSavedPly] = useState(0);
  const [gameReady, setGameReady] = useState(false);
  const [gameLoadError, setGameLoadError] = useState('');
  const [restoreRevision, setRestoreRevision] = useState(0);
  const gameSaveRevision = useRef(0);

  const fen = game.fens[cursor];
  const board = useMemo(() => readBoard(fen), [fen]);
  const possible = useMemo(() => new Set(position?.moves.filter((move) => move.startsWith(selected ?? '\u0000')) ?? []), [position, selected]);
  const lastMove = game.moves[cursor - 1] ?? null;
  const terminal = position?.status === 'checkmate' || position?.status === 'stalemate' || position?.status === 'repetition_review_required';

  useEffect(() => {
    let active = true;
    setGameReady(false);
    setGameLoadError('');
    setPosition(null);
    getSavedLearningGame(learnerId, gameId).then((saved) => {
      if (!active) return;
      if (saved) {
        if (saved.positions_fens.length !== saved.moves_iccs.length + 1 || saved.positions_fens[0] !== saved.starting_fen) {
          throw new Error('Lịch sử ván local không nhất quán; giữ nguyên bản lưu và thử tải lại.');
        }
        setGame({ fens: saved.positions_fens, moves: saved.moves_iccs });
        setCursor(saved.moves_iccs.length);
        setFenInput(saved.positions_fens.at(-1) ?? saved.starting_fen);
        setSavedPly(saved.moves_iccs.length);
      } else {
        setGame({ fens: [INITIAL_FEN], moves: [] });
        setCursor(0);
        setFenInput(INITIAL_FEN);
        setSavedPly(0);
      }
      setGameReady(true);
    }).catch((error: unknown) => {
      if (!active) return;
      const detail = error instanceof Error ? error.message : 'Không khôi phục được ván local.';
      setGameLoadError(detail);
      setMessage(`Không khôi phục được ván đã lưu; bàn cờ đang khóa để giữ nguyên dữ liệu. ${detail}`);
    });
    return () => { active = false; };
  }, [gameId, learnerId, restoreRevision]);

  useEffect(() => {
    if (!gameReady) return;
    let mounted = true;
    requestLegalMoves(fen).then((result) => {
      if (mounted) {
        setPosition(result);
        setMessage(explainStatus(result));
      }
    }).catch((error: unknown) => {
      if (mounted) setMessage(error instanceof Error ? error.message : 'Không tải được luật cờ.');
    });
    return () => { mounted = false; };
  }, [fen, gameReady]);

  async function playMove(move: string) {
    if (!gameReady || busy) return;
    setBusy(true);
    setSelected(null);
    try {
      const result = await requestApplyMove(fen, move, game.fens.slice(0, cursor + 1));
      const nextGame = { fens: [...game.fens.slice(0, cursor + 1), result.fen], moves: [...game.moves.slice(0, cursor), move] };
      setGame(nextGame);
      setRematchCandidates([]);
      setRematchMessage('');
      const saveRevision = ++gameSaveRevision.current;
      void saveLearningGame({ learner_id: learnerId, game_id: gameId, starting_fen: nextGame.fens[0], moves_iccs: nextGame.moves, ended: ['checkmate', 'stalemate', 'repetition_review_required'].includes(result.status) })
        .then((saved) => { if (saveRevision === gameSaveRevision.current) setSavedPly(saved.ply_count); })
        .catch(() => setRematchMessage('Không lưu được ván local; thử lại khi backend hoạt động.'));
      setCursor(nextGame.fens.length - 1);
      setPosition(result);
      setAnalysis(null);
      setFenInput(result.fen);
      setMessage(explainStatus(result));
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Nước đi không hợp lệ.');
    } finally {
      setBusy(false);
    }
  }

  function selectSquare(file: number, rank: number) {
    if (!gameReady || !position || terminal || busy || engineBusy) return;
    const square = `${files[file]}${rank}`;
    if (selected) {
      const move = `${selected}${square}`;
      if (possible.has(move)) {
        void playMove(move);
        return;
      }
    }
    const piece = board[9 - rank][file];
    const isTurnPiece = piece !== null && (piece === piece.toUpperCase() ? 'r' : 'b') === fen.split(' ')[1];
    setSelected(isTurnPiece ? square : null);
  }

  function handleSquareKey(event: KeyboardEvent<SVGGElement>) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      selectSquare(Number(event.currentTarget.dataset.file), Number(event.currentTarget.dataset.rank));
      return;
    }
    if (!['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(event.key)) return;
    event.preventDefault();
    const target = event.currentTarget;
    let file = Number(target.dataset.file);
    let rank = Number(target.dataset.rank);
    if (event.key === 'ArrowUp') rank = Math.min(9, rank + 1);
    if (event.key === 'ArrowDown') rank = Math.max(0, rank - 1);
    if (event.key === 'ArrowLeft') file = Math.max(0, file - 1);
    if (event.key === 'ArrowRight') file = Math.min(8, file + 1);
    target.closest('svg')?.querySelector<SVGGElement>(`[data-file="${file}"][data-rank="${rank}"]`)?.focus();
  }

  async function importFen() {
    if (!gameReady || busy) return;
    setBusy(true);
    try {
      const result = await requestLegalMoves(fenInput.trim());
      const nextId = newLearningId();
      await saveLearningGame({ learner_id: learnerId, game_id: nextId, starting_fen: result.fen, moves_iccs: [], ended: false });
      rotateBoardGameId(nextId);
      setGameId(nextId);
      setGameReady(false);
      gameSaveRevision.current += 1;
      setSavedPly(0);
      setGame({ fens: [result.fen], moves: [] });
      setCursor(0);
      setPosition(result);
      setSelected(null);
      setMessage(explainStatus(result));
    } catch (error) {
      setMessage(error instanceof Error ? `Không tải/lưu được vị trí: ${error.message}` : 'Không tải/lưu được vị trí.');
    } finally {
      setBusy(false);
    }
  }

  async function findRematchMoments() {
    if (!game.moves.length || rematchBusy) return;
    setRematchBusy(true);
    setRematchMessage('Đang kiểm tra tối đa ba thời điểm bằng engine local…');
    try {
      const result = await getRematchCandidates(learnerId, gameId);
      const candidates = Array.isArray(result.candidates) ? result.candidates : [];
      setRematchCandidates(candidates);
      setRematchMessage(candidates.length ? 'Chọn một thời điểm để đánh lại.' : result.engine_status === 'unavailable' ? 'Engine chưa sẵn sàng; hiện chưa thể đánh dấu mốc cần ôn.' : 'Engine chưa đánh dấu sai lệch từ 1,00 tốt trở lên ở các mốc mẫu; không tự gán đây là sai lầm.');
    } catch (error) {
      setRematchMessage(error instanceof Error ? error.message : 'Không tạo được danh sách đánh lại.');
    } finally {
      setRematchBusy(false);
    }
  }

  async function startRematch(candidate: RematchCandidate) {
    if (!gameReady || busy) return;
    setBusy(true);
    try {
      const result = await requestLegalMoves(candidate.fen);
      const nextId = newLearningId();
      await saveLearningGame({ learner_id: learnerId, game_id: nextId, starting_fen: result.fen, moves_iccs: [], ended: false });
      rotateBoardGameId(nextId);
      setGameId(nextId);
      setGameReady(false);
      gameSaveRevision.current += 1;
      setSavedPly(0);
      setGame({ fens: [result.fen], moves: [] });
      setCursor(0);
      setPosition(result);
      setSelected(null);
      setAnalysis(null);
      setFenInput(result.fen);
      setRematchCandidates([]);
      setRematchMessage(`Đánh lại từ trước nước ${candidate.ply}: ${candidate.move_iccs}. ${candidate.evidence}`);
    } catch (error) {
      setRematchMessage(error instanceof Error ? error.message : 'Vị trí đánh lại không hợp lệ.');
    } finally {
      setBusy(false);
    }
  }

  async function copyFen() {
    try {
      await navigator.clipboard.writeText(fen);
      setMessage('Đã sao chép FEN.');
    } catch {
      setMessage('Không thể truy cập clipboard; hãy chọn và sao chép FEN.');
    }
  }

  async function analyzePosition() {
    const requestedFen = fen;
    setEngineBusy(true);
    setAnalysis(null);
    try {
      const result = await requestEngineAnalysis(requestedFen);
      if (result.position_fen === requestedFen) setAnalysis(result);
      setMessage(`Phân tích xong · ${result.engine_id} ${result.engine_version} · ${result.elapsed_ms} ms`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Không phân tích được vị trí.');
    } finally {
      setEngineBusy(false);
    }
  }

  async function playEngineMove() {
    if (fen.split(' ')[1] !== 'b' || engineBusy || busy || terminal) return;
    const requestedFen = fen;
    setEngineBusy(true);
    try {
      const result = await requestEngineMove(requestedFen);
      if (result.position_fen !== requestedFen || !position?.moves.includes(result.best_move)) {
        throw new Error('Engine trả về nước không hợp lệ cho vị trí hiện tại.');
      }
      await playMove(result.best_move);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Engine không tìm được nước đi.');
    } finally {
      setEngineBusy(false);
    }
  }

  const currentAnalysis = analysis?.position_fen === fen ? analysis : null;

  return (
    <section className="board-shell" aria-label="Bàn cờ và điều khiển ván cờ">
      <div className="board-heading">
        <div>
          <p className="eyebrow">BÀN CỜ · LUẬT ĐƯỢC XÁC NHẬN BỞI BACKEND</p>
          <h2>Bàn tập luyện</h2>
        </div>
        <button className="quiet-button" onClick={() => setRotated((value) => !value)} type="button">⟳ Xoay bàn</button>
      </div>
      <div className="board-layout">
        <div className="board-area">
          <div className="board-status" role="status" aria-live="polite">{message}</div>
          {gameLoadError && <div className="board-status" role="alert">{gameLoadError} <button className="quiet-button" type="button" onClick={() => setRestoreRevision((value) => value + 1)}>Thử tải lại ván đã lưu</button></div>}
          <svg className="xiangqi-board" viewBox="0 0 450 500" role="grid" aria-label={`Bàn cờ tướng, lượt ${currentTurn(fen)}`}>
            <rect x="20" y="15" width="410" height="465" rx="8" className="board-frame" />
            {[0, 1, 2, 3, 4, 5, 6, 7, 8].map((file) => {
              const x = 45 + file * 45;
              return <g key={`file-${file}`}><line x1={x} y1="30" x2={x} y2="218" className="board-line" /><line x1={x} y1="265" x2={x} y2="453" className="board-line" /></g>;
            })}
            {Array.from({ length: 10 }, (_, row) => <line key={`rank-${row}`} x1="45" y1={30 + row * 47} x2="405" y2={30 + row * 47} className="board-line" />)}
            <path d="M180 30 L270 124 M270 30 L180 124 M180 359 L270 453 M270 359 L180 453" className="board-line" />
            <text x="225" y="246" textAnchor="middle" className="river-label">河界</text>
            {Array.from({ length: 10 }, (_, row) => Array.from({ length: 9 }, (_, col) => {
              const file = rotated ? 8 - col : col;
              const rank = rotated ? row : 9 - row;
              const x = 45 + col * 45;
              const y = 30 + row * 47;
              const piece = board[9 - rank][file];
              const square = `${files[file]}${rank}`;
              const selectedSquare = selected === square;
              const legalTarget = possible.has(`${selected}${square}`);
              const lastSquare = lastMove?.slice(0, 2) === square || lastMove?.slice(2, 4) === square;
              const checked = position?.checked_general === square;
              return (
                <g key={square} role="gridcell">
                  <g role="button" tabIndex={0} data-file={file} data-rank={rank} aria-label={`${files[file]}${rank}${piece ? `, ${pieceName[piece]}` : ', ô trống'}${selectedSquare ? ', đang chọn' : ''}${legalTarget ? ', nước đi hợp lệ' : ''}${checked ? ', đang bị chiếu' : ''}`}
                    onClick={() => selectSquare(file, rank)} onKeyDown={handleSquareKey}>
                    <rect x={x - 21} y={y - 21} width="42" height="42" rx="21" className={`square-hit${lastSquare ? ' square-last' : ''}${selectedSquare ? ' square-selected' : ''}`} />
                    {legalTarget && <circle cx={x} cy={y} r={piece ? 19 : 5} className={piece ? 'capture-ring' : 'legal-dot'} />}
                    {checked && <circle cx={x} cy={y} r="21" className="check-ring" />}
                    {piece && <><circle cx={x} cy={y} r="17" className={`piece-disc ${piece === piece.toUpperCase() ? 'piece-red' : 'piece-black'}`} /><text x={x} y={y + 7} textAnchor="middle" className={`piece-glyph ${piece === piece.toUpperCase() ? 'glyph-red' : 'glyph-black'}`}>{pieceGlyph[piece]}</text></>}
                  </g>
                </g>
              );
            }))}
            {Array.from({ length: 9 }, (_, col) => <text key={`label-file-${col}`} x={45 + col * 45} y="472" textAnchor="middle" className="coordinate-label">{files[rotated ? 8 - col : col]}</text>)}
          </svg>
        </div>

        <aside className="board-tools" aria-label="Điều khiển ván cờ">
          <div className="turn-card"><span className="eyebrow">ĐANG CHƠI</span><strong>{terminal ? 'Ván đã dừng' : `${currentTurn(fen)} đi`}</strong><span>{position ? `${position.moves.length} nước hợp lệ` : 'Đang kiểm tra…'}</span></div>
          <div className="control-row">
            <button className="control-button" onClick={() => { setCursor(0); setSelected(null); }} disabled={cursor === 0} type="button" aria-label="Về đầu ván">|◀</button>
            <button className="control-button" onClick={() => { setCursor((value) => Math.max(0, value - 1)); setSelected(null); }} disabled={cursor === 0} type="button" aria-label="Lùi một nước">◀</button>
            <button className="control-button" onClick={() => { setCursor((value) => Math.min(game.fens.length - 1, value + 1)); setSelected(null); }} disabled={cursor >= game.fens.length - 1} type="button" aria-label="Tiến một nước">▶</button>
            <button className="control-button" onClick={() => { setCursor(game.fens.length - 1); setSelected(null); }} disabled={cursor >= game.fens.length - 1} type="button" aria-label="Đến cuối ván">▶|</button>
          </div>
          <div className="moves-card">
            <div className="card-title"><h3>Lịch sử nước đi</h3><span>{cursor}/{game.moves.length}</span></div>
            {game.moves.length === 0 ? <p className="empty-moves">Các nước đi sẽ hiện ở đây.</p> : <ol className="move-list">{game.moves.map((move, index) => <li key={`${index}-${move}`}><button type="button" aria-current={cursor === index + 1 ? 'step' : undefined} onClick={() => { setCursor(index + 1); setSelected(null); }}>{moveLabel(move, index)}</button></li>)}</ol>}
          </div>
          <div className="rematch-card" aria-label="Đánh lại thời điểm quan trọng">
            <div className="card-title"><h3>Đánh lại ván</h3><span>{savedPly}/{game.moves.length} ply đã lưu</span></div>
            <p className="engine-provenance">Engine lấy mẫu tối đa ba nước; chỉ đưa vào danh sách khi đánh giá giảm ít nhất 1,00 tốt cho bên vừa đi. Đây là heuristic, không phải nhãn sai lầm chuyên môn.</p>
            <button className="quiet-button" type="button" onClick={() => void findRematchMoments()} disabled={!game.moves.length || savedPly < game.moves.length || rematchBusy || engineBusy}>{rematchBusy ? 'Đang phân tích…' : 'Tìm thời điểm để đánh lại'}</button>
            {rematchMessage && <p role="status" className="engine-provenance">{rematchMessage}</p>}
            {rematchCandidates.length > 0 && <ol className="rematch-list">{rematchCandidates.map((candidate) => <li key={`${candidate.ply}-${candidate.move_iccs}`}>
              <span>Nước {candidate.ply}: {candidate.move_iccs} · {candidate.reason}</span>
              <button className="quiet-button" type="button" onClick={() => void startRematch(candidate)}>Đánh lại từ đây</button>
            </li>)}</ol>}
          </div>
          <div className="engine-card" aria-label="Phân tích engine">
            <div className="card-title"><h3>Engine local</h3><span>{engineBusy ? 'Đang tính…' : currentAnalysis ? `${currentAnalysis.elapsed_ms} ms` : 'Chưa chạy'}</span></div>
            <div className="control-row">
              <button className="quiet-button" onClick={() => void analyzePosition()} disabled={engineBusy || busy || terminal} type="button">Phân tích · 1 giây</button>
              <button className="quiet-button" onClick={() => void playEngineMove()} disabled={engineBusy || busy || terminal || fen.split(' ')[1] !== 'b'} type="button">Đen đi bằng máy</button>
            </div>
            {currentAnalysis ? <>
              <p className="engine-provenance">{currentAnalysis.engine_id} · {currentAnalysis.engine_version} · {currentAnalysis.protocol.toUpperCase()} · depth {currentAnalysis.lines[0]?.depth}</p>
              <ol className="engine-lines">{currentAnalysis.lines.map((line) => <li key={`${line.multipv}-${line.pv.join('-')}`}>
                <span>#{line.multipv}</span>
                <strong>{line.mate_in_red !== null ? `mate ${line.mate_in_red}` : line.score_cp_red !== null ? `${line.score_cp_red > 0 ? '+' : ''}${(line.score_cp_red / 100).toFixed(2)}` : '—'}</strong>
                <span>{line.pv.join(' ')}</span>
              </li>)}</ol>
              <p className="engine-provenance">Điểm theo phía Đỏ · centipawn · biến đã kiểm tra luật.</p>
            </> : <p className="engine-provenance">Cần cấu hình binary UCI local qua <code>ENGINE_COMMAND</code>. Chưa có điểm Elo được hiệu chuẩn.</p>}
          </div>
          <div className="fen-card">
            <label className="card-title" htmlFor="fen-import">FEN <span>ICCS</span></label>
            <textarea id="fen-import" rows={3} value={fenInput} onChange={(event) => setFenInput(event.target.value)} spellCheck={false} />
            <div className="control-row"><button className="quiet-button" onClick={() => void importFen()} disabled={!gameReady || busy} type="button">Tải vị trí</button><button className="quiet-button" onClick={() => void copyFen()} type="button">Sao chép</button></div>
          </div>
          <p className="rules-note">Luật lặp chiếu/đuổi chưa tự phân xử. Khi phát hiện vị trí lặp lần thứ ba, ván dừng để trọng tài đánh giá.</p>
        </aside>
      </div>
    </section>
  );
}
