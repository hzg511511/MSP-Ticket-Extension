import os
from unittest.mock import patch

# 在任何模块导入前设置测试环境变量
_TEST_ENV = {
    "FEISHU_APP_ID": "test_app_id",
    "FEISHU_APP_SECRET": "test_app_secret",
    "FEISHU_BITABLE_URL": "https://example.feishu.cn/wiki/AppToken?table=tblTableId",
    "API_KEY": "test_api_key",
    "AWS_REGION": "us-east-1",
    "BEDROCK_API_KEY": "test_bedrock_key",
    "BEDROCK_MODEL_ID": "us.anthropic.claude-sonnet-4-6",
}
for _k, _v in _TEST_ENV.items():
    os.environ.setdefault(_k, _v)

# 阻止启动时真实调用飞书 API
patch("backend.services.bitable_meta.load_multiselect_fields").start()
