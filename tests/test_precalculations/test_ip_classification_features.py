import os
import sys

import numpy as np
import pandas as pd
import pytest

from src.feature_engineering.precalculations_functions import (
    calculate_ip_classification_features,
    is_private_ip,
)


class TestIsPrivateIp:

    def test_is_private_ip_class_a(self):
        """Test Class A private IPs (10.0.0.0/8)"""
        assert is_private_ip("10.0.0.1") == True
        assert is_private_ip("10.255.255.255") == True

    def test_is_private_ip_class_b(self):
        """Test Class B private IPs (172.16.0.0/12)"""
        assert is_private_ip("172.16.0.1") == True
        assert is_private_ip("172.31.255.255") == True
        assert is_private_ip("172.15.0.1") == False  # Outside range
        assert is_private_ip("172.32.0.1") == False  # Outside range

    def test_is_private_ip_class_c(self):
        """Test Class C private IPs (192.168.0.0/16)"""
        assert is_private_ip("192.168.0.1") == True
        assert is_private_ip("192.168.255.255") == True

    def test_is_private_ip_public(self):
        """Test public IPs"""
        assert is_private_ip("8.8.8.8") == False  # Google DNS
        assert is_private_ip("1.1.1.1") == False  # Cloudflare DNS
        assert is_private_ip("161.185.160.93") == False

    def test_is_private_ip_invalid(self):
        """Test invalid IPs"""
        assert is_private_ip("invalid") == False
        assert is_private_ip("") == False
        assert is_private_ip(None) == False
        assert is_private_ip(np.nan) == False


class TestCalculateIpClassificationFeatures:

    def test_calculate_ip_classification_features_internal(self):
        """Test internal traffic (both IPs private)"""
        df = pd.DataFrame(
            {
                "source_ip": ["192.168.1.1", "10.0.0.1"],
                "destination_ip": ["192.168.1.2", "10.0.0.2"],
            }
        )

        result = calculate_ip_classification_features(df, "source_ip", "destination_ip")

        assert "src_is_private" in result.columns
        assert "dst_is_private" in result.columns
        assert "is_internal" in result.columns

        # Both rows should be internal
        assert result["src_is_private"].iloc[0] == 1
        assert result["dst_is_private"].iloc[0] == 1
        assert result["is_internal"].iloc[0] == 1

    def test_calculate_ip_classification_features_external(self):
        """Test external traffic (at least one public IP)"""
        df = pd.DataFrame(
            {
                "source_ip": ["8.8.8.8", "192.168.1.1", "10.0.0.1"],
                "destination_ip": ["1.1.1.1", "8.8.8.8", "1.1.1.1"],
            }
        )

        result = calculate_ip_classification_features(df, "source_ip", "destination_ip")

        # Row 0: public to public
        assert result["src_is_private"].iloc[0] == 0
        assert result["dst_is_private"].iloc[0] == 0
        assert result["is_internal"].iloc[0] == 0

        # Row 1: private to public
        assert result["src_is_private"].iloc[1] == 1
        assert result["dst_is_private"].iloc[1] == 0
        assert result["is_internal"].iloc[1] == 0

        # Row 2: private to public
        assert result["src_is_private"].iloc[2] == 1
        assert result["dst_is_private"].iloc[2] == 0
        assert result["is_internal"].iloc[2] == 0

    def test_calculate_ip_classification_features_with_nan(self):
        """Test handling of NaN values"""
        df = pd.DataFrame(
            {
                "source_ip": ["192.168.1.1", np.nan, None],
                "destination_ip": ["192.168.1.2", "8.8.8.8", "10.0.0.1"],
            }
        )

        result = calculate_ip_classification_features(df, "source_ip", "destination_ip")

        # NaN should be treated as not private
        assert result["src_is_private"].iloc[1] == 0
        assert result["src_is_private"].iloc[2] == 0
