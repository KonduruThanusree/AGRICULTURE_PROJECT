from flask import Blueprint, render_template, request, jsonify

from database.db import latest_readings

bp = Blueprint("soil", __name__)


@bp.route("/soil")
def soil_page():
    return render_template("soil.html")


@bp.route("/api/soil/analyze", methods=["POST"])
def soil_analyze():

    data = request.get_json(silent=True) or {}

    try:
        nitrogen = float(data.get("nitrogen", 0))
        phosphorus = float(data.get("phosphorus", 0))
        potassium = float(data.get("potassium", 0))
        ph = float(data.get("ph", 0))
        moisture = float(data.get("moisture", 0))

        if not all(map(lambda x: 0 <= x <= 200, [
            nitrogen, phosphorus, potassium, moisture
        ])):
            return jsonify({"error": "Invalid soil values"}), 400

        if not 0 <= ph <= 14:
            return jsonify({"error": "pH must be between 0 and 14"}), 400

        if ph < 5.5:
            health = "Acidic Soil"
        elif ph > 7.5:
            health = "Alkaline Soil"
        else:
            health = "Suitable pH Range"

        if moisture < 25:
            water = "Low soil moisture"
        elif moisture > 70:
            water = "High soil moisture"
        else:
            water = "Moderate soil moisture"

        if nitrogen < 50:
            nutrient = "Nitrogen is low"
        else:
            nutrient = "Nitrogen level is acceptable"

        return jsonify({
            "health": health,
            "moisture_status": water,
            "nutrient_status": nutrient,
            "recommendation": (
                "Consider a soil laboratory test before applying fertilizers."
            )
        })

    except (ValueError, TypeError):
        return jsonify({"error": "Please enter valid numeric values"}), 400