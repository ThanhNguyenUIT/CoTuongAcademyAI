"""Repeatable, local CPU/latency profile for the personal-learning hot paths.

This profiles synchronous service calls on the current machine. It does not
start a server, invoke an external engine/provider, or include learner text in
output. Use the same Python environment and iteration count before/after edits.
"""

from __future__ import annotations

import argparse
import random
import statistics
import sys
import tempfile
import time
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.knowledge.service import get_opening
from backend.app.learning.schemas import GameSaveRequest
from backend.app.learning.service import LearningService
from backend.app.learning.store import LearningStore
from backend.app.main import get_legal_moves, post_apply_move
from backend.app.rules import xiangqi
from backend.app.rules.schemas import ApplyMoveRequest, PositionRequest


START_FEN = xiangqi.STARTING_FEN


def summarize(label: str, samples: list[float]) -> None:
    ordered = sorted(samples)
    p95 = ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))]
    print(f"{label}: median={statistics.median(samples):.3f}ms p95={p95:.3f}ms max={max(samples):.3f}ms n={len(samples)}")


def measure(label: str, action, iterations: int) -> None:
    for _ in range(min(3, iterations)):
        action()
    samples = []
    for _ in range(iterations):
        started = time.perf_counter()
        action()
        samples.append((time.perf_counter() - started) * 1000)
    summarize(label, samples)


def legal_game(length: int) -> list[str]:
    """Make a deterministic legal playout long enough for save-path profiling."""
    for seed in range(100):
        rng = random.Random(seed)
        position = xiangqi.Position.from_fen(START_FEN)
        moves: list[str] = []
        while len(moves) < length:
            choices = xiangqi.legal_moves(position)
            if not choices:
                break
            move = rng.choice(choices)
            position = xiangqi.apply_move(position, move)
            moves.append(move)
        if len(moves) == length:
            return moves
    raise RuntimeError(f"Could not generate a legal {length}-ply profiling game.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=25)
    args = parser.parse_args()
    if args.iterations < 5 or args.iterations > 500:
        parser.error("--iterations must be between 5 and 500")

    move_request = PositionRequest(fen=START_FEN)
    apply_request = ApplyMoveRequest(fen=START_FEN, move="b2e2", history_fens=[START_FEN])
    measure("rules.legal_moves", lambda: get_legal_moves(move_request), args.iterations)
    measure("rules.apply_move", lambda: post_apply_move(apply_request), args.iterations)
    measure("knowledge.get_opening", lambda: get_opening("cannon-vs-screen-horse", include_experimental=True), args.iterations)

    learner_id = uuid4()
    game_id = uuid4()
    moves = legal_game(300)
    with tempfile.TemporaryDirectory(prefix="xiangqi-profile-") as temp_dir:
        service = LearningService(store=LearningStore(Path(temp_dir) / "profile.sqlite3"), app_env="local")
        for plies in (1, 20, 100, 300):
            new_game_samples = []
            for iteration in range(args.iterations + 3):
                request = GameSaveRequest(
                    learner_id=learner_id, game_id=uuid4(), starting_fen=START_FEN,
                    moves_iccs=moves[:plies], ended=False,
                )
                started = time.perf_counter()
                service.save_game(request)
                elapsed_ms = (time.perf_counter() - started) * 1000
                if iteration >= 3:
                    new_game_samples.append(elapsed_ms)
            summarize(f"learning.new_game.{plies}_plies", new_game_samples)

            samples = []
            for iteration in range(args.iterations + 3):
                game_id = uuid4()
                prefix = GameSaveRequest(
                    learner_id=learner_id, game_id=game_id, starting_fen=START_FEN,
                    moves_iccs=moves[: max(0, plies - 1)], ended=False,
                )
                service.save_game(prefix)
                append = prefix.model_copy(update={"moves_iccs": moves[:plies]})
                started = time.perf_counter()
                service.save_game(append)
                elapsed_ms = (time.perf_counter() - started) * 1000
                if iteration >= 3:
                    samples.append(elapsed_ms)
            summarize(f"learning.append_to_{plies}_plies", samples)


if __name__ == "__main__":
    main()
