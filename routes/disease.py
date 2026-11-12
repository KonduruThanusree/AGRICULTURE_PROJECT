from flask import Blueprint, render_template, request, jsonify
from models.disease_model import predict_disease
from database.db import log_event

bp = Blueprint("disease", __name__)


@bp.route("/disease")
def disease_page():
    return render_template("disease.html")


@bp.route("/api/disease/predict", methods=["POST"])
def disease_predict():
    if "image" not in request.files:
        return jsonify({"error": "Please upload an image"}), 400

    image = request.files["image"]

    if image.filename == "":
        return jsonify({"error": "No image selected"}), 400

    try:
        result = predict_disease(image)
        log_event(
            "disease_logs",
            filename=image.filename,
            disease=result["disease"],
            confidence=result["confidence"],
            severity=result["severity"]
        )
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 400