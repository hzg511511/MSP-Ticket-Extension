"""工具函数：拼接飞书多维表格「任务详情描述」字段内容。"""


def format_task_detail(customer_name: str, user_issue: str, issue_cause: str) -> str:
    return f"【客户名称】{customer_name}\n【问题】{user_issue}\n【原因及措施】{issue_cause}"
