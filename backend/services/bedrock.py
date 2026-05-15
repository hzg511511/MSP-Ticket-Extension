"""通过 AWS Bedrock API Key 生成多维表格字段内容。"""

import json
import requests
from backend.config import bedrock as bedrock_cfg

_SYSTEM = "你是一名技术问题分析专家，擅长从问题描述和原因措施中提炼结构化知识。请严格按要求返回 JSON，不要包含任何其他内容。"


def generate_fields(user_issue: str, issue_cause: str, multiselect_fields: dict[str, list[str]] = None) -> dict:
    """
    根据用户问题和原因及措施，生成：
    - task_name: 任务名称
    - root_cause: 根因分析/知识点摘要
    - solution_steps: 解决步骤
    - qa: Q&A提取
    - multiselect: {字段名: [已选选项名, ...]}（仅当传入 multiselect_fields 时）
    """
    multiselect_section = ""
    if multiselect_fields:
        fields_desc = "\n".join(
            f'- "{name}": 可选值为 {opts}'
            for name, opts in multiselect_fields.items()
        )
        multiselect_section = f"""
请为以下每个字段，从给定选项中选出匹配度最高的一个（必须从列表中选，只能选一个，确实无法匹配才返回空列表）。
结果放在 "multiselect" 键下，格式为 {{字段名: ["选项名"]}} 或 {{字段名: []}}：
{fields_desc}
"""

    prompt = f"""请根据以下信息生成字段内容，以 JSON 格式返回：

【问题】
{user_issue}

【原因及措施】
{issue_cause}

返回格式（只返回 JSON，不要有其他内容）：
{{
  "task_name": "简洁的任务名称，一句话概括问题",
  "root_cause": "根因分析和知识点摘要，说明问题本质原因",
  "solution_steps": "分步骤的解决方案",
  "qa": "Q: 问题描述\\nA: 解决答案"{',\n  "multiselect": {{}}' if multiselect_fields else ''}
}}{multiselect_section}"""

    url = f"https://bedrock-runtime.{bedrock_cfg.region}.amazonaws.com/model/{bedrock_cfg.model_id}/converse"
    payload = {
        "system": [{"text": _SYSTEM}],
        "messages": [{"role": "user", "content": [{"text": prompt}]}],
    }
    resp = requests.post(
        url,
        json=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bedrock_cfg.api_key}",
        },
        timeout=30,
    )
    resp.raise_for_status()
    text = resp.json()["output"]["message"]["content"][0]["text"].strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())
