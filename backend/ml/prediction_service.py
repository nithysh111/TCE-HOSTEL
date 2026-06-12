"""Prediction service for food attendance forecasting."""

import os
import joblib
import numpy as np
from datetime import date


class FoodPredictionService:
    _instance = None
    _model_data = None

    def __new__(cls, model_path=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), 'food_prediction_model.joblib')
        if self._model_data is None and os.path.exists(model_path):
            self._model_data = joblib.load(model_path)
            self.model_path = model_path

    @property
    def is_loaded(self):
        return self._model_data is not None

    def predict(self, total_students, students_inside, students_outside,
                leave_requests, is_weekend=False, is_holiday=False):
        if not self.is_loaded:
            return self._fallback_predict(
                students_inside, is_weekend, is_holiday
            )

        features = np.array([[
            total_students, students_inside, students_outside,
            leave_requests, int(is_weekend), int(is_holiday)
        ]])

        predictions = self._model_data['model'].predict(features)[0]
        breakfast = max(0, int(round(predictions[0])))
        lunch = max(0, int(round(predictions[1])))
        dinner = max(0, int(round(predictions[2])))

        return {
            'predicted_breakfast': breakfast,
            'predicted_lunch': lunch,
            'predicted_dinner': dinner,
        }

    @staticmethod
    def _fallback_predict(students_inside, is_weekend, is_holiday):
        """Rule-based fallback when ML model is not trained yet."""
        factor = 1.0
        if is_weekend:
            factor = 0.6
        if is_holiday:
            factor = 0.4

        inside = int(students_inside * factor)
        return {
            'predicted_breakfast': int(inside * 0.65),
            'predicted_lunch': int(inside * 0.90),
            'predicted_dinner': int(inside * 0.82),
        }

    def get_metrics(self):
        if self._model_data and 'metrics' in self._model_data:
            return self._model_data['metrics']
        return None
