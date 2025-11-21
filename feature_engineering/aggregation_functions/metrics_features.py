import pandas as pd
import numpy as np


def calculate_total_events_processed(df, timestamp_col='timestamp_start', window_minutes=60):
    """
    Calculate total events processed per time window
    """
    
    df = df.copy()
    
    # Create time window identifier (floor to nearest window)
    df['time_window'] = df[timestamp_col].dt.floor(f'{window_minutes}min')
    
    # Count events per window
    window_counts = df.groupby('time_window').size().reset_index(name='events_in_window')
    
    # Merge back to original dataframe
    df = df.merge(window_counts, on='time_window', how='left')
    
    # Drop temporary column
    df = df.drop(columns=['time_window'])
    
    return df


def calculate_total_anomalous_events(df, timestamp_col='timestamp_start', label_col='label', malicious_label='malicious', window_minutes=60):
    """
    Calculate total anomalous events per time window
    """
    
    df = df.copy()
    
    # Create time window identifier (floor to nearest window)
    df['time_window'] = df[timestamp_col].dt.floor(f'{window_minutes}min')
    
    # Count events per window
    malicious_df = df[df[label_col] == malicious_label]
    malicious_counts = malicious_df.groupby('time_window').size().reset_index(name='malicious_events_in_window')
    
    # Merge back to original dataframe
    df = df.merge(malicious_counts, on='time_window', how='left')
    
    # Drop temporary column
    df = df.drop(columns=['time_window'])
    
    return df
    