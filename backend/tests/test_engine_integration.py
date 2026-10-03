import asyncio
import os
import shlex
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.engine.service import EngineService, SearchLimits, UciEngineAdapter, validate_pv
from backend.app.main import app
from backend.app.rules import xiangqi


INITIAL_FEN = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR r - - 0 1"
ENGINE_COMMAND = os.getenv("ENGINE_COMMAND", "").strip()
pytestmark = pytest.mark.skipif(not ENGINE_COMMAND, reason="Set ENGINE_COMMAND to a verified local Xiangqi UCI engine.")


def engine_command() -> tuple[str, ...]:
    command = tuple(shlex.split(ENGINE_COMMAND, posix=os.name != "nt"))
    executable = Path(command[0])
    assert executable.is_file(), f"ENGINE_COMMAND binary does not exist: {executable}"
    return command


def test_real_engine_returns_legal_best_move_multipv_and_reuses_one_process():
    async def run():
        adapter = UciEngineAdapter(engine_command())
        service = EngineService(adapter, max_concurrent=3)
        try:
            result = await service.analyze(INITIAL_FEN, SearchLimits(time_ms=1000, depth=12), 3)
            legal = set(xiangqi.legal_moves(xiangqi.Position.from_fen(INITIAL_FEN)))
            assert result.protocol == "uci"
            assert result.engine_id
            assert result.engine_version != "unknown"
            assert result.lines
            assert result.lines[0].pv[0] in legal
            assert all(validate_pv(INITIAL_FEN, line.pv) for line in result.lines)
            process_id = adapter.process.pid if adapter.process else None

            concurrent = await asyncio.gather(*[
                service.analyze(INITIAL_FEN, SearchLimits(time_ms=250, depth=5), 1)
                for _ in range(3)
            ])
            assert len(concurrent) == 3
            assert all(item.lines[0].pv[0] in legal for item in concurrent)
            assert adapter.process is not None and adapter.process.pid == process_id
            stop_task = asyncio.create_task(
                service.analyze(INITIAL_FEN, SearchLimits(time_ms=5000, depth=20), 1, "stop-smoke")
            )
            await asyncio.sleep(0.05)
            assert await service.stop("stop-smoke") is True
            stopped_result = await asyncio.gather(stop_task, return_exceptions=True)
            assert isinstance(stopped_result[0], asyncio.CancelledError)
            assert adapter.process is not None and adapter.process.returncode is None
            after_stop = await service.analyze(INITIAL_FEN, SearchLimits(time_ms=250, depth=5), 1)
            assert after_stop.lines[0].pv[0] in legal
            crashed_process = adapter.process
            crashed_process.kill()
            await crashed_process.wait()
            restarted = await service.analyze(INITIAL_FEN, SearchLimits(time_ms=250, depth=5), 1)
            assert restarted.lines[0].pv[0] in legal
            assert adapter.process is not None and adapter.process.pid != process_id
            print(
                f"engine={result.engine_id} version={result.engine_version} protocol={result.protocol} "
                f"single_elapsed_ms={result.elapsed_ms} depth={result.lines[0].depth} multipv={len(result.lines)} "
                f"concurrent_3_elapsed_ms={[item.elapsed_ms for item in concurrent]} stop=PASS process_id={process_id} "
                f"restarted_process_id={adapter.process.pid}"
            )
        finally:
            await service.close()

    asyncio.run(run())


def test_real_engine_analysis_api_returns_validated_provenance(monkeypatch):
    monkeypatch.setenv("ENGINE_COMMAND", ENGINE_COMMAND)
    monkeypatch.setenv("ENGINE_COORDINATES", "auto")
    app.state.engine_service = None
    with TestClient(app) as client:
        response = client.post(
            "/v1/engine/analyze",
            json={"fen": INITIAL_FEN, "time_ms": 500, "depth": 8, "multipv": 3},
        )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["engine_id"]
    assert payload["engine_version"] != "unknown"
    assert payload["protocol"] == "uci"
    assert payload["score_perspective"] == "side_to_move"
    assert 1 <= len(payload["lines"]) <= 3
    assert payload["best_move"] == payload["lines"][0]["pv"][0]
