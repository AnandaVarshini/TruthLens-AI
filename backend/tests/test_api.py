"""API integration tests (run against the real trained model and a temp database)."""
from __future__ import annotations


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["model_ready"] is True, body
    assert body["status"] == "ok"


def test_register_login_and_profile(client, registered_user):
    # duplicate email is rejected
    duplicate = client.post("/api/auth/register", json=registered_user["payload"])
    assert duplicate.status_code == 409

    # wrong password is rejected
    bad = client.post(
        "/api/auth/login",
        json={"email": registered_user["user"]["email"], "password": "WrongPass123"},
    )
    assert bad.status_code == 401

    # correct password returns a token
    good = client.post(
        "/api/auth/login",
        json={"email": registered_user["user"]["email"], "password": "StrongPass123"},
    )
    assert good.status_code == 200
    assert good.json()["user"]["email"] == registered_user["email"]

    me = client.get("/api/auth/me", headers=registered_user["headers"])
    assert me.status_code == 200
    assert me.json()["name"] == "Test Student"


def test_register_rejects_mismatched_passwords(client):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "No Match",
            "email": "nomatch@example.com",
            "password": "StrongPass123",
            "confirm_password": "DifferentPass123",
        },
    )
    assert response.status_code == 422


def test_protected_endpoints_require_token(client):
    assert client.get("/api/predictions").status_code == 401
    assert client.get("/api/predictions/stats").status_code == 401
    assert client.post("/api/predict", json={"text": "A claim that is long enough."}).status_code == 401


def test_prediction_returns_real_model_output(client, registered_user):
    text = "The unemployment rate has fallen to its lowest level in fifty years."
    response = client.post("/api/predict", json={"text": text}, headers=registered_user["headers"])
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["label"] in {"Real", "Misleading", "Partially False", "Fake"}
    assert body["model_name"]
    assert body["scores"] and len(body["scores"]) == 4
    assert abs(sum(item["score"] for item in body["scores"]) - 1.0) < 1e-4
    assert body["score_type"] in {"probability", "decision_score"}


def test_prediction_validation_and_errors(client, registered_user):
    empty = client.post("/api/predict", json={"text": "  "}, headers=registered_user["headers"])
    assert empty.status_code == 422

    too_long = client.post(
        "/api/predict", json={"text": "word " * 2000}, headers=registered_user["headers"]
    )
    assert too_long.status_code == 422


def test_history_is_user_scoped(client, registered_user):
    # user A creates two predictions
    for text in (
        "The new policy will reduce taxes for every household in the country.",
        "Scientists confirm that the moon is made of blue cheese.",
    ):
        assert (
            client.post("/api/predict", json={"text": text}, headers=registered_user["headers"]).status_code
            == 201
        )

    # user B registers and sees an empty history
    other = client.post(
        "/api/auth/register",
        json={
            "name": "Other Student",
            "email": "other@example.com",
            "password": "AnotherPass123",
            "confirm_password": "AnotherPass123",
        },
    )
    assert other.status_code == 201
    other_headers = {"Authorization": f"Bearer {other.json()['access_token']}"}

    history_a = client.get("/api/predictions", headers=registered_user["headers"]).json()
    history_b = client.get("/api/predictions", headers=other_headers).json()
    assert history_a["total"] >= 2
    assert history_b["total"] == 0

    # user B cannot delete user A's prediction
    target = history_a["items"][0]["id"]
    assert client.delete(f"/api/predictions/{target}", headers=other_headers).status_code == 404

    # user A can delete their own prediction
    assert client.delete(f"/api/predictions/{target}", headers=registered_user["headers"]).status_code == 204


def test_dashboard_stats(client, registered_user):
    client.post(
        "/api/predict",
        json={"text": "A completely invented claim about a secret island nation."},
        headers=registered_user["headers"],
    )
    response = client.get("/api/predictions/stats", headers=registered_user["headers"])
    assert response.status_code == 200
    body = response.json()
    assert body["total_predictions"] >= 1
    assert len(body["counts_by_label"]) == 4
    assert body["model_accuracy_test"] is not None


def test_insights_expose_computed_results(client):
    response = client.get("/api/insights")
    assert response.status_code == 200
    body = response.json()
    assert body["selected_model"] in body["candidates"]
    assert 0.0 <= body["selected_model_metrics"]["accuracy"] <= 1.0
    assert len(body["selected_model_metrics"]["confusion_matrix"]) == 4
    assert body["dataset"]["split_counts"]["train"] > 0
