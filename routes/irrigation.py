from flask import Blueprint, render_template, request, jsonify

from models.irrigation_model import calculate_irrigation
from database.db import log_event

bp = Blueprint("irrigation", __name__)


@bp.route("/irrigation")
def irrigation_page():
    return render_template("irrigation.html")


@bp.route("/api/irrigation/calculate", methods=["POST"])
def irrigation_calculate():

    data = request.get_json(silent=True) or {}

    try:
        crop = data.get("crop", "").lower()
        stage = data.get("stage", "")

        moisture = float(data.get("moisture", 0))
        temperature = float(data.get("temperature", 0))
        humidity = float(data.get("humidity", 0))
        rain = float(data.get("rain_forecast", 0))
        area = float(data.get("area_ha", 0))
        field = data.get("field", "")

        if not crop or not stage or not field:
            return jsonify({"error": "Please select all options"}), 400

        if not 0 <= moisture <= 100:
            return jsonify({"error": "Invalid soil moisture"}), 400

        if not 0 <= humidity <= 100:
            return jsonify({"error": "Invalid humidity"}), 400

        if temperature < 0 or rain < 0 or area <= 0:
            return jsonify({"error": "Enter valid numerical values"}), 400

        result = calculate_irrigation(
            moisture,
            temperature,
            humidity,
            crop,
            stage
        )

        # Adjust water requirement using rain forecast
        amount = max(0, result["amount_mm"] - rain)

        irrigate = amount > 0

        volume = round(amount * area * 10000, 2)

        if irrigate:
            recommendation = (
                f"Apply approximately {amount} mm of water "
                f"to {area} hectares."
            )
            best_time = "Early morning or late evening"
            reason = result["status"]
        else:
            recommendation = "No additional irrigation is required currently."
            best_time = "Not required"
            reason = "Rainfall and soil moisture are sufficient."

        output = {
            "irrigate": irrigate,
            "amount_mm": round(amount, 2),
            "volume_litres": volume,
            "best_time": best_time,
            "reason": reason,
            "recommendation": recommendation,
            "crop": crop,
            "stage": stage,
            "field": field
        }

        log_event(
            "irrigation_logs",
            field=field,
            crop=crop,
            irrigate=int(irrigate),
            amount_mm=round(amount, 2)
        )

        return jsonify(output)

    except (ValueError, TypeError):
        return jsonify({"error": "Please enter valid values"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500