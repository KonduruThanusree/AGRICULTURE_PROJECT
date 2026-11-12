"""Crop yield prediction model."""

import numpy as np
from sklearn.ensemble import RandomForestRegressor


class YieldModel:

    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            random_state=42
        )

        self.model.fit(
            np.array([
                [100, 40, 30, 6.5, 25],
                [80, 30, 20, 6.0, 20],
                [120, 50, 40, 7.0, 30],
                [60, 20, 15, 5.5, 18],
                [110, 45, 35, 6.8, 28],
                [90, 35, 25, 6.2, 22]
            ]),
            [5.5, 4.0, 6.5, 3.0, 6.0, 4.8]
        )

    def predict(self, nitrogen, phosphorus, potassium, ph, rainfall):
        values = np.array([[
            nitrogen,
            phosphorus,
            potassium,
            ph,
            rainfall
        ]])

        return round(float(self.model.predict(values)[0]), 2)


yield_model = YieldModel()


def predict_yield(nitrogen, phosphorus, potassium, ph, rainfall):
    return yield_model.predict(
        nitrogen, phosphorus, potassium, ph, rainfall
    )