"""Synthetic dataset generator for food prediction ML model."""

import numpy as np
import pandas as pd
from datetime import date, timedelta


def generate_synthetic_dataset(num_days=365, total_students=500, seed=42):
    """
    Generate synthetic historical data for food attendance prediction.
    Features correlate with realistic hostel dining patterns.
    """
    np.random.seed(seed)
    records = []
    start_date = date.today() - timedelta(days=num_days)

    for day_offset in range(num_days):
        current_date = start_date + timedelta(days=day_offset)
        is_weekend = current_date.weekday() >= 5
        is_holiday = np.random.random() < 0.03  # ~3% holidays

        leave_requests = int(np.random.poisson(15 if not is_weekend else 8))
        leave_requests = min(leave_requests, int(total_students * 0.3))

        base_inside = total_students - leave_requests
        if is_weekend:
            base_inside = int(base_inside * np.random.uniform(0.4, 0.65))
        elif is_holiday:
            base_inside = int(base_inside * np.random.uniform(0.2, 0.4))
        else:
            base_inside = int(base_inside * np.random.uniform(0.75, 0.95))

        students_inside = max(0, min(base_inside, total_students))
        students_outside = max(0, total_students - students_inside - leave_requests)
        students_on_leave = leave_requests

        # Breakfast: lower attendance, especially weekdays
        breakfast_factor = 0.55 if is_weekend else 0.70
        if is_holiday:
            breakfast_factor *= 0.6
        breakfast = int(students_inside * breakfast_factor * np.random.uniform(0.9, 1.1))
        breakfast = max(0, min(breakfast, students_inside))

        # Lunch: highest attendance
        lunch_factor = 0.85 if is_weekend else 0.92
        if is_holiday:
            lunch_factor *= 0.75
        lunch = int(students_inside * lunch_factor * np.random.uniform(0.92, 1.08))
        lunch = max(breakfast, min(lunch, students_inside))

        # Dinner: moderate-high attendance
        dinner_factor = 0.80 if is_weekend else 0.88
        if is_holiday:
            dinner_factor *= 0.70
        dinner = int(students_inside * dinner_factor * np.random.uniform(0.9, 1.1))
        dinner = max(lunch * 0.85, min(dinner, students_inside))

        records.append({
            'date': current_date.isoformat(),
            'total_students': total_students,
            'students_inside': students_inside,
            'students_outside': students_outside,
            'leave_requests': students_on_leave,
            'is_weekend': int(is_weekend),
            'is_holiday': int(is_holiday),
            'breakfast_count': breakfast,
            'lunch_count': lunch,
            'dinner_count': dinner,
        })

    return pd.DataFrame(records)


if __name__ == '__main__':
    df = generate_synthetic_dataset()
    output_path = 'ml/synthetic_food_data.csv'
    df.to_csv(output_path, index=False)
    print(f'Generated {len(df)} records -> {output_path}')
    print(df.describe())
