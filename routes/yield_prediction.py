from flask import Blueprint, render_template, request, jsonify

from models.yield_model import predict_yield
from database.db import log_event

bp = Blueprint("yield_prediction", __name__)


@bp.route("/yield")
def yield_page():
    return render_template("yield.html")


@bp.route("/api/yield/predict", methods=["POST"])
def yield_predict():

    data = request.get_json(silent=True) or {}

    try:
        nitrogen = float(data.get("nitrogen", 0))
        phosphorus = float(data.get("phosphorus", 0))
        potassium = float(data.get("potassium", 0))
        ph = float(data.get("ph", 0))
        rainfall = float(data.get("rainfall", 0))
        area = float(data.get("area", 1))

        if not all(0 <= x <= 1000 for x in [
            nitrogen, phosphorus, potassium, rainfall
        ]):
            return jsonify({"error": "Invalid input values"}), 400

        if not 0 <= ph <= 14 or area <= 0:
            return jsonify({"error": "Invalid pH or area"}), 400

        prediction = predict_yield(
            nitrogen,
            phosphorus,
            potassium,
            ph,
            rainfall
        )

        total_yield = round(prediction * area, 2)

        log_event(
            "yield_logs",
            crop=data.get("crop", "rice"),
            area_ha=area,
            yield_t_ha=prediction,
            total_t=total_yield
        )

        return jsonify({
            "predicted_yield": prediction,
            "area": area,
            "total_yield": total_yield,
            "unit": "tonnes",
            "message": "Crop yield prediction completed successfully"
        })

    except (ValueError, TypeError):
        return jsonify({"error": "Please enter valid numeric values"}), 400