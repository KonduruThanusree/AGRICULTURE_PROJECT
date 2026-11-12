"""Organic waste recycling and compost estimation model."""


def calculate_recycling(materials):
    carbon = {
        "dry_leaves": 60,
        "straw": 80,
        "sawdust": 100,
        "green_waste": 20,
        "food_waste": 15,
        "cow_dung": 15
    }

    nitrogen = {
        "dry_leaves": 1,
        "straw": 1,
        "sawdust": 0.5,
        "green_waste": 2,
        "food_waste": 2,
        "cow_dung": 1.5
    }

    total_carbon = 0
    total_nitrogen = 0
    total_weight = 0

    for material, quantity in materials.items():
        if material not in carbon:
            continue

        quantity = max(0, float(quantity))

        total_weight += quantity
        total_carbon += carbon[material] * quantity
        total_nitrogen += nitrogen[material] * quantity

    if total_nitrogen == 0:
        ratio = 0
    else:
        ratio = total_carbon / total_nitrogen

    compost = round(total_weight * 0.4, 2)

    if ratio < 20:
        recommendation = "Add dry leaves or straw to balance the mixture."
    elif ratio > 35:
        recommendation = "Add green waste or cow dung to balance the mixture."
    else:
        recommendation = "The mixture has a suitable estimated carbon-nitrogen balance."

    return {
        "total_t": round(total_weight, 2),
        "blend_cn": round(ratio, 2),
        "compost_t": compost,
        "recommendation": recommendation
    }