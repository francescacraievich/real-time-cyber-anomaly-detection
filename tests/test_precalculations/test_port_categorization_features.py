import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.feature_engineering.precalculations_functions import (
    calculate_port_categorization, is_port_common)


class TestIsPortCommon:

    def test_is_port_common_http(self):
        """Test HTTP port"""
        assert is_port_common(80) == True

    def test_is_port_common_https(self):
        """Test HTTPS port"""
        assert is_port_common(443) == True

    def test_is_port_common_ssh(self):
        """Test SSH port"""
        assert is_port_common(22) == True

    def test_is_port_common_all(self):
        """Test all common ports"""
        common_ports = [80, 443, 22, 21, 25, 53, 3389]
        for port in common_ports:
            assert is_port_common(port) == True

    def test_is_port_common_uncommon(self):
        """Test uncommon ports"""
        assert is_port_common(8080) == False
        assert is_port_common(12345) == False
        assert is_port_common(50000) == False


class TestCalculatePortCategorization:

    def test_calculate_port_categorization_common(self):
        """Test common port detection"""
        df = pd.DataFrame({"destination_port": [80, 443, 22, 8080, 12345]})

        result = calculate_port_categorization(df, "destination_port")

        assert "dst_port_is_common" in result.columns

        # First 3 should be common
        assert result["dst_port_is_common"].iloc[0] == 1  # 80
        assert result["dst_port_is_common"].iloc[1] == 1  # 443
        assert result["dst_port_is_common"].iloc[2] == 1  # 22

        # Last 2 should not be common
        assert result["dst_port_is_common"].iloc[3] == 0  # 8080
        assert result["dst_port_is_common"].iloc[4] == 0  # 12345

    def test_calculate_port_categorization_with_nan(self):
        """Test handling of NaN values"""
        df = pd.DataFrame({"destination_port": [80, np.nan, None]})

        result = calculate_port_categorization(df, "destination_port")

        assert result["dst_port_is_common"].iloc[0] == 1  # 80 is common
        assert result["dst_port_is_common"].iloc[1] == 0  # NaN -> not common
        assert result["dst_port_is_common"].iloc[2] == 0  # None -> not common

    def test_calculate_port_categorization_all_common(self):
        """Test with only common ports"""
        df = pd.DataFrame({"destination_port": [80, 443, 22, 21, 25, 53, 3389]})

        result = calculate_port_categorization(df, "destination_port")

        # All should be common
        assert all(result["dst_port_is_common"] == 1)
