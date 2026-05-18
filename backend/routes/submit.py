"""POST /api/submit 路由。"""

from flask import Blueprint, request, jsonify
from backend.utils.format_record import format_task_detail
from backend.services.bitable import create_record
from backend.services.feishu_user import get_open_id_by_email
from backend.services.bedrock import generate_fields
from backend.services.bitable_meta import multiselect_fields
from backend.logger import get_logger

logger = get_logger("submit")

submit_bp = Blueprint("submit", __name__)

REQUIRED_FIELDS = ["creatorEmail", "customerType", "userIssue", "issueCause"]


@submit_bp.post("/api/submit")
def submit():
    body = request.get_json(silent=True) or {}

    missing = [f for f in REQUIRED_FIELDS if not str(body.get(f, "")).strip()]
    if missing:
        logger.warning("VALIDATION_ERROR from %s, missing fields: %s", request.remote_addr, missing)
        return jsonify({"success": False, "error": "VALIDATION_ERROR", "fields": missing}), 400

    try:
        open_id = get_open_id_by_email(body["creatorEmail"])
    except RuntimeError as e:
        err = str(e)
        if "USER_NOT_FOUND" in err:
            logger.warning("USER_NOT_FOUND for email: %s", body["creatorEmail"])
            return jsonify({"success": False, "error": err}), 400
        logger.error("feishu_user error: %s", err)
        return jsonify({"success": False, "error": err}), 502

    task_detail = format_task_detail(body["customerName"], body["userIssue"], body["issueCause"])

    try:
        generated = generate_fields(body["userIssue"], body["issueCause"], multiselect_fields)
        logger.info("Bedrock generated fields for customer: %s", body.get("customerName", ""))
    except Exception as e:
        import traceback
        logger.error("generate_fields failed: %s\n%s", e, traceback.format_exc())
        generated = {}

    fields = {
        "创建人": [{"id": open_id}],
        "客户类型": [body["customerType"]] if body.get("customerType") else [],
        "任务详情描述": task_detail,
        "任务名称": generated.get("task_name", ""),
        "根因分析/知识点摘要": generated.get("root_cause", ""),
        "解决步骤": generated.get("solution_steps", ""),
        "Q&A提取": generated.get("qa", ""),
    }

    for field_name, selected in (generated.get("multiselect") or {}).items():
        if field_name in multiselect_fields and selected:
            valid = [s for s in selected if s in multiselect_fields[field_name]]
            if valid:
                fields[field_name] = valid

    try:
        record_id = create_record(fields)
        logger.info(
            "Record created: %s | customer: %s | creator: %s | issue: %s | cause: %s",
            record_id,
            body.get("customerName", ""),
            body.get("creatorEmail", ""),
            body.get("userIssue", ""),
            body.get("issueCause", ""),
        )
    except RuntimeError as e:
        err = str(e)
        if "AUTH_ERROR" in err or "FEISHU_API_ERROR" in err:
            logger.error("bitable create_record error: %s", err)
            return jsonify({"success": False, "error": err}), 502
        logger.error("bitable create_record unexpected error: %s", err)
        return jsonify({"success": False, "error": "INTERNAL_ERROR"}), 500

    return jsonify({"success": True, "recordId": record_id}), 200
