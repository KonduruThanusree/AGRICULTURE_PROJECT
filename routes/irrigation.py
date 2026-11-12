from flask import Blueprint, render_template, request, jsonify

from models.irrigation_model import calculate_irrigation
from database.db import latest_readings, log_event

bp = Blueprint("irrigation", __name__)


@bp.route("/irrigation")
def irrigation_page():
    return render_template("irrigation.html")


@bp.route("/api/irrigation/calculate", methods=["POST"])
def irrigation_calculate():
    data = request.get_json(silent=True) or {}

    field = data.get("field", "Field A")
    crop = data.get("crop", "rice")
    stage = data.get("stage", "mid")

    readings = next(
        (r for r in latest_readings() if r["field"] == field),
        None
    )

    if readings is None:
        return jsonify({"error": "Field not found"}), 400

    result = calculate_irrigation(
        readings["moisture"],
        readings["temperature"],
        readings["humidity"],
        crop,
        stage
    )

    log_event(
        "irrigation_logs",
        field=field,
        crop=crop,
        irrigate=int(result["irrigate"]),
        amount_mm=result["amount_mm"]
    )

    return jsonify(result)
