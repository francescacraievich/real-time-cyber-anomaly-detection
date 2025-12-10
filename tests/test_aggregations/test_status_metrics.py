import numpy as np
import pandas as pd
import pytest
from src.feature_engineering.aggregation_functions import (
    calculate_total_anomalous_events, calculate_total_events_for_dst_ports,
    calculate_total_events_processed,
    calculate_total_malicious_events_per_protocol,
    calculate_total_unique_malicious_ips, calculate_trend_percentage_change)


class TestAggregateStatusMetrics:

    def test_calculate_total_events_processed(self):
        """test basic aggregation of total events per time window"""

        time_window = 60  # mins

        df = pd.DataFrame(
            {
                "timestamp_start": pd.to_datetime(
                    [
                        "2025-01-06 10:00:00",
                        "2025-01-06 10:30:00",
                        "2025-01-06 10:45:00",
                        "2025-01-06 11:03:00",
                    ]
                )
            }
        )

        result = calculate_total_events_processed(df, "timestamp_start", time_window)

        # Check that the column was added
        assert "events_in_window" in result.columns

        # First 3 events are in the 10:00-11:00 window
        assert result["events_in_window"].iloc[0] == 3
        assert result["events_in_window"].iloc[1] == 3
        assert result["events_in_window"].iloc[2] == 3

        # Last event is in the 11:00-12:00 window
        assert result["events_in_window"].iloc[3] == 1

        # Check that original dataframe length is preserved
        assert len(result) == len(df)

    def test_calculate_total_anomalous_events(self):
        """test basic aggregation of malicious events per time window"""

        time_window = 60  # mins

        df = pd.DataFrame(
            {
                "timestamp_start": pd.to_datetime(
                    [
                        "2025-01-06 10:00:00",
                        "2025-01-06 10:30:00",
                        "2025-01-06 10:45:00",
                        "2025-01-06 11:03:00",
                    ]
                ),
                "label": ["malicious", "malicious", "benign", "malicious"],
            }
        )

        result = calculate_total_anomalous_events(
            df,
            timestamp_col="timestamp_start",
            label_col="label",
            malicious_label="malicious",
            window_minutes=time_window,
        )

        # Check that the column was added
        assert "malicious_events_in_window" in result.columns
        assert "label" in result.columns

        # First 3 events are in the 10:00-11:00 window and 2 are malicious
        assert result["malicious_events_in_window"].iloc[0] == 2
        assert result["malicious_events_in_window"].iloc[1] == 2
        assert result["malicious_events_in_window"].iloc[2] == 2

        # Last event is in the 11:00-12:00 window and 1 is malicious
        assert result["malicious_events_in_window"].iloc[3] == 1

        # Check that original dataframe length is preserved
        assert len(result) == len(df)

    def test_calculate_total_unique_malicious_ips(self):
        """test basic aggregation of malicious events per time window"""

        time_window = 60  # mins

        df = pd.DataFrame(
            {
                "timestamp_start": pd.to_datetime(
                    [
                        "2025-01-06 10:00:00",
                        "2025-01-06 10:30:00",
                        "2025-01-06 10:45:00",
                        "2025-01-06 11:03:00",
                    ]
                ),
                "label": ["malicious", "malicious", "benign", "malicious"],
                "source_ip": [
                    "192.168.1.10",
                    "192.168.1.10",
                    "192.168.1.0",
                    "192.168.1.12",
                ],
            }
        )

        result = calculate_total_unique_malicious_ips(
            df,
            timestamp_col="timestamp_start",
            source_ip_col="source_ip",
            label_col="label",
            malicious_label="malicious",
            window_minutes=time_window,
        )

        # Check that the column was added
        assert "unique_malicious_ips" in result.columns
        assert "label" in result.columns
        assert "source_ip" in result.columns

        # First 3 events are in the 10:00-11:00 window and 2 unique ips of malicious traffic
        assert result["unique_malicious_ips"].iloc[0] == 1
        assert result["unique_malicious_ips"].iloc[1] == 1
        assert result["unique_malicious_ips"].iloc[2] == 1

        # Last event is in the 11:00-12:00 window and 1 unique ip
        assert result["unique_malicious_ips"].iloc[3] == 1

        # Check that original dataframe length is preserved
        assert len(result) == len(df)

    def test_calculate_trend_percentage_change(self):
        """test percentage change calculation between time windows"""

        time_window = 60  # mins

        df = pd.DataFrame(
            {
                "timestamp_start": pd.to_datetime(
                    [
                        "2025-01-06 10:00:00",
                        "2025-01-06 10:30:00",  # Window 1: 2 events
                        "2025-01-06 11:00:00",
                        "2025-01-06 11:30:00",  # Window 2: 2 events (0% change)
                        "2025-01-06 12:00:00",
                        "2025-01-06 12:10:00",
                        "2025-01-06 12:20:00",
                        "2025-01-06 12:30:00",
                        "2025-01-06 12:40:00",  # Window 3: 5 events (+150% change)
                    ]
                ),
                "label": [
                    "malicious",
                    "normal",
                    "malicious",
                    "normal",
                    "malicious",
                    "malicious",
                    "malicious",
                    "malicious",
                    "normal",
                ],
            }
        )

        result = calculate_trend_percentage_change(
            df, timestamp_col="timestamp_start", window_minutes=time_window
        )

        # Check that the columns were added
        assert "events_pct_change" in result.columns
        assert "malicious_events_pct_change" in result.columns
        assert "burst_indicator" in result.columns

        # Window 1 (rows 0-1): First window, no previous data
        assert result["events_pct_change"].iloc[0] == 0  # or NaN filled with 0
        assert result["events_pct_change"].iloc[1] == 0

        # Window 2 (rows 2-3): Same as window 1 (2 events), 0% change
        assert result["events_pct_change"].iloc[2] == 0
        assert result["events_pct_change"].iloc[3] == 0

        # Window 3 (rows 4-8): 5 events vs 2 previous = 150% increase
        assert result["events_pct_change"].iloc[4] == 150.0
        assert result["events_pct_change"].iloc[5] == 150.0
        assert result["events_pct_change"].iloc[6] == 150.0
        assert result["events_pct_change"].iloc[7] == 150.0
        assert result["events_pct_change"].iloc[8] == 150.0

        # Burst indicator shouldn't be triggered (<50% increase)
        assert result["burst_indicator"].iloc[0] == 0
        assert result["burst_indicator"].iloc[1] == 0
        assert result["burst_indicator"].iloc[2] == 0
        assert result["burst_indicator"].iloc[3] == 0

        # Burst indicator should be triggered (>50% increase)
        assert result["burst_indicator"].iloc[4] == 1
        assert result["burst_indicator"].iloc[5] == 1
        assert result["burst_indicator"].iloc[6] == 1
        assert result["burst_indicator"].iloc[7] == 1
        assert result["burst_indicator"].iloc[8] == 1

        # Check that original dataframe length is preserved
        assert len(result) == len(df)

    def test_calculate_total_events_for_dst_ports(self):
        """test basic event counting per destination port"""

        time_window = 60  # mins

        df = pd.DataFrame(
            {
                "timestamp_start": pd.to_datetime(
                    [
                        "2025-01-06 10:00:00",
                        "2025-01-06 10:15:00",
                        "2025-01-06 10:30:00",
                        "2025-01-06 10:45:00",
                        "2025-01-06 11:00:00",
                    ]
                ),
                "destination_port": [80, 80, 22, 80, 22],
                "label": ["normal", "malicious", "malicious", "normal", "malicious"],
            }
        )

        result = calculate_total_events_for_dst_ports(
            df,
            timestamp_col="timestamp_start",
            destination_port_col="destination_port",
            window_minutes=time_window,
        )

        # Check that the column was added
        assert "events_to_dst_port" in result.columns
        assert "destination_port" in result.columns

        # Window 1 (10:00-11:00):
        # Port 80: 3 events (rows 0, 1, 3)
        # Port 22: 1 event (row 2)

        # Rows 0, 1, 3: Port 80
        assert result["events_to_dst_port"].iloc[0] == 3
        assert result["events_to_dst_port"].iloc[1] == 3
        assert result["events_to_dst_port"].iloc[3] == 3

        # Row 2: Port 22
        assert result["events_to_dst_port"].iloc[2] == 1

        # Window 2 (11:00-12:00):
        # Port 22: 1 event (row 4)
        assert result["events_to_dst_port"].iloc[4] == 1

        # Check that original dataframe length is preserved
        assert len(result) == len(df)

    def test_calculate_total_malicious_events_per_protocol(self):
        """test basic malicious event counting per protocol"""

        time_window = 60  # mins

        df = pd.DataFrame(
            {
                "timestamp_start": pd.to_datetime(
                    [
                        "2025-01-06 10:00:00",
                        "2025-01-06 10:15:00",
                        "2025-01-06 10:30:00",
                        "2025-01-06 10:45:00",
                        "2025-01-06 11:00:00",
                    ]
                ),
                "application_protocol": ["http", "dns", "http", "dns", "ssh"],
                "label": ["normal", "malicious", "normal", "malicious", "malicious"],
            }
        )

        result = calculate_total_malicious_events_per_protocol(
            df,
            timestamp_col="timestamp_start",
            app_protocol_col="application_protocol",
            window_minutes=time_window,
        )

        # Check columns exist
        assert "total_events_for_protocol" in result.columns
        assert "malicious_events_for_protocol" in result.columns
        assert "malicious_ratio_for_protocol" in result.columns

        # Window 1 (10:00-11:00):
        # HTTP: 2 total, 0 malicious (0%)
        # DNS: 2 total, 2 malicious (100%)

        # Row 0: HTTP, window 1
        assert result["total_events_for_protocol"].iloc[0] == 2
        assert result["malicious_events_for_protocol"].iloc[0] == 0
        assert result["malicious_ratio_for_protocol"].iloc[0] == 0.0

        # Row 1: DNS, window 1
        assert result["total_events_for_protocol"].iloc[1] == 2
        assert result["malicious_events_for_protocol"].iloc[1] == 2
        assert result["malicious_ratio_for_protocol"].iloc[1] == 100.0

        # Row 2: HTTP, window 1 (same as row 0)
        assert result["total_events_for_protocol"].iloc[2] == 2
        assert result["malicious_events_for_protocol"].iloc[2] == 0

        # Row 3: DNS, window 1 (same as row 1)
        assert result["total_events_for_protocol"].iloc[3] == 2
        assert result["malicious_events_for_protocol"].iloc[3] == 2

        # Window 2 (11:00-12:00):
        # SSH: 1 total, 1 malicious (100%)
        assert result["total_events_for_protocol"].iloc[4] == 1
        assert result["malicious_events_for_protocol"].iloc[4] == 1
        assert result["malicious_ratio_for_protocol"].iloc[4] == 100.0

        # Check that original dataframe length is preserved
        assert len(result) == len(df)
