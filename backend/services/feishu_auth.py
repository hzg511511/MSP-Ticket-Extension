"""飞书 tenant_access_token 获取与缓存。"""

import time
import requests
from backend.config import feishu

_cache = {"token": None, "expires_at": 0}


def get_access_token() -> str:
    if _cache["token"] and time.time() < _cache["expires_at"] - 300:
        return _cache["token"]

    resp = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": feishu.app_id, "app_secret": feishu.app_secret},
        timeout=8,
    )
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"AUTH_ERROR: {data.get('msg')}")

    _cache["token"] = data["tenant_access_token"]
    _cache["expires_at"] = time.time() + data["expire"]
    return _cache["token"]
