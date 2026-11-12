from flask import Blueprint, render_template, request, jsonify

from sklearn.cluster import KMeans
import numpy as np

from database.db import latest_readings

bp = Blueprint("zoning", __name__)


@bp.route("/zoning")
def zoning_page():
    return render_template("zoning.html")


@bp.route("/api/zoning/analyze", methods=["POST"])
def zoning_analyze():

    readings = latest_readings()

    if len(readings) < 2:
        return jsonify({"error": "Not enough field data"}), 400

    try:
        data = np.array([
            [
                float(r["moisture"]),
                float(r["ph"]),
                float(r["ndvi"])
            ]
            for r in readings
        ])

        model = KMeans(
            n_clusters=min(3, len(data)),
            random_state=42,
            n_init=10
        )

        labels = model.fit_predict(data)

        results = []

        for i, reading in enumerate(readings):
            results.append({
                "field": reading["field"],
                "zone": int(labels[i]) + 1,
                "moisture": reading["moisture"],
                "ph": reading["ph"],
                "ndvi": reading["ndvi"]
            })

        return jsonify({
            "message": "Field zoning completed",
            "zones": results
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400