import pytest
import pandas as pd
import numpy as np

from feature_engineering.aggregation_functions import (
    calculate_total_events_processed,
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