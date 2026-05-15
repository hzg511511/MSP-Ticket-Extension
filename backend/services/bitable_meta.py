"""启动时从飞书多维表格获取多选字段及其选项，缓存供全局使用。"""

import requests
from backend.config import feishu
from backend.services.feishu_auth import get_access_token

TARGET_FIELDS = {"服务类别", "服务名称", "问题分类", "解决方案分类"}

# {字段名: [选项名, ...]}，启动时填充
multiselect_fields: dict[str, list[str]] = {}


def load_multiselect_fields() -> None:
    token = get_access_token()
    url = (
        f"https://open.feishu.cn/open-apis/bitable/v1"
        f"/apps/{feishu.app_token}/tables/{feishu.table_id}/fields"
    )
    data = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=8).json()
    if data.get("code") != 0:
        raise RuntimeError(f"FEISHU_API_ERROR: {data.get('msg')}")

    multiselect_fields.clear()
    for field in data.get("data", {}).get("items", []):
        if field.get("type") == 4 and field.get("field_name") in TARGET_FIELDS:
            options = [opt["name"] for opt in field.get("property", {}).get("options", [])]
            if options:
                multiselect_fields[field["field_name"]] = options
