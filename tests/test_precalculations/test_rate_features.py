import pandas as pd

from src.feature_engineering.precalculations_functions import calculate_rate_features


class TestCalculateRateFeatures:

    def test_calculate_rate_features_basic(self):
        """Test basic rate calculation"""
        df = pd.DataFrame(
            {
                "bytes_sent": [1000, 2000, 3000],
                "bytes_received": [500, 1000, 1500],
                "pkts_sent": [10, 20, 30],
                "pkts_received": [5, 10, 15],
                "duration": [10, 20, 30],
            }
        )

        result = calculate_rate_features(df)

        # Check columns exist
        assert "bytes_per_second" in result.columns
        assert "packets_per_second" in result.columns
        assert "bytes_per_packet" in result.columns

        # Check calculations
        assert result["bytes_per_second"].iloc[0] == 150.0  # (1000+500)/10
        assert result["packets_per_second"].iloc[0] == 1.5  # (10+5)/10
        assert result["bytes_per_packet"].iloc[0] == 100.0  # (1000+500)/(10+5)

    def test_calculate_rate_features_zero_duration(self):
        """Test handling of zero duration"""
        df = pd.DataFrame(
            {
                "bytes_sent": [1000],
                "bytes_received": [500],
                "pkts_sent": [10],
                "pkts_received": [5],
                "duration": [0],
            }
        )

        result = calculate_rate_features(df)

        # Should return 0, not error
        assert result["bytes_per_second"].iloc[0] == 0
        assert result["packets_per_second"].iloc[0] == 0

    def test_calculate_rate_features_zero_packets(self):
        """Test handling of zero packets"""
        df = pd.DataFrame(
            {
                "bytes_sent": [1000],
                "bytes_received": [500],
                "pkts_sent": [0],
                "pkts_received": [0],
                "duration": [10],
            }
        )

        result = calculate_rate_features(df)

        # Should return 0 for bytes_per_packet
        assert result["bytes_per_packet"].iloc[0] == 0

    def test_calculate_rate_features_custom_columns(self):
        """Test with custom column names"""
        df = pd.DataFrame(
            {
                "src_bytes": [1000],
                "dst_bytes": [500],
                "src_pkts": [10],
                "dst_pkts": [5],
                "time": [10],
            }
        )

        result = calculate_rate_features(
            df,
            bytes_sent_col="src_bytes",
            bytes_received_col="dst_bytes",
            pkts_sent_col="src_pkts",
            pkts_received_col="dst_pkts",
            duration_col="time",
        )

        assert "bytes_per_second" in result.columns
        assert result["bytes_per_second"].iloc[0] == 150.0
