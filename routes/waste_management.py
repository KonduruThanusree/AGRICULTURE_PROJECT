from flask import Blueprint, render_template, request, jsonify

from models.waste_model import (
    recommend_waste_management,
    WASTE_TYPES
)
from database.db import log_event

bp = Blueprint("waste", __name__)


@bp.route("/waste")
def waste_page():
    return render_template(
        "waste.html",
        waste_types={
            key: value["label"]
            for key, value in WASTE_TYPES.items()
        }
    )


@bp.route("/api/waste/recommend", methods=["POST"])
def waste_recommend():

    data = request.get_json(silent=True) or {}

    waste_type = data.get("waste_type")
    quantity = data.get("quantity", 0)

    try:
        quantity = float(quantity)

        if quantity <= 0:
            return jsonify({"error": "Enter a valid quantity"}), 400

        result = recommend_waste_management(
            waste_type, quantity
        )

        log_event(
            "waste_logs",
            waste_type=waste_type,
            quantity_t=quantity,
            top_option=result["top_option"]
        )

        return jsonify(result)

    except (ValueError, TypeError, KeyError):
        return jsonify({
            "error": "Invalid waste type or quantity"
        }), 400