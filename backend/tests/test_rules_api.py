from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.rules.xiangqi import STARTING_FEN

client = TestClient(app)


def test_legal_moves_endpoint_returns_starting_position_contract() -> None:
    response = client.post("/v1/rules/legal-moves", json={"fen": STARTING_FEN})

    assert response.status_code == 200
    assert response.json()["fen"] == STARTING_FEN
    assert len(response.json()["moves"]) == 44
    assert response.json()["status"] == "active"


def test_invalid_fen_has_stable_error_code() -> None:
    response = client.post("/v1/rules/legal-moves", json={"fen": "bad fen"})

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "invalid_fen"


def test_apply_endpoint_rejects_illegal_move() -> None:
    response = client.post(
        "/v1/rules/apply-move",
        json={"fen": STARTING_FEN, "move": "a0a9", "history_fens": [STARTING_FEN]},
    )

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "illegal_move"


def test_repeated_position_is_held_for_review_instead_of_guessed_draw() -> None:
    fen = STARTING_FEN
    positions = [fen]
    moves = ["h0g2", "h9g7", "g2h0", "g7h9", "h0g2", "h9g7", "g2h0"]
    for move in moves:
        response = client.post("/v1/rules/apply-move", json={"fen": fen, "move": move, "history_fens": positions})
        assert response.status_code == 200
        fen = response.json()["fen"]
        positions.append(fen)

    response = client.post("/v1/rules/apply-move", json={"fen": fen, "move": "g7h9", "history_fens": positions})
    assert response.status_code == 200
    assert response.json()["status"] == "repetition_review_required"
    assert response.json()["repetition_count"] == 3


def test_cors_allows_local_frontend_post_only() -> None:
    allowed = client.options(
        "/v1/rules/legal-moves",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    denied = client.options(
        "/v1/rules/legal-moves",
        headers={
            "Origin": "https://example.invalid",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert allowed.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"
    assert "access-control-allow-origin" not in denied.headers
