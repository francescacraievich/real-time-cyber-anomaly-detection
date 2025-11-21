import pytest
import pandas as pd
import numpy as np

from feature_engineering.aggregation_functions import (
    calculate_total_events_processed,
    calculate_total_anomalous_events,
    calculate_total_unique_malicious_ips
)


class TestAggregateStatusMetrics:
    
    def test_calculate_total_events_processed(self):
        """test basic aggregation of total events per time window"""
        
        time_window = 60  # mins
        
        df = pd.DataFrame({
            'timestamp_start': pd.to_datetime([
                '2025-01-06 10:00:00',
                '2025-01-06 10:30:00',
                '2025-01-06 10:45:00',
                '2025-01-06 11:03:00'
            ])
        })
        
        result = calculate_total_events_processed(df, 'timestamp_start', time_window)
        
        # Check that the column was added
        assert 'events_in_window' in result.columns
        
        # First 3 events are in the 10:00-11:00 window
        assert result['events_in_window'].iloc[0] == 3
        assert result['events_in_window'].iloc[1] == 3
        assert result['events_in_window'].iloc[2] == 3
        
        # Last event is in the 11:00-12:00 window
        assert result['events_in_window'].iloc[3] == 1
        
        # Check that original dataframe length is preserved
        assert len(result) == len(df)
        
        
    def test_calculate_total_anomalous_events(self):
        """test basic aggregation of malicious events per time window"""
        
        time_window = 60  # mins
        
        df = pd.DataFrame({
            'timestamp_start': pd.to_datetime([
                '2025-01-06 10:00:00',
                '2025-01-06 10:30:00',
                '2025-01-06 10:45:00',
                '2025-01-06 11:03:00']),
            'label': ['malicious', 'malicious', 'benign', 'malicious']
        })
        
        result = calculate_total_anomalous_events(df, timestamp_col='timestamp_start', label_col='label', malicious_label='malicious', window_minutes=time_window)
        
        # Check that the column was added
        assert 'malicious_events_in_window' in result.columns
        assert 'label' in result.columns
        
        # First 3 events are in the 10:00-11:00 window and 2 are malicious
        assert result['malicious_events_in_window'].iloc[0] == 2
        assert result['malicious_events_in_window'].iloc[1] == 2
        assert result['malicious_events_in_window'].iloc[2] == 2
        
        # Last event is in the 11:00-12:00 window and 1 is malicious
        assert result['malicious_events_in_window'].iloc[3] == 1
        
        # Check that original dataframe length is preserved
        assert len(result) == len(df)
        

    def test_calculate_total_unique_malicious_ips(self):
        """test basic aggregation of malicious events per time window"""
        
        time_window = 60  # mins
        
        df = pd.DataFrame({
            'timestamp_start': pd.to_datetime([
                '2025-01-06 10:00:00',
                '2025-01-06 10:30:00',
                '2025-01-06 10:45:00',
                '2025-01-06 11:03:00']),
            'label': ['malicious', 'malicious', 'benign', 'malicious'],
            'source_ip' : ['192.168.1.10', '192.168.1.10', '192.168.1.0', '192.168.1.12']
        })
        
        result = calculate_total_unique_malicious_ips(df, timestamp_col='timestamp_start', source_ip_col='source_ip', label_col='label', malicious_label='malicious', window_minutes=time_window)
        
        # Check that the column was added
        assert 'unique_malicious_ips' in result.columns
        assert 'label' in result.columns
        assert 'source_ip' in result.columns
        
        # First 3 events are in the 10:00-11:00 window and 2 unique ips of malicious traffic
        assert result['unique_malicious_ips'].iloc[0] == 1
        assert result['unique_malicious_ips'].iloc[1] == 1
        assert result['unique_malicious_ips'].iloc[2] == 1
        
        # Last event is in the 11:00-12:00 window and 1 unique ip
        assert result['unique_malicious_ips'].iloc[3] == 1
        
        # Check that original dataframe length is preserved
        assert len(result) == len(df)