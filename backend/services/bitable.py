"""飞书多维表格记录写入服务。"""

import requests
from backend.config import feishu
from backend.services.feishu_auth import get_access_token


def create_record(fields: dict) -> str:
    """向飞书 Bitable 写入一条记录，返回 record_id。"""
    token = get_access_token()
    url = (
        f"https://open.feishu.cn/open-apis/bitable/v1"
        f"/apps/{feishu.app_token}/tables/{feishu.table_id}/records"
    )
    resp = requests.post(
        url,
        json={"fields": fields},
        headers={"Authorization": f"Bearer {token}"},
        timeout=8,
    )
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"FEISHU_API_ERROR: {data.get('msg')}")
    return data["data"]["record"]["record_id"]
