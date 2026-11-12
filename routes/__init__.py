import math

from flask import request

import config


class ValidationError(ValueError):
    """Raised for bad user input; app.py turns it into a JSON 400 response."""


def json_body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidationError("Send a JSON object as the request body")
    return data


def num(data, key, lo=None, hi=None, default=None):
    raw = data.get(key)
    if raw is None or raw == "":
        if default is None:
            raise ValidationError(f"'{key}' is required")
        return float(default)
    try:
        val = float(raw)
    except (TypeError, ValueError):
        raise ValidationError(f"'{key}' must be a number")
    if not math.isfinite(val):
        raise ValidationError(f"'{key}' must be a finite number")
    if (lo is not None and val < lo) or (hi is not None and val > hi):
        raise ValidationError(f"'{key}' must be between {lo} and {hi}")
    return val


def choice(data, key, options, default=None):
    val = str(data.get(key) or default or "").strip().lower()
    if val not in options:
        raise ValidationError(f"'{key}' must be one of: {', '.join(options)}")
    return val


def pick_field(data, key="field", default=None):
    """Return the canonical field name (case-insensitive match against config.FIELDS)."""
    raw = str(data.get(key) or default or "").strip().lower()
    for name in config.FIELDS:
        if name.lower() == raw:
            return name
    raise ValidationError(f"'{key}' must be one of: {', '.join(config.FIELDS)}")