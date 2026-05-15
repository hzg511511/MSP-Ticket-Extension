"""
后端配置模块：使用 python-dotenv 读取环境变量，导出 feishu 和 server 配置对象。
若必需环境变量缺失，启动时抛出明确错误。
"""

import os
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# 加载 .env 文件（若存在）
load_dotenv()


@dataclass
class FeishuConfig:
    app_id: str       # 飞书应用 App ID（环境变量 FEISHU_APP_ID）
    app_secret: str   # 飞书应用 App Secret（环境变量 FEISHU_APP_SECRET）
    app_token: str    # 多维表格 App Token（环境变量 FEISHU_APP_TOKEN）
    table_id: str     # 数据表 ID（环境变量 FEISHU_TABLE_ID）


@dataclass
class BedrockConfig:
    region: str       # AWS Region（环境变量 AWS_REGION）
    model_id: str     # Bedrock 模型 ID（环境变量 BEDROCK_MODEL_ID）
    api_key: str      # Bedrock API Key（环境变量 BEDROCK_API_KEY）


@dataclass
class ServerConfig:
    port: int         # 服务端口，默认 5000
    api_key: str      # 插件请求鉴权 Key（环境变量 API_KEY）


def _require_env(name: str) -> str:
    """读取必需环境变量，若缺失则抛出明确错误。"""
    value = os.environ.get(name)
    if not value:
        raise EnvironmentError(
            f"必需的环境变量 '{name}' 未设置或为空。"
            f"请参考 .env.example 文件配置环境变量。"
        )
    return value


def _parse_bitable_url(url: str) -> tuple[str, str]:
    parsed = urlparse(url)
    app_token = parsed.path.rstrip("/").split("/")[-1]
    table_id = parse_qs(parsed.query).get("table", [None])[0]
    if not app_token or not table_id:
        raise EnvironmentError("FEISHU_BITABLE_URL 格式无效，无法解析 app_token 或 table_id")
    return app_token, table_id


def _load_feishu_config() -> FeishuConfig:
    app_id = _require_env("FEISHU_APP_ID")
    app_secret = _require_env("FEISHU_APP_SECRET")
    bitable_url = _require_env("FEISHU_BITABLE_URL")
    app_token, table_id = _parse_bitable_url(bitable_url)
    return FeishuConfig(app_id=app_id, app_secret=app_secret, app_token=app_token, table_id=table_id)


def _load_server_config() -> ServerConfig:
    api_key = _require_env("API_KEY")
    port_str = os.environ.get("PORT", "5000")
    try:
        port = int(port_str)
    except ValueError:
        raise EnvironmentError(
            f"环境变量 'PORT' 的值 '{port_str}' 不是有效的整数。"
        )
    return ServerConfig(port=port, api_key=api_key)


def _load_bedrock_config() -> BedrockConfig:
    return BedrockConfig(
        region=_require_env("AWS_REGION"),
        model_id=_require_env("BEDROCK_MODEL_ID"),
        api_key=_require_env("BEDROCK_API_KEY"),
    )


# 模块级配置对象，导入时立即加载并校验
feishu: FeishuConfig = _load_feishu_config()
server: ServerConfig = _load_server_config()
bedrock: BedrockConfig = _load_bedrock_config()
