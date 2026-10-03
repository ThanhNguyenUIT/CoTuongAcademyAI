"""Core Xiangqi move legality and FEN handling.

Coordinates are ICCS internally (a0 is Red's bottom-left). FEN rows are
stored top to bottom. Repetition/chase adjudication is intentionally exposed
as requiring review; this module does not claim tournament-rule adjudication.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

FILES = "abcdefghi"
PIECES = set("rnbakcpRNBAKCP")
STARTING_FEN = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR r - - 0 1"


class PositionError(ValueError):
    """A malformed or structurally invalid Xiangqi FEN position."""


class IllegalMoveError(ValueError):
    """A move is not legal in the supplied position."""


@dataclass(frozen=True)
class Move:
    from_file: int
    from_rank: int
    to_file: int
    to_rank: int

    @property
    def iccs(self) -> str:
        return f"{FILES[self.from_file]}{self.from_rank}{FILES[self.to_file]}{self.to_rank}"


@dataclass
class Position:
    board: list[list[str | None]]  # FEN orientation: row 0 is Black's back rank.
    turn: str
    halfmove: int
    fullmove: int

    @classmethod
    def from_fen(cls, fen: str) -> "Position":
        fields = fen.strip().split()
        if len(fields) != 6:
            raise PositionError("FEN must have six fields.")
        placement, turn, castling, en_passant, halfmove, fullmove = fields
        rows = placement.split("/")
        if len(rows) != 10:
            raise PositionError("FEN must describe exactly 10 ranks.")
        board: list[list[str | None]] = []
        for row in rows:
            expanded: list[str | None] = []
            for char in row:
                if char.isdigit():
                    if char not in "123456789":
                        raise PositionError("Empty-square counts must be 1 through 9.")
                    expanded.extend([None] * int(char))
                elif char in PIECES:
                    expanded.append(char)
                else:
                    raise PositionError("FEN contains an unsupported piece symbol.")
            if len(expanded) != 9:
                raise PositionError("Each FEN rank must contain exactly 9 files.")
            board.append(expanded)
        if turn not in {"r", "b"}:
            raise PositionError("Active color must be 'r' or 'b'.")
        if castling != "-" or en_passant != "-":
            raise PositionError("Xiangqi FEN castling and en-passant fields must be '-'.")
        if not re.fullmatch(r"\d+", halfmove) or not re.fullmatch(r"[1-9]\d*", fullmove):
            raise PositionError("FEN move counters must be non-negative integers; fullmove must be positive.")
        if sum(piece == "K" for row in board for piece in row) != 1:
            raise PositionError("FEN must contain exactly one Red general.")
        if sum(piece == "k" for row in board for piece in row) != 1:
            raise PositionError("FEN must contain exactly one Black general.")
        red_general = next(( (x, 9 - y) for y, row in enumerate(board) for x, piece in enumerate(row) if piece == "K"), None)
        black_general = next(( (x, 9 - y) for y, row in enumerate(board) for x, piece in enumerate(row) if piece == "k"), None)
        if not _palace("r", *red_general) or not _palace("b", *black_general):
            raise PositionError("Each general must be inside its own palace.")
        for y, row in enumerate(board):
            for x, piece in enumerate(row):
                if piece is None:
                    continue
                side, rank = _side(piece), 9 - y
                if piece.lower() == "a" and not _palace(side, x, rank):
                    raise PositionError("Advisors must be inside their own palace.")
                if piece.lower() == "b" and ((side == "r" and rank > 4) or (side == "b" and rank < 5)):
                    raise PositionError("Elephants cannot cross the river.")
        return cls(board, turn, int(halfmove), int(fullmove))

    def to_fen(self) -> str:
        ranks: list[str] = []
        for row in self.board:
            out = ""
            empty = 0
            for piece in row:
                if piece is None:
                    empty += 1
                else:
                    if empty:
                        out += str(empty)
                        empty = 0
                    out += piece
            if empty:
                out += str(empty)
            ranks.append(out)
        return f"{'/'.join(ranks)} {self.turn} - - {self.halfmove} {self.fullmove}"

    def piece_at(self, file: int, rank: int) -> str | None:
        return self.board[9 - rank][file]

    def set_piece(self, file: int, rank: int, piece: str | None) -> None:
        self.board[9 - rank][file] = piece

    def locate(self, piece: str) -> tuple[int, int] | None:
        for y, row in enumerate(self.board):
            for x, item in enumerate(row):
                if item == piece:
                    return x, 9 - y
        return None

    def copy(self) -> "Position":
        return Position([row[:] for row in self.board], self.turn, self.halfmove, self.fullmove)


@dataclass(frozen=True)
class PositionAnalysis:
    legal_moves: tuple[str, ...]
    status: str
    in_check: bool
    checked_general: str | None


def _side(piece: str) -> str:
    return "r" if piece.isupper() else "b"


def _inside(file: int, rank: int) -> bool:
    return 0 <= file < 9 and 0 <= rank < 10


def _palace(side: str, file: int, rank: int) -> bool:
    return 3 <= file <= 5 and (0 <= rank <= 2 if side == "r" else 7 <= rank <= 9)


def _path_count(position: Position, a: tuple[int, int], b: tuple[int, int]) -> int:
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    if dx and dy or (not dx and not dy):
        return -1
    step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
    step_y = 0 if dy == 0 else (1 if dy > 0 else -1)
    x, y, count = ax + step_x, ay + step_y, 0
    while (x, y) != (bx, by):
        count += position.piece_at(x, y) is not None
        x += step_x
        y += step_y
    return count


def _pseudo_targets(position: Position, x: int, y: int, *, attacks_only: bool = False) -> Iterable[tuple[int, int]]:
    piece = position.piece_at(x, y)
    if piece is None:
        return
    side = _side(piece)
    kind = piece.lower()

    def available(tx: int, ty: int) -> bool:
        if not _inside(tx, ty):
            return False
        target = position.piece_at(tx, ty)
        return target is None or _side(target) != side

    if kind == "r":
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            tx, ty = x + dx, y + dy
            while _inside(tx, ty):
                target = position.piece_at(tx, ty)
                if target is None:
                    if not attacks_only:
                        yield tx, ty
                else:
                    if _side(target) != side:
                        yield tx, ty
                    break
                tx += dx
                ty += dy
    elif kind == "c":
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            tx, ty, screen = x + dx, y + dy, False
            while _inside(tx, ty):
                target = position.piece_at(tx, ty)
                if not screen:
                    if target is None:
                        if not attacks_only:
                            yield tx, ty
                    else:
                        screen = True
                elif target is not None:
                    if _side(target) != side:
                        yield tx, ty
                    break
                tx += dx
                ty += dy
    elif kind == "n":
        for dx, dy, leg_x, leg_y in (
            (1, 2, 0, 1), (-1, 2, 0, 1), (1, -2, 0, -1), (-1, -2, 0, -1),
            (2, 1, 1, 0), (2, -1, 1, 0), (-2, 1, -1, 0), (-2, -1, -1, 0),
        ):
            tx, ty = x + dx, y + dy
            if _inside(tx, ty) and position.piece_at(x + leg_x, y + leg_y) is None and available(tx, ty):
                yield tx, ty
    elif kind == "b":
        for dx, dy in ((2, 2), (-2, 2), (2, -2), (-2, -2)):
            tx, ty = x + dx, y + dy
            if not _inside(tx, ty) or position.piece_at(x + dx // 2, y + dy // 2) is not None:
                continue
            if (side == "r" and ty > 4) or (side == "b" and ty < 5):
                continue
            if available(tx, ty):
                yield tx, ty
    elif kind == "a":
        for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            tx, ty = x + dx, y + dy
            if _inside(tx, ty) and _palace(side, tx, ty) and available(tx, ty):
                yield tx, ty
    elif kind == "k":
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            tx, ty = x + dx, y + dy
            if _inside(tx, ty) and _palace(side, tx, ty) and available(tx, ty):
                yield tx, ty
        enemy_general = "k" if side == "r" else "K"
        enemy = position.locate(enemy_general)
        if enemy and enemy[0] == x and _path_count(position, (x, y), enemy) == 0:
            yield enemy
    elif kind == "p":
        forward = 1 if side == "r" else -1
        for dx, dy in ((0, forward), (-1, 0), (1, 0)):
            tx, ty = x + dx, y + dy
            crossed = y >= 5 if side == "r" else y <= 4
            if dx and not crossed:
                continue
            if _inside(tx, ty) and available(tx, ty):
                yield tx, ty


def _attacked(position: Position, file: int, rank: int, by_side: str) -> bool:
    target = position.piece_at(file, rank)
    for y, row in enumerate(position.board):
        for x, piece in enumerate(row):
            if piece is None or _side(piece) != by_side:
                continue
            kind = piece.lower()
            if kind == "c":
                if (x == file or y == 9 - rank) and _path_count(position, (x, 9 - y), (file, rank)) == 1:
                    if target is not None and _side(target) != by_side:
                        return True
            elif (file, rank) in _pseudo_targets(position, x, 9 - y, attacks_only=True):
                return True
    return False


def in_check(position: Position, side: str | None = None) -> bool:
    side = side or position.turn
    general = position.locate("K" if side == "r" else "k")
    if general is None:
        return True
    enemy = "b" if side == "r" else "r"
    return _attacked(position, general[0], general[1], enemy)


def legal_moves(position: Position, side: str | None = None) -> list[str]:
    side = side or position.turn
    moves: list[str] = []
    for y, row in enumerate(position.board):
        for x, piece in enumerate(row):
            if piece is None or _side(piece) != side:
                continue
            rank = 9 - y
            for tx, ty in _pseudo_targets(position, x, rank):
                target = position.piece_at(tx, ty)
                if target is not None and target.lower() == "k":
                    continue
                candidate = position.copy()
                candidate.set_piece(tx, ty, piece)
                candidate.set_piece(x, rank, None)
                if not in_check(candidate, side):
                    moves.append(Move(x, rank, tx, ty).iccs)
    return moves


def checked_general(position: Position) -> str | None:
    if not in_check(position):
        return None
    general = position.locate("K" if position.turn == "r" else "k")
    return f"{FILES[general[0]]}{general[1]}" if general else None


def status(position: Position) -> str:
    return analyze_position(position).status


def analyze_position(position: Position) -> PositionAnalysis:
    """Compute response fields from one legal-move and one current-check pass."""
    moves = tuple(legal_moves(position))
    checked = in_check(position)
    if moves:
        state = "check" if checked else "active"
    else:
        state = "checkmate" if checked else "stalemate"
    general = position.locate("K" if position.turn == "r" else "k") if checked else None
    checked_square = f"{FILES[general[0]]}{general[1]}" if general else None
    return PositionAnalysis(moves, state, checked, checked_square)


def apply_move(position: Position, iccs: str) -> Position:
    if not re.fullmatch(r"[a-i][0-9][a-i][0-9]", iccs):
        raise IllegalMoveError("Move must use ICCS coordinates such as a0a1.")
    if iccs not in legal_moves(position):
        raise IllegalMoveError("Move is not legal in this position.")
    fx, fr, tx, tr = FILES.index(iccs[0]), int(iccs[1]), FILES.index(iccs[2]), int(iccs[3])
    piece = position.piece_at(fx, fr)
    target = position.piece_at(tx, tr)
    result = position.copy()
    result.set_piece(fx, fr, None)
    result.set_piece(tx, tr, piece)
    result.halfmove = 0 if target is not None or piece.lower() == "p" else result.halfmove + 1
    if position.turn == "b":
        result.fullmove += 1
    result.turn = "b" if position.turn == "r" else "r"
    return result


def repetition_count(fens: list[str], current_fen: str) -> int:
    """Count identical board+turn states (excluding non-positional FEN counters)."""
    target = " ".join(Position.from_fen(current_fen).to_fen().split()[:2])
    count = 0
    for fen in [*fens, current_fen]:
        candidate = Position.from_fen(fen)
        if " ".join(candidate.to_fen().split()[:2]) == target:
            count += 1
    return count
