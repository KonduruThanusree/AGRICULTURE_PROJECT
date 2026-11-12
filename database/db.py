"""SQLite helpers: schema, seeding, and small query functions."""

import math
import random
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta

import config

TS_FORMAT = "%Y-%m-%d %H:%M:%S"

LOG_TABLES = {
    "disease_logs",
    "irrigation_logs",
    "yield_logs",
    "waste_logs",
    "recycling_logs"
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS sensor_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    field TEXT NOT NULL,
    ts TEXT NOT NULL,
    moisture REAL,
    temperature REAL,
    humidity REAL,
    ph REAL,
    nitrogen REAL,
    phosphorus REAL,
    potassium REAL,
    ndvi REAL
);

CREATE TABLE IF NOT EXISTS disease_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT,
    filename TEXT,
    disease TEXT,
    confidence REAL,
    severity TEXT
);

CREATE TABLE IF NOT EXISTS irrigation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT,
    field TEXT,
    crop TEXT,
    irrigate INTEGER,
    amount_mm REAL
);

CREATE TABLE IF NOT EXISTS yield_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT,
    crop TEXT,
    area_ha REAL,
    yield_t_ha REAL,
    total_t REAL
);

CREATE TABLE IF NOT EXISTS waste_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT,
    waste_type TEXT,
    quantity_t REAL,
    top_option TEXT
);

CREATE TABLE IF NOT EXISTS recycling_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT,
    materials TEXT,
    total_t REAL,
    blend_cn REAL,
    compost_t REAL
);

CREATE INDEX IF NOT EXISTS idx_readings_field
ON sensor_readings(field, id);
"""

SENSOR_COLUMNS = [
    "moisture", "temperature", "humidity", "ph",
    "nitrogen", "phosphorus", "potassium", "ndvi"
]


@contextmanager
def get_conn():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def now_str():
    return datetime.now().strftime(TS_FORMAT)


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)

        empty = conn.execute(
            "SELECT COUNT(*) FROM sensor_readings"
        ).fetchone()[0] == 0

    if empty:
        seed_demo_data()


def seed_demo_data():
    rng = random.Random(42)

    base = {
        "Field A": dict(ph=6.6, n=110, p=24, k=130, ndvi=0.74, m=46),
        "Field B": dict(ph=6.2, n=85, p=18, k=95, ndvi=0.66, m=38),
        "Field C": dict(ph=7.1, n=60, p=14, k=80, ndvi=0.55, m=30),
        "Field D": dict(ph=5.5, n=45, p=10, k=70, ndvi=0.38, m=22),
    }

    start = datetime.now() - timedelta(hours=23)
    rows = []

    for field in config.FIELDS:
        b = base.get(field, base["Field A"])

        for i in range(24):
            t = start + timedelta(hours=i)

            temp = (
                27 + 6 * math.sin((t.hour - 9) / 24 * 2 * math.pi)
                + rng.uniform(-0.6, 0.6)
            )

            hum = max(
                25,
                min(95, 85 - (temp - 22) * 2.2 + rng.uniform(-3, 3))
            )

            moist = max(
                8, b["m"] - i * 0.25 + rng.uniform(-0.8, 0.8)
            )

            rows.append((
                field,
                t.strftime(TS_FORMAT),
                round(moist, 1),
                round(temp, 1),
                round(hum, 1),
                round(b["ph"] + rng.uniform(-0.05, 0.05), 2),
                round(b["n"] + rng.uniform(-2, 2), 1),
                round(b["p"] + rng.uniform(-0.5, 0.5), 1),
                round(b["k"] + rng.uniform(-3, 3), 1),
                round(max(0.05, b["ndvi"] + rng.uniform(-0.01, 0.01)), 2)
            ))

    with get_conn() as conn:
        conn.executemany(
            """INSERT INTO sensor_readings
            (field, ts, moisture, temperature, humidity, ph,
             nitrogen, phosphorus, potassium, ndvi)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            rows
        )


def insert_reading(field, values):
    cols = ["field", "ts"] + SENSOR_COLUMNS
    data = [field, now_str()] + [
        values[c] for c in SENSOR_COLUMNS
    ]

    with get_conn() as conn:
        conn.execute(
            f"INSERT INTO sensor_readings ({','.join(cols)}) "
            f"VALUES ({','.join('?' * len(cols))})",
            data
        )

    return dict(zip(cols, data))


def latest_readings():
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT * FROM sensor_readings
            WHERE id IN (
                SELECT MAX(id)
                FROM sensor_readings
                GROUP BY field
            )
            ORDER BY field"""
        ).fetchall()

    return [dict(r) for r in rows]


def reading_history(field, limit=24):
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT * FROM sensor_readings
            WHERE field=?
            ORDER BY id DESC LIMIT ?""",
            (field, limit)
        ).fetchall()

    return [dict(r) for r in reversed(rows)]


def simulate_reading(field):
    latest = next(
        (r for r in latest_readings() if r["field"] == field),
        None
    )

    if latest is None:
        latest = dict(
            moisture=35,
            temperature=28,
            humidity=60,
            ph=6.5,
            nitrogen=80,
            phosphorus=18,
            potassium=100,
            ndvi=0.6
        )

    new = {
        "moisture": round(
            min(80, max(5, latest["moisture"] + random.uniform(-2.5, 1.2))), 1
        ),
        "temperature": round(
            min(45, max(5, latest["temperature"] + random.uniform(-1, 1))), 1
        ),
        "humidity": round(
            min(98, max(15, latest["humidity"] + random.uniform(-4, 4))), 1
        ),
        "ph": round(latest["ph"] + random.uniform(-0.03, 0.03), 2),
        "nitrogen": round(
            max(0, latest["nitrogen"] + random.uniform(-1.5, 0.5)), 1
        ),
        "phosphorus": round(
            max(0, latest["phosphorus"] + random.uniform(-0.3, 0.2)), 1
        ),
        "potassium": round(
            max(0, latest["potassium"] + random.uniform(-1.5, 0.5)), 1
        ),
        "ndvi": round(
            min(0.95, max(0.05, latest["ndvi"] + random.uniform(-0.015, 0.012))), 2
        ),
    }

    return insert_reading(field, new)


def log_event(table, **values):
    if table not in LOG_TABLES:
        raise ValueError("unknown log table")

    values["ts"] = now_str()
    cols = ",".join(values)

    with get_conn() as conn:
        conn.execute(
            f"INSERT INTO {table} ({cols}) "
            f"VALUES ({','.join('?' * len(values))})",
            list(values.values())
        )


def count_rows(table):
    if table not in LOG_TABLES | {"sensor_readings"}:
        raise ValueError("unknown table")

    with get_conn() as conn:
        return conn.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]


def recent_rows(table, limit=5):
    if table not in LOG_TABLES:
        raise ValueError("unknown table")

    with get_conn() as conn:
        rows = conn.execute(
            f"SELECT * FROM {table} ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()

    return [dict(r) for r in rows]