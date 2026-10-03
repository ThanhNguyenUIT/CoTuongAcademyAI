"""Replaceable, bounded Xiangqi engine interface and UCI subprocess adapter."""

from __future__ import annotations

import asyncio
import logging
import os
import re
import shlex
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from backend.app.rules import xiangqi

logger = logging.getLogger(__name__)


class EngineError(RuntimeError):
    """An engine could not complete a valid request."""


@dataclass(frozen=True)
class SearchLimits:
    time_ms: int = 1000
    depth: int = 12


@dataclass(frozen=True)
class EngineLine:
    multipv: int
    depth: int
    score_cp_side_to_move: int | None
    mate_in_side_to_move: int | None
    pv: tuple[str, ...]


@dataclass(frozen=True)
class EngineResult:
    engine_id: str
    engine_version: str
    protocol: str
    position: str
    limits: SearchLimits
    lines: tuple[EngineLine, ...]
    score_perspective: str
    elapsed_ms: int
    is_complete: bool


class EngineAdapter(Protocol):
    async def analyze(self, fen: str, limits: SearchLimits, multipv: int) -> EngineResult: ...

    async def close(self) -> None: ...


_MOVE = re.compile(r"^[a-i][0-9][a-i][0-9]$")


def validate_pv(fen: str, pv: tuple[str, ...]) -> bool:
    """Check every ICCS move against the authoritative RulesService."""
    try:
        position = xiangqi.Position.from_fen(fen)
        for move in pv:
            if not _MOVE.fullmatch(move):
                return False
            position = xiangqi.apply_move(position, move)
        return True
    except (xiangqi.PositionError, xiangqi.IllegalMoveError):
        return False


