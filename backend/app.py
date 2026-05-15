"""Flask 应用入口。"""

from flask import Flask, jsonify, request
from backend.config import server
from backend.routes.submit import submit_bp
from backend.services.bitable_meta import load_multiselect_fields

app = Flask(__name__)


@app.before_request
def auth():
    if request.path.startswith("/api/"):
        if request.headers.get("x-api-key") != server.api_key:
            return jsonify({"success": False, "error": "UNAUTHORIZED"}), 401


app.register_blueprint(submit_bp)

with app.app_context():
    try:
        load_multiselect_fields()
        from backend.services.bitable_meta import multiselect_fields
        print(f"[startup] 已加载多选字段: {dict(multiselect_fields)}", flush=True)
    except Exception as e:
        import traceback
        print(f"[startup] 加载多选字段失败: {e}\n{traceback.format_exc()}", flush=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=server.port)
