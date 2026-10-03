import pytest

from backend.app.rules.xiangqi import (
    STARTING_FEN,
    IllegalMoveError,
    Position,
    PositionError,
    apply_move,
    in_check,
    legal_moves,
    repetition_count,
    status,
)


def test_starting_fen_round_trips_and_has_expected_legal_move_count() -> None:
    position = Position.from_fen(STARTING_FEN)

    assert position.to_fen() == STARTING_FEN
    assert len(legal_moves(position)) == 44
    assert "a3a4" in legal_moves(position)
    assert "e3e4" in legal_moves(position)


@pytest.mark.parametrize(
    "fen",
    [
        "9/9/9 r - - 0 1",  # rank count
        "10/9/9/9/9/9/9/9/9/4K4 r - - 0 1",  # unsupported run length
        "8/9/9/9/9/9/9/9/9/4K3k r - - 0 1",  # rank width
        "9/9/9/9/9/9/9/9/9/4K4 x - - 0 1",  # active color
        "9/9/9/9/9/9/9/9/9/4K3k r K - 0 1",  # castling unsupported
        "9/9/9/9/9/9/9/9/9/4K3k r - - -1 1",  # invalid counter
        "9/9/9/9/9/9/9/9/9/4K3k r - - 0 0",  # invalid fullmove
        "9/9/9/9/9/9/9/9/9/4K4 r - - 0 1",  # missing black general
        "9/9/9/9/9/9/9/9/9/3K4k r - - 0 1",  # general outside palace
        "4k4/9/9/9/9/9/9/9/9/A3K4 r - - 0 1",  # advisor outside palace
        "4k4/9/9/9/2B6/9/9/9/9/4K4 r - - 0 1",  # elephant across river
    ],
)
def test_invalid_fen_is_rejected(fen: str) -> None:
    with pytest.raises(PositionError):
        Position.from_fen(fen)


def test_cannon_capture_requires_exactly_one_screen() -> None:
    blocked = Position.from_fen("4k4/9/9/9/r8/9/9/9/9/C2K5 r - - 0 1")
    screened = Position.from_fen("4k4/9/9/9/r8/9/9/C8/9/C2K5 r - - 0 1")

    assert "a0a5" not in legal_moves(blocked)
    assert "a0a5" in legal_moves(screened)


def test_horse_leg_blocks_move() -> None:
    position = Position.from_fen("4k4/9/9/9/9/9/9/4N4/4P4/4K4 r - - 0 1")

    assert "e1d3" not in legal_moves(position)
    assert "e1f3" not in legal_moves(position)


def test_elephant_eye_and_river_limit() -> None:
    blocked_eye = Position.from_fen("4k4/9/9/9/9/9/9/4P4/9/2B1K4 r - - 0 1")
    river_edge = Position.from_fen("4k4/9/9/9/9/2B6/9/9/9/4K4 r - - 0 1")

    assert "e0c2" not in legal_moves(blocked_eye)
    assert "c4a6" not in legal_moves(river_edge)


def test_advisor_and_general_stay_in_palace() -> None:
    position = Position.from_fen("4k4/9/9/9/9/9/9/9/3A5/3K5 r - - 0 1")

    moves = legal_moves(position)
    assert all(move[2] in "def" and move[3] in "012" for move in moves)


def test_soldier_gains_sideways_moves_after_crossing_river() -> None:
    before_crossing = Position.from_fen("4k4/9/9/9/9/4P4/9/9/9/3K5 r - - 0 1")
    after_crossing = Position.from_fen("4k4/9/9/4P4/9/9/9/9/9/3K5 r - - 0 1")

    assert "e4d4" not in legal_moves(before_crossing)
    assert "e4e5" in legal_moves(before_crossing)
    assert "e6d6" in legal_moves(after_crossing)


def test_move_cannot_expose_generals_to_facing_file() -> None:
    position = Position.from_fen("4k4/9/9/9/9/9/9/9/4R4/4K4 r - - 0 1")

    assert not in_check(position)
    assert "e1d1" not in legal_moves(position)


def test_check_must_be_evaded_and_fen_counters_advance() -> None:
    checked = Position.from_fen("4k4/9/9/9/9/4r4/9/9/9/4K4 r - - 0 1")
    start = Position.from_fen(STARTING_FEN)
    moved = apply_move(start, "e3e4")

    assert in_check(checked)
    assert all(move.startswith("e0") for move in legal_moves(checked))
    assert moved.turn == "b"
    assert moved.halfmove == 0
    assert moved.fullmove == 1


def test_no_legal_moves_is_a_loss_by_checkmate_or_stalemate() -> None:
    checkmate = Position.from_fen("4k4/4R4/9/9/9/9/9/9/3K5/3RRR3 b - - 0 1")

    assert legal_moves(checkmate) == []
    assert status(checkmate) == "checkmate"
    stalemate = Position.from_fen("3aca3/1Cnrk4/b3r4/2p1n4/2b6/9/9/9/4C4/ppppcK3 b - - 0 1")
    assert legal_moves(stalemate) == []
    assert status(stalemate) == "stalemate"


def test_repetition_is_flagged_for_review_not_adjudicated() -> None:
    start = Position.from_fen(STARTING_FEN)
    fens = [start.to_fen()]
    current = start
    for move in ["h0g2", "h9g7", "g2h0", "g7h9"] * 2:
        current = apply_move(current, move)
        fens.append(current.to_fen())

    assert repetition_count(fens[:-1], current.to_fen()) == 3


def test_halfmove_and_fullmove_counters_follow_iccs_turns() -> None:
    position = Position.from_fen(STARTING_FEN)
    after_red = apply_move(position, "h0g2")
    after_black = apply_move(after_red, "h9g7")

    assert after_red.to_fen().endswith(" b - - 1 1")
    assert after_black.to_fen().endswith(" r - - 2 2")


def test_illegal_move_is_rejected() -> None:
    with pytest.raises(IllegalMoveError):
        apply_move(Position.from_fen(STARTING_FEN), "a0a9")