class UciEngineAdapter:
    """One reusable UCI process. Requests are serialized by its owner."""

    def __init__(self, command: tuple[str, ...], *, threads: int = 2, hash_mb: int = 64, coordinate_format: str = "auto"):
        self.command = command
        self.threads = max(1, min(threads, 2))
        self.hash_mb = max(16, min(hash_mb, 128))
        self.coordinate_format = coordinate_format if coordinate_format in {"zero_based", "one_based"} else "auto"
        self._active_coordinate_format = "zero_based"
        self.process: asyncio.subprocess.Process | None = None
        self.engine_name = Path(command[0]).stem
        self.engine_version = "unknown"
        self.options: set[str] = set()
        self._lock = asyncio.Lock()

    async def _send(self, command: str) -> None:
        if self.process is None or self.process.stdin is None or self.process.returncode is not None:
            raise EngineError("Engine process is not running.")
        self.process.stdin.write((command + "\n").encode("ascii"))
        await self.process.stdin.drain()

    async def _read_line(self, timeout: float) -> str:
        process = self.process
        if process is None or process.stdout is None:
            raise EngineError("Engine process is not running.")
        try:
            raw = await asyncio.wait_for(process.stdout.readline(), timeout)
        except TimeoutError as exc:
            raise EngineError("Engine protocol timed out.") from exc
        if not raw:
            code = process.returncode
            raise EngineError(f"Engine process exited unexpectedly (code {code}).")
        return raw.decode("utf-8", errors="replace").strip()

    async def _wait_for(self, expected: str, timeout: float, *, discover_options: bool = False) -> list[str]:
        deadline = time.monotonic() + timeout
        lines: list[str] = []
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise EngineError(f"Timed out waiting for {expected}.")
            line = await self._read_line(remaining)
            lines.append(line)
            if discover_options and line.startswith("option name "):
                self.options.add(line[len("option name "):].split(" type ", 1)[0])
            if line == expected:
                return lines

    async def _start(self) -> None:
        if self.process is not None and self.process.returncode is None:
            return
        await self._terminate()
        try:
            self.process = await asyncio.create_subprocess_exec(
                *self.command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
                cwd=str(Path(self.command[0]).expanduser().resolve().parent) if Path(self.command[0]).expanduser().is_file() else None,
            )
            lines = await self._handshake()
            for line in lines:
                if line.startswith("id name "):
                    self.engine_name = line[8:].strip()
                    version_match = re.search(r"\b(\d+(?:\.\d+){0,2}(?:[-+][\w.-]+)?)\b", self.engine_name)
                    if version_match:
                        self.engine_version = version_match.group(1)
            self._active_coordinate_format = self.coordinate_format
            if self._active_coordinate_format == "auto":
                self._active_coordinate_format = "one_based" if "fairy-stockfish" in self.engine_name.lower() else "zero_based"
            if "UCI_Variant" in self.options:
                await self._send("setoption name UCI_Variant value xiangqi")
            if "Threads" in self.options:
                await self._send(f"setoption name Threads value {self.threads}")
            if "Hash" in self.options:
                await self._send(f"setoption name Hash value {self.hash_mb}")
            await self._ready()
            logger.info("Started local UCI engine id=%s version=%s", self.engine_name, self.engine_version)
        except (OSError, EngineError, asyncio.CancelledError):
            await self._terminate()
            raise

    async def _handshake(self) -> list[str]:
        await self._send("uci")
        self.options.clear()
        return await self._wait_for("uciok", 8, discover_options=True)

    async def _ready(self) -> None:
        await self._send("isready")
        await self._wait_for("readyok", 8)

    async def _terminate(self) -> None:
        process, self.process = self.process, None
        if process is None:
            return
        if process.returncode is None:
            try:
                if process.stdin is not None:
                    process.stdin.write(b"quit\n")
                    await process.stdin.drain()
                await asyncio.wait_for(process.wait(), 1.0)
            except (OSError, TimeoutError):
                process.kill()
                await process.wait()
        if process.returncode not in (0, None):
            logger.warning("Local UCI engine process exited with code %s", process.returncode)

    async def analyze(self, fen: str, limits: SearchLimits, multipv: int) -> EngineResult:
        async with self._lock:
            await self._start()
            started = time.monotonic()
            self._current_fen = fen
            search_active = False
            try:
                if "MultiPV" in self.options:
                    await self._send(f"setoption name MultiPV value {multipv}")
                await self._ready()
                engine_fen = fen.split()
                if len(engine_fen) > 1 and engine_fen[1] == "r":
                    engine_fen[1] = "w"  # UCI uses w/b; the app's Xiangqi FEN uses r/b.
                await self._send(f"position fen {' '.join(engine_fen)}")
                await self._send(f"go movetime {limits.time_ms} depth {limits.depth}")
                search_active = True
                raw_lines: list[str] = []
                deadline = started + limits.time_ms / 1000 + 2.0
                while True:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise EngineError("Engine search exceeded its time limit.")
                    line = await self._read_line(remaining)
                    if line.startswith("info "):
                        raw_lines.append(line)
                    elif line.startswith("bestmove "):
                        best_move_parts = line.split()
                        best_move = self._to_iccs(best_move_parts[1]) if len(best_move_parts) > 1 else ""
                        search_active = False
                        break
                lines = self._parse_lines(raw_lines, multipv)
                if not best_move or not validate_pv(fen, (best_move,)):
                    raise EngineError("Engine returned no legal best move.")
                if not lines or not lines[0].pv or not validate_pv(fen, lines[0].pv):
                    raise EngineError("Engine returned no legal principal variation.")
                if lines[0].pv[0] != best_move:
                    raise EngineError("Engine best move does not match its principal variation.")
                return EngineResult(
                    engine_id=self.engine_name,
                    engine_version=self.engine_version,
                    protocol="uci",
                    position=fen,
                    limits=limits,
                    lines=tuple(lines),
                    score_perspective="side_to_move",
                    elapsed_ms=max(0, round((time.monotonic() - started) * 1000)),
                    is_complete=True,
                )
            except asyncio.CancelledError:
                if search_active:
                    await self._stop_or_restart()
                raise
            except EngineError:
                if search_active:
                    await self._stop_or_restart()
                raise

    def _parse_lines(self, raw_lines: list[str], max_lines: int) -> list[EngineLine]:
        parsed: dict[int, EngineLine] = {}
        for raw in raw_lines:
            parts = raw.split()
            try:
                depth = int(parts[parts.index("depth") + 1])
                multipv = int(parts[parts.index("multipv") + 1]) if "multipv" in parts else 1
                score_kind = parts[parts.index("score") + 1]
                score_value = int(parts[parts.index("score") + 2])
                pv_index = parts.index("pv")
                pv = tuple(self._to_iccs(token) for token in parts[pv_index + 1:])
                if not pv or not validate_pv(self._current_fen, pv):
                    continue
                line = EngineLine(
                    multipv=multipv,
                    depth=depth,
                    score_cp_side_to_move=score_value if score_kind == "cp" else None,
                    mate_in_side_to_move=score_value if score_kind == "mate" else None,
                    pv=pv,
                )
                previous = parsed.get(multipv)
                if previous is None or depth >= previous.depth:
                    parsed[multipv] = line
            except (ValueError, IndexError):
                continue
        return [parsed[key] for key in sorted(parsed) if key <= max_lines]

    def _to_iccs(self, move: str) -> str:
        if self._active_coordinate_format == "one_based":
            match = re.fullmatch(r"([a-i])(10|[1-9])([a-i])(10|[1-9])", move)
            if match is None:
                return ""
            file_from, rank_from, file_to, rank_to = match.groups()
            return f"{file_from}{int(rank_from) - 1}{file_to}{int(rank_to) - 1}"
        return move if _MOVE.fullmatch(move) else ""

    async def _stop_or_restart(self) -> None:
        try:
            if self.process is not None and self.process.returncode is None:
                await self._send("stop")
                await self._wait_for_bestmove(1.0)
        except (EngineError, OSError):
            await self._terminate()

    async def _wait_for_bestmove(self, timeout: float) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            line = await self._read_line(max(0.01, deadline - time.monotonic()))
            if line.startswith("bestmove "):
                return

    async def close(self) -> None:
        await self._terminate()

    _current_fen: str = ""


