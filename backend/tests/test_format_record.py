from hypothesis import given, settings
import hypothesis.strategies as st
from backend.utils.format_record import format_task_detail


@given(st.text(), st.text(), st.text())
@settings(max_examples=100)
def test_format_task_detail_invariant(customer_name, user_issue, issue_cause):
    result = format_task_detail(customer_name, user_issue, issue_cause)
    assert result == f"【客户名称】{customer_name}\n【问题】{user_issue}\n【原因及措施】{issue_cause}"
