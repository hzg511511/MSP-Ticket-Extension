from hypothesis import given, settings
import hypothesis.strategies as st
from unittest.mock import patch, MagicMock
from backend.services.bitable import create_record

nonempty = st.text(min_size=1).filter(lambda s: s.strip())


@given(nonempty, nonempty, nonempty)
@settings(max_examples=50)
def test_create_record_sends_fields(task_name, root_cause, solution_steps):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"code": 0, "data": {"record": {"record_id": "r1"}}}
    with patch("backend.services.bitable.get_access_token", return_value="tok"), \
         patch("backend.services.bitable.requests.post", return_value=mock_resp) as mock_post:
        fields = {
            "任务名称": task_name,
            "根因分析/知识点摘要": root_cause,
            "解决步骤": solution_steps,
        }
        record_id = create_record(fields)
        assert record_id == "r1"
        sent = mock_post.call_args.kwargs["json"]["fields"]
        assert sent["任务名称"] == task_name
