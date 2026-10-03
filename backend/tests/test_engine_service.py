import asyncio
import sys

import pytest

from backend.app.engine.service import EngineError, EngineService, MockEngine, SearchLimits, UciEngineAdapter, validate_pv


INITIAL_FEN = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR r - - 0 1"


def test_mock_engine_returns_provenance_and_valid_pv():
    async def run():
        service = EngineService(MockEngine())
        result = await service.analyze(INITIAL_FEN, SearchLimits(time_ms=500, depth=6), 3)
        assert result.engine_id == "mock-xiangqi"
        assert result.score_perspective == "side_to_move"
        assert 1 <= len(result.lines) <= 3
        assert validate_pv(INITIAL_FEN, result.lines[0].pv)

    asyncio.run(run())


def test_invalid_engine_pv_is_rejected():
    async def run():
        service = EngineService(MockEngine(fail="invalid_pv"))
        with pytest.raises(EngineError, match="no legal principal variation"):
            await service.analyze(INITIAL_FEN, SearchLimits(), 1)

    asyncio.run(run())


def test_hanging_engine_times_out_and_cancellation_releases_job():
    async def run():
        hanging = EngineService(MockEngine(delay_seconds=1), timeout_grace_seconds=0.02)
        with pytest.raises(EngineError, match="timed out"):
            await hanging.analyze(INITIAL_FEN, SearchLimits(time_ms=100, depth=1), 1)

        cancellable = EngineService(MockEngine(delay_seconds=1))
        task = asyncio.create_task(cancellable.analyze(INITIAL_FEN, SearchLimits(), 1, "cancel-me"))
        await asyncio.sleep(0)
        assert await cancellable.stop("cancel-me") is True
        await asyncio.gather(task, return_exceptions=True)
        assert await cancellable.stop("cancel-me") is False

    asyncio.run(run())


def test_queued_engine_request_gets_its_search_budget_after_queueing():
    class DelayedAdapter:
        async def analyze(self, fen, limits, multipv):
            await asyncio.sleep(0.1)
            return await MockEngine().analyze(fen, limits, multipv)

        async def close(self):
            return None

    async def run():
        service = EngineService(DelayedAdapter(), max_concurrent=3, queue_timeout_seconds=0.5)
        first = asyncio.create_task(service.analyze(INITIAL_FEN, SearchLimits(time_ms=300, depth=4), 1))
        await asyncio.sleep(0.01)
        second = asyncio.create_task(service.analyze(INITIAL_FEN, SearchLimits(time_ms=150, depth=4), 1))
        first_result, second_result = await asyncio.gather(first, second)
        assert first_result.lines and second_result.lines

    asyncio.run(run())


def test_engine_queue_wait_is_bounded_separately_from_search():
    class DelayedAdapter:
        async def analyze(self, fen, limits, multipv):
            await asyncio.sleep(0.15)
            return await MockEngine().analyze(fen, limits, multipv)

        async def close(self):
            return None

    async def run():
        service = EngineService(DelayedAdapter(), max_concurrent=3, queue_timeout_seconds=0.01)
        first = asyncio.create_task(service.analyze(INITIAL_FEN, SearchLimits(time_ms=300, depth=4), 1))
        await asyncio.sleep(0)
        with pytest.raises(EngineError, match="queue wait timed out"):
            await service.analyze(INITIAL_FEN, SearchLimits(time_ms=300, depth=4), 1)
        assert (await first).lines

    asyncio.run(run())


def test_engine_crash_is_reported_without_a_fake_move():
    async def run():
        service = EngineService(MockEngine(fail="crash"))
        with pytest.raises(EngineError, match="crashed"):
            await service.analyze(INITIAL_FEN, SearchLimits(), 1)

    asyncio.run(run())


def test_uci_transcript_handshake_options_analysis_and_quit():
    script = r'''import sys
for raw in sys.stdin:
    command = raw.strip()
    if command == "uci":
        print("id name Fairy-Stockfish 14.0.1 XQ", flush=True)
        print("option name UCI_Variant type combo default chess var xiangqi", flush=True)
        print("option name MultiPV type spin default 1 min 1 max 3", flush=True)
        print("option name Threads type spin default 1 min 1 max 2", flush=True)
        print("option name Hash type spin default 16 min 1 max 128", flush=True)
        print("uciok", flush=True)
    elif command == "isready":
        print("readyok", flush=True)
    elif command.startswith("go "):
        print("info depth 4 multipv 1 score cp 28 nodes 20 pv a4a5", flush=True)
        print("info depth 4 multipv 2 score cp -5 nodes 18 pv c4c5", flush=True)
        print("bestmove a4a5", flush=True)
    elif command == "stop":
        print("bestmove a4a5", flush=True)
    elif command == "quit":
        break
'''

    async def run():
        adapter = UciEngineAdapter((sys.executable, "-u", "-c", script))
        try:
            result = await adapter.analyze(INITIAL_FEN, SearchLimits(time_ms=300, depth=4), 2)
            assert result.engine_id == "Fairy-Stockfish 14.0.1 XQ"
            assert result.engine_version == "14.0.1"
            assert len(result.lines) == 2
            assert result.lines[0].pv == ("a3a4",)
            assert result.protocol == "uci"
        finally:
            await adapter.close()
        assert adapter.process is None

    asyncio.run(run())
