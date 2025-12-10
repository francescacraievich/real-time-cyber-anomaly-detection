import pandas as pd
import numpy as np


def calculate_temporal_features(df, timestamp_col="timestamp_start"):
    """
    Calculate:
    - hour: Hour of day (0-23)
    - day_of_week: Day of week (0=Monday, 6=Sunday)
    - is_weekend: 1 if Saturday/Sunday, 0 otherwise
    - is_business_hours: 1 if weekday 9am-5pm, 0 otherwise
    """
    df = df.copy()

    # Ensure timestamp is datetime
    if not pd.api.types.is_datetime64_any_dtype(df[timestamp_col]):
        df[timestamp_col] = pd.to_datetime(df[timestamp_col])

    # Extract features
    df["hour"] = df[timestamp_col].dt.hour
    df["day_of_week"] = df[timestamp_col].dt.dayofweek
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    df["is_business_hours"] = (
        (df["hour"] >= 9) & (df["hour"] <= 17) & (df["is_weekend"] == 0)
    ).astype(int)

    return df
