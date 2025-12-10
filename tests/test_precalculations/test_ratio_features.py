import numpy as np
import pandas as pd
import pytest
from src.feature_engineering.precalculations_functions import \
    calculate_ratio_features


class TestCalculateRatioFeatures:

    def test_calculate_ratio_features_basic(self):
        """Test basic ratio calculation"""
        df = pd.DataFrame(
            {
                "bytes_sent": [1000, 2000],
                "bytes_received": [500, 1000],
                "pkts_sent": [10, 20],
                "pkts_received": [5, 10],
            }
        )

        result = calculate_ratio_features(df)

        # Check columns exist
        assert "bytes_sent_ratio" in result.columns
        assert "packets_sent_ratio" in result.columns

        # Check calculations
        assert result["bytes_sent_ratio"].iloc[0] == pytest.approx(
            0.667, rel=0.01
        )  # 1000/1500
        assert result["packets_sent_ratio"].iloc[0] == pytest.approx(
            0.667, rel=0.01
        )  # 10/15

    def test_calculate_ratio_features_zero_total(self):
        """Test handling of zero total bytes/packets"""
        df = pd.DataFrame(
            {
                "bytes_sent": [0],
                "bytes_received": [0],
                "pkts_sent": [0],
                "pkts_received": [0],
            }
        )

        result = calculate_ratio_features(df)

    def test_calculate_ratio_features_all_sent(self):
        """Test ratio when all bytes are sent"""
        df = pd.DataFrame(
            {
                "bytes_sent": [1000],
                "bytes_received": [0],
                "pkts_sent": [10],
                "pkts_received": [0],
            }
        )

        result = calculate_ratio_features(df)

        # Should be 1.0 (all sent, none received)
        assert result["bytes_sent_ratio"].iloc[0] == 1.0
        assert result["packets_sent_ratio"].iloc[0] == 1.0