class MockEngine:
    """Deterministic adapter for tests and setups without a selected binary."""

    engine_id = "mock-xiangqi"
    engine_version = "1.0"

    def __init__(self, *, delay_seconds: float = 0, fail: str | None = None, score_cp: int = 42):
        self.delay_seconds = delay_seconds
        self.fail = fail
        self.score_cp = score_cp
        self.calls = 0
        self.closed = False

    async def analyze(self, fen: str, limits: SearchLimits, multipv: int) -> EngineResult:
        self.calls += 1
        if self.fail == "crash":
            raise EngineError("Mock engine crashed.")
        if self.delay_seconds:
            await asyncio.sleep(self.delay_seconds)
        position = xiangqi.Position.from_fen(fen)
        legal = xiangqi.legal_moves(position)
        lines = tuple(
            EngineLine(index + 1, min(4, limits.depth), self.score_cp, None, (move,))
            for index, move in enumerate(legal[:multipv])
        )
        if self.fail == "invalid_pv":
            lines = (EngineLine(1, 1, 0, None, ("a0a9",)),)
        return EngineResult(self.engine_id, self.engine_version, "mock", fen, limits, lines, "side_to_move", 0, True)

    async def close(self) -> None:
        self.closed = True


class EngineService:
    """Bounds queued requests around one serialized local engine process."""

    def __init__(self, adapter: EngineAdapter, *, max_concurrent: int = 3, timeout_grace_seconds: float = 2.0,
                 queue_timeout_seconds: float = 10.0):
        self.adapter = adapter
        self._slots = asyncio.Semaphore(max(1, min(max_concurrent, 3)))
        self._adapter_lock = asyncio.Lock()
        self.timeout_grace_seconds = max(0.01, timeout_grace_seconds)
        self.queue_timeout_seconds = max(0.01, queue_timeout_seconds)
        self._active: dict[str, asyncio.Task[object]] = {}

    async def analyze(self, fen: str, limits: SearchLimits, multipv: int, job_id: str | None = None) -> EngineResult:
        if self._slots.locked():
            raise EngineError("Engine is busy; try again shortly.")
        try:
            xiangqi.Position.from_fen(fen)
        except xiangqi.PositionError as exc:
            raise ValueError("Invalid FEN.") from exc
        current_task = asyncio.current_task()
        if job_id and current_task:
            if job_id in self._active:
                raise ValueError("job_id is already active.")
            self._active[job_id] = current_task
        try:
            async with self._slots:
                try:
                    await asyncio.wait_for(self._adapter_lock.acquire(), timeout=self.queue_timeout_seconds)
                except TimeoutError as exc:
                    raise EngineError("Engine queue wait timed out.") from exc
                try:
                    result = await asyncio.wait_for(
                        self.adapter.analyze(fen, limits, multipv),
                        timeout=limits.time_ms / 1000 + self.timeout_grace_seconds,
                    )
                except TimeoutError as exc:
                    raise EngineError("Engine search timed out.") from exc
                finally:
                    self._adapter_lock.release()
                valid_lines = tuple(line for line in result.lines if validate_pv(fen, line.pv))
                if not valid_lines:
                    raise EngineError("Engine returned no legal principal variation.")
                logger.info(
                    "Engine analysis complete engine_id=%s version=%s elapsed_ms=%d depth=%d multipv=%d",
                    result.engine_id,
                    result.engine_version,
                    result.elapsed_ms,
                    max(line.depth for line in valid_lines),
                    len(valid_lines),
                )
                return EngineResult(
                    engine_id=result.engine_id,
                    engine_version=result.engine_version,
                    protocol=result.protocol,
                    position=result.position,
                    limits=result.limits,
                    lines=valid_lines,
                    score_perspective=result.score_perspective,
                    elapsed_ms=result.elapsed_ms,
                    is_complete=result.is_complete,
                )
        finally:
            if job_id:
                self._active.pop(job_id, None)

    async def stop(self, job_id: str) -> bool:
        task = self._active.get(job_id)
        if task is None or task.done():
            return False
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        return True

    async def close(self) -> None:
        await self.adapter.close()


def configured_engine_service() -> EngineService:
    raw_command = os.getenv("ENGINE_COMMAND", "").strip()
    if not raw_command:
        raise EngineError("Set ENGINE_COMMAND to a local UCI engine executable to enable engine analysis.")
    command = tuple(shlex.split(raw_command, posix=os.name != "nt"))
    if not command:
        raise EngineError("ENGINE_COMMAND is empty.")
    executable = Path(command[0]).expanduser()
    if executable.parent != Path(".") and not executable.is_file():
        raise EngineError("Configured ENGINE_COMMAND executable does not exist.")
    coordinate_format = os.getenv("ENGINE_COORDINATES", "auto").strip().lower()
    return EngineService(UciEngineAdapter(command, coordinate_format=coordinate_format))
