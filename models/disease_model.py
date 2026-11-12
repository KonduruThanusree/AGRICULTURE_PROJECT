"""Demo plant disease detection model."""

import numpy as np
from PIL import Image


def predict_disease(image):
    img = Image.open(image).convert("RGB")
    img = img.resize((100, 100))

    pixels = np.array(img)
    green = np.mean(pixels[:, :, 1])
    red = np.mean(pixels[:, :, 0])

    if green > red:
        disease = "Healthy Plant"
        severity = "Low"
        confidence = 90.0
    else:
        disease = "Possible Leaf Disease"
        severity = "Medium"
        confidence = 75.0

    return {
        "disease": disease,
        "severity": severity,
        "confidence": confidence,
        "recommendation": (
            "Plant appears healthy."
            if disease == "Healthy Plant"
            else "Inspect the plant and consult an agricultural expert."
        )
    }