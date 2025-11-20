import pandas as pd
import numpy as np


def calculate_events_per_time_window(df, timestamp_col='timestamp_start', window_minutes=60):
    """
    Calculate total events processed per time window.
    
    Args:
        df: DataFrame with timestamp column
        timestamp_col: Name of the timestamp column (default: 'timestamp_start')
        window_minutes: Size of time window in minutes (default: 60 for 1 hour)
        
    Returns:
        DataFrame with added 'events_in_window' column showing count of events
        in the same time window as each row
        
    Example:
        >>> df = calculate_events_per_time_window(df, 'timestamp_start', window_minutes=60)
        >>> # Each row now has 'events_in_window' showing how many events occurred in that hour
    """
    df = df.copy()
    
    # Ensure timestamp is datetime
    if not pd.api.types.is_datetime64_any_dtype(df[timestamp_col]):
        df[timestamp_col] = pd.to_datetime(df[timestamp_col])
    
    # Create time window identifier (floor to nearest window)
    df['time_window'] = df[timestamp_col].dt.floor(f'{window_minutes}min')
    
    # Count events per window
    window_counts = df.groupby('time_window').size().reset_index(name='events_in_window')
    
    # Merge back to original dataframe
    df = df.merge(window_counts, on='time_window', how='left')
    
    # Drop temporary column
    df = df.drop(columns=['time_window'])
    
    return df