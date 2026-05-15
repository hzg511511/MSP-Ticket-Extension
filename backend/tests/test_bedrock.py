import json
import pytest
from unittest.mock import patch, MagicMock
from backend.services.bedrock import generate_fields

_VALID_RESPONSE = {
    "task_name": "修复登录超时问题",
    "root_cause": "Token 过期时间配置过短",
    "solution_steps": "1. 调整 token 有效期\n2. 重启服务",
    "qa": "Q: 为什么登录失效？\nA: Token 过期时间过短导致",
}


def _mock_resp(body: dict, status=200):
    m = MagicMock()
    m.status_code = status
    m.raise_for_status = MagicMock()
    m.json.return_value = {
        "output": {
            "message": {
                "content": [{"text": json.dumps(body, ensure_ascii=False)}]
            }
        }
    }
    return m


def test_generate_fields_returns_all_keys():
    with patch("backend.services.bedrock.requests.post", return_value=_mock_resp(_VALID_RESPONSE)):
        result = generate_fields("登录后立即失效", "Token 过期时间设置为 1 分钟")
    assert set(result.keys()) == {"task_name", "root_cause", "solution_steps", "qa"}


def test_generate_fields_values_match():
    with patch("backend.services.bedrock.requests.post", return_value=_mock_resp(_VALID_RESPONSE)):
        result = generate_fields("登录后立即失效", "Token 过期时间设置为 1 分钟")
    assert result["task_name"] == _VALID_RESPONSE["task_name"]
    assert result["root_cause"] == _VALID_RESPONSE["root_cause"]


def test_generate_fields_strips_markdown_codeblock():
    """模型返回 ```json ... ``` 时能正确解析。"""
    wrapped = f"```json\n{json.dumps(_VALID_RESPONSE, ensure_ascii=False)}\n```"
    m = MagicMock()
    m.raise_for_status = MagicMock()
    m.json.return_value = {
        "output": {"message": {"content": [{"text": wrapped}]}}
    }
    with patch("backend.services.bedrock.requests.post", return_value=m):
        result = generate_fields("问题", "原因")
    assert result["task_name"] == _VALID_RESPONSE["task_name"]


def test_generate_fields_http_error_raises():
    m = MagicMock()
    m.raise_for_status.side_effect = Exception("HTTP 401")
    with patch("backend.services.bedrock.requests.post", return_value=m):
        with pytest.raises(Exception, match="HTTP 401"):
            generate_fields("问题", "原因")
