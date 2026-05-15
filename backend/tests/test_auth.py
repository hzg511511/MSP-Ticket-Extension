from hypothesis import given, settings, assume
import hypothesis.strategies as st
from unittest.mock import patch


def test_missing_api_key_returns_401():
    from backend.app import app
    with app.test_client() as client:
        with patch("backend.services.bitable.create_record") as mock_create:
            resp = client.post("/api/submit", json={})
            assert resp.status_code == 401
            mock_create.assert_not_called()


@given(st.text().filter(lambda s: "\n" not in s and "\r" not in s))
@settings(max_examples=100)
def test_wrong_api_key_returns_401(bad_key):
    import os
    assume(bad_key != os.environ.get("API_KEY", ""))
    from backend.app import app
    with app.test_client() as client:
        with patch("backend.services.bitable.create_record") as mock_create:
            resp = client.post("/api/submit", json={}, headers={"x-api-key": bad_key})
            assert resp.status_code == 401
            mock_create.assert_not_called()
