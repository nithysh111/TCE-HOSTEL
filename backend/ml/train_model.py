"""Model training pipeline for food prediction using Random Forest Regressor."""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from generate_dataset import generate_synthetic_dataset

FEATURE_COLUMNS = [
    'total_students', 'students_inside', 'students_outside',
    'leave_requests', 'is_weekend', 'is_holiday'
]
TARGET_COLUMNS = ['breakfast_count', 'lunch_count', 'dinner_count']


def train_and_evaluate(df=None, save_path=None):
    if df is None:
        df = generate_synthetic_dataset(num_days=730, total_students=500)

    X = df[FEATURE_COLUMNS].values
    y = df[TARGET_COLUMNS].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    base_model = RandomForestRegressor(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    model = MultiOutputRegressor(base_model)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    metrics = {}
    for i, target in enumerate(TARGET_COLUMNS):
        mae = mean_absolute_error(y_test[:, i], y_pred[:, i])
        rmse = np.sqrt(mean_squared_error(y_test[:, i], y_pred[:, i]))
        r2 = r2_score(y_test[:, i], y_pred[:, i])
        metrics[target] = {'mae': round(mae, 2), 'rmse': round(rmse, 2), 'r2': round(r2, 4)}

    if save_path is None:
        save_path = os.path.join(os.path.dirname(__file__), 'food_prediction_model.joblib')

    joblib.dump({
        'model': model,
        'feature_columns': FEATURE_COLUMNS,
        'target_columns': TARGET_COLUMNS,
        'metrics': metrics,
    }, save_path)

    print('Model Evaluation Metrics:')
    for target, m in metrics.items():
        print(f'  {target}: MAE={m["mae"]}, RMSE={m["rmse"]}, R²={m["r2"]}')
    print(f'Model saved to {save_path}')

    return model, metrics


if __name__ == '__main__':
    train_and_evaluate()
