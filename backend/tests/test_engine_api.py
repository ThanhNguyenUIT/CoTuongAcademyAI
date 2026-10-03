from fastapi.testclient import TestClient

from backend.app.engine.service import EngineService, MockEngine
from backend.app.main import app


INITIAL_FEN = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR r - - 0 1"


def client_with_mock(score_cp: int = 42) -> TestClient:
    app.state.engine_service = EngineService(MockEngine(score_cp=score_cp))
    return TestClient(app)


def test_analysis_response_has_provenance_multipv_and_red_perspective():
    with client_with_mock() as client:
        response = client.post(
            "/v1/engine/analyze",
            json={"fen": INITIAL_FEN, "time_ms": 500, "depth": 6, "multipv": 3},
        )
    assert response.status_code == 200
    payload = response.json()
    assert payload["engine_id"] == "mock-xiangqi"
    assert payload["score_perspective"] == "side_to_move"
    assert payload["lines"][0]["score_cp_side_to_move"] == 42
    assert payload["lines"][0]["score_cp_red"] == 42
    assert payload["best_move"] == payload["lines"][0]["pv"][0]


def test_black_to_move_score_is_converted_to_red_perspective():
    black_to_move = INITIAL_FEN.replace(" r - - ", " b - - ")
    with client_with_mock(score_cp=57) as client:
        response = client.post("/v1/engine/analyze", json={"fen": black_to_move, "multipv": 1})
    assert response.status_code == 200
    line = response.json()["lines"][0]
    assert line["score_cp_side_to_move"] == 57
    assert line["score_cp_red"] == -57


def test_bad_fen_is_rejected_and_unconfigured_engine_is_not_faked(monkeypatch):
    with client_with_mock() as client:
        invalid = client.post("/v1/engine/analyze", json={"fen": "not-a-fen"})
    assert invalid.status_code == 422
    assert invalid.json()["detail"]["code"] == "invalid_fen_or_job"

    app.state.engine_service = None
    monkeypatch.delenv("ENGINE_COMMAND", raising=False)
    with TestClient(app) as client:
        unavailable = client.post("/v1/engine/analyze", json={"fen": INITIAL_FEN})
    assert unavailable.status_code == 503
    assert unavailable.json()["detail"]["code"] == "engine_unavailable"


def test_engine_request_limits_are_bounded():
    with client_with_mock() as client:
        response = client.post("/v1/engine/analyze", json={"fen": INITIAL_FEN, "time_ms": 6000})
    assert response.status_code == 422
