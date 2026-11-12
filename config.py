import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = "agrisense-secret-key"

DB_PATH = os.path.join(BASE_DIR, "database", "agrisense.db")

DEBUG = True

FIELDS = ["Field A", "Field B", "Field C"]

ALERT_THRESHOLDS = {
    "moisture_low": 30,
    "moisture_high": 80,
    "temp_high": 35,
    "ph_low": 5.5,
    "ph_high": 7.5,
    "ndvi_low": 0.3
}


class Config:
    SECRET_KEY = SECRET_KEY
    DEBUG = DEBUG
    DATABASE = DB_PATH