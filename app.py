from flask import Flask, render_template

from config import Config
from database.db import init_db

from routes.dashboard import bp as dashboard_bp
from routes.disease import bp as disease_bp
from routes.soil import bp as soil_bp
from routes.irrigation import bp as irrigation_bp
from routes.yield_prediction import bp as yield_prediction_bp
from routes.zoning import bp as zoning_bp
from routes.waste_management import bp as waste_bp
from routes.organic_recycling import bp as recycling_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    init_db()

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(disease_bp)
    app.register_blueprint(soil_bp)
    app.register_blueprint(irrigation_bp)
    app.register_blueprint(yield_prediction_bp)
    app.register_blueprint(zoning_bp)
    app.register_blueprint(waste_bp)
    app.register_blueprint(recycling_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)