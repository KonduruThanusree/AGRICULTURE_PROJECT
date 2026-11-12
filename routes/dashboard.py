import config
from database.db import (SENSOR_COLUMNS, count_rows, insert_reading, latest_readings,
                         reading_history, simulate_reading)
from routes import choice, json_body, num, pick_field
from flask import Blueprint, render_template, jsonify,request

bp = Blueprint("dashboard", __name__)

SENSOR_RANGES = {"moisture": (0, 100), "temperature": (-10, 60), "humidity": (0, 100),
                 "ph": (3, 10), "nitrogen": (0, 500), "phosphorus": (0, 200),
                 "potassium": (0, 600), "ndvi": (-0.2, 1.0)}


def build_alerts(readings):
    t, alerts = config.ALERT_THRESHOLDS, []

    def add(field, level, msg):
        alerts.append({"field": field, "level": level, "message": msg})

    for r in readings:
        f = r["field"]
        if r["moisture"] < t["moisture_low"]:
            add(f, "High", f"Soil moisture low ({r['moisture']:.1f}%) - irrigation needed")
        elif r["moisture"] > t["moisture_high"]:
            add(f, "Medium", f"Soil moisture very high ({r['moisture']:.1f}%) - check drainage")
        if r["temperature"] > t["temp_high"]:
            add(f, "Medium", f"Heat stress risk ({r['temperature']:.0f} C)")
        if not t["ph_low"] <= r["ph"] <= t["ph_high"]:
            add(f, "Medium", f"Soil pH out of range ({r['ph']:.1f})")
        if r["ndvi"] < t["ndvi_low"]:
            add(f, "High", f"Low crop vigour (NDVI {r['ndvi']:.2f}) - scout the field")
    order = {"High": 0, "Medium": 1, "Low": 2}
    return sorted(alerts, key=lambda a: order[a["level"]])


@bp.route("/dashboard")
def page():
    return render_template("dashboard.html")


@bp.route("/api/dashboard/summary")
def summary():
    readings = latest_readings()
    n = max(len(readings), 1)
    alerts = build_alerts(readings)
    return jsonify({
        "fields": readings,
        "alerts": alerts,
        "stats": {
            "fields": len(readings),
            "avg_moisture": round(sum(r["moisture"] for r in readings) / n, 1),
            "avg_temperature": round(sum(r["temperature"] for r in readings) / n, 1),
            "avg_ndvi": round(sum(r["ndvi"] for r in readings) / n, 2),
            "alerts": len(alerts),
            "disease_scans": count_rows("disease_logs"),
            "irrigation_runs": count_rows("irrigation_logs"),
            "yield_forecasts": count_rows("yield_logs"),
            "waste_records": count_rows("waste_logs"),
            "recycling_plans": count_rows("recycling_logs"),
        },
    })


@bp.route("/api/dashboard/history")
def history():
    field = pick_field(request.args, "field", config.FIELDS[0])
    rows = reading_history(field, limit=int(num(request.args, "limit", 1, 200, 24)))
    return jsonify({
        "field": field,
        "labels": [r["ts"][11:16] for r in rows],
        "moisture": [r["moisture"] for r in rows],
        "temperature": [r["temperature"] for r in rows],
        "ndvi": [r["ndvi"] for r in rows],
    })


@bp.route("/api/sensors", methods=["POST"])
def ingest():
    """IoT gateways POST JSON here: {"field": "Field A", "moisture": 31.2, ...}"""
    data = json_body()
    field = pick_field(data)
    values = {c: num(data, c, *SENSOR_RANGES[c]) for c in SENSOR_COLUMNS}
    return jsonify(insert_reading(field, values)), 201


@bp.route("/api/sensors/simulate", methods=["POST"])
def simulate():
    """Demo helper: generate a new drifting reading for every field (or one field)."""
    data = request.get_json(silent=True) or {}
    fields = config.FIELDS
    if data.get("field"):
        fields = [pick_field(data)]
    return jsonify({"created": [simulate_reading(f) for f in fields]}), 201