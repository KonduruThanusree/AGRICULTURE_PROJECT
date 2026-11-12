"""Agricultural waste management recommendation model."""

WASTE_TYPES = {
    "crop_residue": {
        "label": "Crop Residue",
        "options": [
            "Composting",
            "Biofuel Production",
            "Animal Feed"
        ]
    },
    "animal_waste": {
        "label": "Animal Waste",
        "options": [
            "Organic Manure",
            "Biogas Production",
            "Composting"
        ]
    },
    "plastic": {
        "label": "Agricultural Plastic",
        "options": [
            "Recycling",
            "Proper Waste Collection"
        ]
    },
    "food_waste": {
        "label": "Food Waste",
        "options": [
            "Composting",
            "Biogas Production"
        ]
    },
    "leaves": {
        "label": "Dry Leaves",
        "options": [
            "Composting",
            "Mulching"
        ]
    }
}


def recommend_waste_management(waste_type, quantity):

    if waste_type not in WASTE_TYPES:
        raise ValueError("Invalid waste type")

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero")

    waste = WASTE_TYPES[waste_type]

    options = waste["options"]

    recommendation = options[0]

    return {
        "waste_type": waste["label"],
        "quantity_t": round(quantity, 2),
        "top_option": recommendation,
        "other_options": options[1:],
        "message": (
            f"{recommendation} is a suggested method "
            f"for managing {quantity} tonnes of {waste['label']}."
        )
    }