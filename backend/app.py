"""Flask 应用入口。"""

from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from limits.storage import MemoryStorage
from backend.config import server
from backend.routes.submit import submit_bp
from backend.services.bitable_meta import load_multiselect_fields
from backend.logger import get_logger

logger = get_logger("app")

app = Flask(__name__)

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[server.rate_limit],
    headers_enabled=True,
    storage_uri="memory://",
)


@app.errorhandler(429)
def ratelimit_handler(e):
    logger.warning("RATE_LIMIT_EXCEEDED from %s", request.remote_addr)
    return jsonify({"success": False, "error": "RATE_LIMIT_EXCEEDED"}), 429


@app.before_request
def auth():
    if request.path.startswith("/api/"):
        if request.headers.get("x-api-key") != server.api_key:
            logger.warning("UNAUTHORIZED request from %s", request.remote_addr)
            return jsonify({"success": False, "error": "UNAUTHORIZED"}), 401


app.register_blueprint(submit_bp)

with app.app_context():
    try:
        load_multiselect_fields()
        from backend.services.bitable_meta import multiselect_fields
        logger.info("已加载多选字段: %s", list(multiselect_fields.keys()))
    except Exception as e:
        import traceback
        logger.error("加载多选字段失败: %s\n%s", e, traceback.format_exc())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=server.port)
