"""Smart irrigation recommendation model."""


def calculate_irrigation(moisture, temperature, humidity, crop, stage):

    water_required = {
        "rice": 30,
        "wheat": 20,
        "maize": 25,
        "cotton": 22,
        "sugarcane": 35
    }

    base_water = water_required.get(crop.lower(), 20)

    if moisture < 25:
        amount = base_water * 1.5
        irrigate = True
        status = "High water requirement"

    elif moisture < 40:
        amount = base_water
        irrigate = True
        status = "Moderate water requirement"

    else:
        amount = 0
        irrigate = False
        status = "Sufficient soil moisture"

    if temperature > 35 and humidity < 40 and irrigate:
        amount *= 1.2

    return {
        "irrigate": irrigate,
        "amount_mm": round(amount, 2),
        "status": status,
        "crop": crop,
        "stage": stage,
        "recommendation": (
            f"Apply approximately {round(amount, 2)} mm of water."
            if irrigate
            else "No irrigation is currently recommended."
        )
    }