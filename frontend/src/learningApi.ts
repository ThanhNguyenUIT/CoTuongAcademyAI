export type LearningProgress = {
  learner_id: string;
  total_attempts: number;
  due_reviews: number;
  updated_at: string | null;
  skills: Array<{
    skill_id: string; name: string; attempts: number; focus_aligned: number;
    sample_size: number; focus_rate: number | null; repeated_errors: number; next_review_at: string | null;
  }>;
};

export type ExerciseRecommendation = {
  lesson_id: string; exercise_id: string; exercise_version: string; question: string;
  skill_ids: string[]; reason: string; scheduled_for: string | null; include_experimental: boolean;
};

export type AttemptReceipt = {
  attempt_id: string; game_id: string; lesson_id: string; exercise_id: string;
  exercise_version: string; skill_ids: string[]; duplicate: boolean;
  outcome: {
    status: 'focus_aligned' | 'needs_practice'; focus_aligned: boolean; reason_submitted: boolean;
    points: number; points_possible: number; rubric_self_checks: string[];
    review_due_at: string; repeated_error_count: number;
  };
};

export type RematchCandidate = { game_id: string; ply: number; fen: string; move_iccs: string; reason: string; engine_marked: boolean; evidence: string };
export type SavedGame = { learner_id: string; game_id: string; starting_fen: string; moves_iccs: string[]; positions_fens: string[]; ended: boolean; updated_at: string };

const LEARNER_KEY = 'xiangqi-learning-learner-id';
const BOARD_GAME_KEY = 'xiangqi-learning-board-game-id';
let gameSaveQueue: Promise<unknown> = Promise.resolve();

function newId(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') return crypto.randomUUID();
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (letter) => {
    const value = Math.random() * 16 | 0;
    return (letter === 'x' ? value : (value & 0x3 | 0x8)).toString(16);
  });
}

export function localLearnerId(): string {
  let value = localStorage.getItem(LEARNER_KEY);
  if (!value) { value = newId(); localStorage.setItem(LEARNER_KEY, value); }
  return value;
}

export function newLearningId(): string { return newId(); }

export function currentBoardGameId(): string {
  let value = localStorage.getItem(BOARD_GAME_KEY);
  if (!value) { value = newId(); localStorage.setItem(BOARD_GAME_KEY, value); }
  return value;
}

export function rotateBoardGameId(nextValue = newId()): string {
  const value = nextValue;
  localStorage.setItem(BOARD_GAME_KEY, value);
  return value;
}

async function jsonRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);
  const value = await response.json() as T & { detail?: { message?: string } };
  if (!response.ok) throw new Error(value.detail?.message ?? `Learning request failed (${response.status}).`);
  return value;
}

export function getLearningProgress(learnerId: string): Promise<LearningProgress> {
  return jsonRequest(`/v1/learning/progress/${encodeURIComponent(learnerId)}`);
}

export function getNextExercise(learnerId: string, includeExperimental: boolean): Promise<ExerciseRecommendation> {
  return jsonRequest(`/v1/learning/next/${encodeURIComponent(learnerId)}?include_experimental=${includeExperimental}`);
}

export function submitLearningAttempt(payload: {
  learner_id: string; attempt_id: string; game_id: string; lesson_id: string; exercise_id: string;
  exercise_version: string; selected_move: string; learner_reason: string; hint_level: number;
  rubric_self_checks: string[]; include_experimental: boolean;
}): Promise<AttemptReceipt> {
  return jsonRequest('/v1/learning/attempts', {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
  });
}

export function saveLearningGame(payload: { learner_id: string; game_id: string; starting_fen: string; moves_iccs: string[]; ended: boolean }): Promise<{ game_id: string; ply_count: number }> {
  const pending = gameSaveQueue.then(() => jsonRequest<{ game_id: string; ply_count: number }>('/v1/learning/games', {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
  }));
  gameSaveQueue = pending.catch(() => undefined);
  return pending;
}

export async function getSavedLearningGame(learnerId: string, gameId: string): Promise<SavedGame | null> {
  const response = await fetch(`/v1/learning/games/${encodeURIComponent(gameId)}?learner_id=${encodeURIComponent(learnerId)}`);
  if (response.status === 404) return null;
  const value = await response.json() as SavedGame & { detail?: { message?: string } };
  if (!response.ok) throw new Error(value.detail?.message ?? `Could not restore game (${response.status}).`);
  return value;
}

export function getRematchCandidates(learnerId: string, gameId: string): Promise<{ game_id: string; candidates: RematchCandidate[]; engine_status: 'available' | 'unavailable' }> {
  return jsonRequest(`/v1/learning/games/${encodeURIComponent(gameId)}/rematch?learner_id=${encodeURIComponent(learnerId)}`);
}

export async function deleteLearningProgress(learnerId: string): Promise<void> {
  await jsonRequest(`/v1/learning/progress/${encodeURIComponent(learnerId)}`, { method: 'DELETE' });
  localStorage.removeItem(LEARNER_KEY);
}
