export type RulesStatus = 'active' | 'check' | 'checkmate' | 'stalemate' | 'repetition_review_required';

export interface RulesResponse {
  fen: string;
  moves: string[];
  status: RulesStatus;
  in_check: boolean;
  checked_general: string | null;
  repetition_count?: number | null;
}

export interface EngineLine {
  multipv: number;
  depth: number;
  score_cp_side_to_move: number | null;
  mate_in_side_to_move: number | null;
  score_cp_red: number | null;
  mate_in_red: number | null;
  pv: string[];
}

export interface EngineAnalysis {
  engine_id: string;
  engine_version: string;
  protocol: string;
  position_fen: string;
  limits: { time_ms: number; depth: number };
  score_perspective: 'side_to_move';
  elapsed_ms: number;
  is_complete: boolean;
  best_move: string;
  lines: EngineLine[];
}

async function postRules<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const payload = await response.json() as T & { detail?: { message?: string } };
  if (!response.ok) {
    throw new Error(payload.detail?.message ?? `Rules request failed (${response.status}).`);
  }
  return payload;
}

export function requestLegalMoves(fen: string): Promise<RulesResponse> {
  return postRules('/v1/rules/legal-moves', { fen });
}

export function requestApplyMove(fen: string, move: string, historyFens: string[]): Promise<RulesResponse> {
  return postRules('/v1/rules/apply-move', { fen, move, history_fens: historyFens });
}

export async function requestEngineAnalysis(fen: string, signal?: AbortSignal): Promise<EngineAnalysis> {
  const response = await fetch('/v1/engine/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ fen, time_ms: 1000, depth: 12, multipv: 3 }),
    signal,
  });
  const payload = await response.json() as EngineAnalysis & { detail?: { message?: string } };
  if (!response.ok) throw new Error(payload.detail?.message ?? `Engine request failed (${response.status}).`);
  return payload;
}

export async function requestEngineMove(fen: string): Promise<EngineAnalysis> {
  const response = await fetch('/v1/engine/best-move', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ fen, time_ms: 1000, depth: 12, multipv: 1 }),
  });
  const payload = await response.json() as EngineAnalysis & { detail?: { message?: string } };
  if (!response.ok) throw new Error(payload.detail?.message ?? `Engine request failed (${response.status}).`);
  return payload;
}
