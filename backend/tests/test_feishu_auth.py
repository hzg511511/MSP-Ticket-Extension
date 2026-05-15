import time
from unittest.mock import patch, MagicMock
import pytest
import backend.services.feishu_auth as auth_module


def _mock_resp(code=0, token="tok", expire=7200):
    m = MagicMock()
    m.json.return_value = {"code": code, "tenant_access_token": token, "expire": expire, "msg": "err"}
    return m


def setup_function():
    auth_module._cache.update({"token": None, "expires_at": 0})


def test_cache_hit():
    auth_module._cache.update({"token": "cached", "expires_at": time.time() + 1000})
    with patch("requests.post") as mock_post:
        assert auth_module.get_access_token() == "cached"
        mock_post.assert_not_called()


def test_cache_miss_fetches():
    with patch("requests.post", return_value=_mock_resp()) as mock_post:
        token = auth_module.get_access_token()
        assert token == "tok"
        mock_post.assert_called_once()


def test_api_failure_raises():
    with patch("requests.post", return_value=_mock_resp(code=99)):
        with pytest.raises(RuntimeError, match="AUTH_ERROR"):
            auth_module.get_access_token()
