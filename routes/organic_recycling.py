from flask import Blueprint, render_template, request, jsonify

from models.recycling_model import calculate_recycling
from database.db import log_event

bp = Blueprint("recycling", __name__)

MATERIALS = {
    "dry_leaves": "Dry Leaves",
    "straw": "Straw",
    "sawdust": "Sawdust",
    "green_waste": "Green Waste",
    "food_waste": "Food Waste",
    "cow_dung": "Cow Dung"
}


@bp.route("/recycling")
def recycling_page():
    return render_template(
        "recycling.html",
        materials=MATERIALS
    )


@bp.route("/api/recycling/calculate", methods=["POST"])
def recycling_calculate():

    data = request.get_json(silent=True) or {}
    quantities = data.get("materials", {})

    if not isinstance(quantities, dict) or not quantities:
        return jsonify({"error": "Enter material quantities"}), 400

    try:
        materials = {}

        for key in MATERIALS:
            value = float(quantities.get(key, 0))

            if value < 0:
                return jsonify({
                    "error": "Quantities cannot be negative"
                }), 400

            materials[key] = value

        result = calculate_recycling(materials)

        if result["total_t"] <= 0:
            return jsonify({
                "error": "Enter at least one valid quantity"
            }), 400

        log_event(
            "recycling_logs",
            materials=str(materials),
            total_t=result["total_t"],
            blend_cn=result["blend_cn"],
            compost_t=result["compost_t"]
        )

        return jsonify(result)

    except (ValueError, TypeError):
        return jsonify({
            "error": "Please enter valid numeric quantities"
        }), 400