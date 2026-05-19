"""通过邮箱查询飞书用户 open_id。"""

import requests
from backend.services.feishu_auth import get_access_token

_cache: dict[str, str] = {}


def get_open_id_by_email(email: str) -> str:
    """通过邮箱获取用户 open_id，找不到时抛出 RuntimeError。"""
    if email in _cache:
        return _cache[email]
    token = get_access_token()
    resp = requests.post(
        "https://open.feishu.cn/open-apis/contact/v3/users/batch_get_id",
        params={"user_id_type": "open_id"},
        json={"emails": [email]},
        headers={"Authorization": f"Bearer {token}"},
        timeout=8,
    )
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"FEISHU_API_ERROR: {data.get('msg')}")
    user_list = data.get("data", {}).get("user_list", [])
    if not user_list or not user_list[0].get("user_id"):
        raise RuntimeError(f"USER_NOT_FOUND: 邮箱 {email} 未找到对应飞书用户")
    open_id = user_list[0]["user_id"]
    _cache[email] = open_id
    return open_id
