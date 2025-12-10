import pytest
import pandas as pd
import sys
import os


from src.feature_engineering.precalculations_functions import (
    calculate_temporal_features,
)


class TestCalculateTemporalFeatures:

    def test_calculate_temporal_features_basic(self):
        """Test basic temporal feature extraction"""
        df = pd.DataFrame(
            {
                "timestamp_start": pd.to_datetime(
                    [
                        "2025-01-06 10:00:00",  # Monday 10am
                        "2025-01-11 14:00:00",  # Saturday 2pm
                    ]
                )
            }
        )

        result = calculate_temporal_features(df, "timestamp_start")

        # Check columns exist
        assert "hour" in result.columns
        assert "day_of_week" in result.columns
        assert "is_weekend" in result.columns
        assert "is_business_hours" in result.columns

        # Check values for Monday 10am
        assert result["hour"].iloc[0] == 10
        assert result["day_of_week"].iloc[0] == 0  # Monday
        assert result["is_weekend"].iloc[0] == 0
        assert result["is_business_hours"].iloc[0] == 1  # 10am on weekday

        # Check values for Saturday 2pm
        assert result["hour"].iloc[1] == 14
        assert result["day_of_week"].iloc[1] == 5  # Saturday
        assert result["is_weekend"].iloc[1] == 1
        assert result["is_business_hours"].iloc[1] == 0  # Weekend

    def test_calculate_temporal_features_business_hours(self):
        """Test business hours detection"""
        df = pd.DataFrame(
            {
                "timestamp_start": pd.to_datetime(
                    [
                        "2025-01-06 08:00:00",  # Monday 8am - before business hours
                        "2025-01-06 09:00:00",  # Monday 9am - start of business hours
                        "2025-01-06 17:00:00",  # Monday 5pm - end of business hours
                        "2025-01-06 18:00:00",  # Monday 6pm - after business hours
                    ]
                )
            }
        )

        result = calculate_temporal_features(df, "timestamp_start")

        assert result["is_business_hours"].iloc[0] == 0  # 8am - too early
        assert result["is_business_hours"].iloc[1] == 1  # 9am - yes
        assert result["is_business_hours"].iloc[2] == 1  # 5pm - yes
        assert result["is_business_hours"].iloc[3] == 0  # 6pm - too late

    def test_calculate_temporal_features_weekend(self):
        """Test weekend detection"""
        df = pd.DataFrame(
            {
                "timestamp_start": pd.to_datetime(
                    [
                        "2025-01-10 10:00:00",  # Friday
                        "2025-01-11 10:00:00",  # Saturday
                        "2025-01-12 10:00:00",  # Sunday
                        "2025-01-13 10:00:00",  # Monday
                    ]
                )
            }
        )

        result = calculate_temporal_features(df, "timestamp_start")

        assert result["is_weekend"].iloc[0] == 0  # Friday
        assert result["is_weekend"].iloc[1] == 1  # Saturday
        assert result["is_weekend"].iloc[2] == 1  # Sunday
        assert result["is_weekend"].iloc[3] == 0  # Monday

    def test_calculate_temporal_features_string_input(self):
        """Test with string timestamps (should convert)"""
        df = pd.DataFrame(
            {"timestamp_start": ["2025-01-06 10:00:00", "2025-01-07 14:00:00"]}
        )

        result = calculate_temporal_features(df, "timestamp_start")

        # Should work and convert strings to datetime
        assert "hour" in result.columns
        assert result["hour"].iloc[0] == 10
