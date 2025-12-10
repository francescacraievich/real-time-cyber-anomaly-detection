import json
import os
import tempfile
from pathlib import Path

import pandas as pd
import pytest
from src.feature_engineering.df_initializing import NormalTrafficDataFrameInitializer


class TestNormalTrafficDataFrameInitializer:
    """Test suite for NormalTrafficDataFrameInitializer"""

    @pytest.fixture
    def sample_normal_traffic_data(self):
        """Create sample normal traffic log data matching actual structure"""
        return [
            {
                "generated": "3/11/2014 18:21",
                "appName": "Unknown_UDP",
                "totalSourceBytes": 16076,
                "totalDestinationBytes": 0,
                "totalDestinationPackets": 0,
                "totalSourcePackets": 178,
                "sourcePayloadAsBase64": None,
                "sourcePayloadAsUTF": None,
                "destinationPayloadAsBase64": None,
                "destinationPayloadAsUTF": None,
                "direction": "L2R",
                "sourceTCPFlagsDescription": None,
                "destinationTCPFlagsDescription": None,
                "source": "192.168.5.122",
                "protocolName": "udp_ip",
                "sourcePort": 5353,
                "destination": "224.0.0.251",
                "destinationPort": 5353,
                "startDateTime": "6/13/2010 23:57",
                "stopDateTime": "6/14/2010 0:11",
                "Label": "Normal",
            },
            {
                "generated": "3/11/2014 18:21",
                "appName": "HTTPImageTransfer",
                "totalSourceBytes": 384,
                "totalDestinationBytes": 0,
                "totalDestinationPackets": 0,
                "totalSourcePackets": 6,
                "sourcePayloadAsBase64": None,
                "sourcePayloadAsUTF": None,
                "destinationPayloadAsBase64": None,
                "destinationPayloadAsUTF": None,
                "direction": "L2R",
                "sourceTCPFlagsDescription": "F,A",
                "destinationTCPFlagsDescription": None,
                "source": "192.168.2.111",
                "protocolName": "tcp_ip",
                "sourcePort": 4435,
                "destination": "206.217.198.186",
                "destinationPort": 80,
                "startDateTime": "6/13/2010 23:58",
                "stopDateTime": "6/14/2010 0:01",
                "Label": "Normal",
            },
        ]

    @pytest.fixture
    def temp_traffic_file(self, sample_normal_traffic_data):
        """Create temporary normal traffic JSON file in ijson-compatible format"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            json.dump(sample_normal_traffic_data, f)
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    def test_initialization(self, temp_traffic_file):
        """Test NormalTrafficDataFrameInitializer initialization"""
        initializer = NormalTrafficDataFrameInitializer(temp_traffic_file)
        assert initializer.benign_traffic_json_path == temp_traffic_file

    def test_initialize_benign_traffic_returns_dataframe(self, temp_traffic_file):
        """Test that initialize_benign_traffic returns a DataFrame"""
        initializer = NormalTrafficDataFrameInitializer(temp_traffic_file)
        df = initializer.initialize_benign_traffic(sample_size=10)
        assert isinstance(df, pd.DataFrame)

    def test_initialize_benign_traffic_correct_shape(
        self, temp_traffic_file, sample_normal_traffic_data
    ):
        """Test DataFrame has correct number of rows when sample size >= data size"""
        initializer = NormalTrafficDataFrameInitializer(temp_traffic_file)
        df = initializer.initialize_benign_traffic(sample_size=10)
        assert len(df) == len(sample_normal_traffic_data)

    def test_initialize_benign_traffic_contains_expected_columns(
        self, temp_traffic_file
    ):
        """Test DataFrame contains expected columns"""
        initializer = NormalTrafficDataFrameInitializer(temp_traffic_file)
        df = initializer.initialize_benign_traffic(sample_size=10)

        # Check for key columns from actual normal traffic data
        expected_columns = [
            "generated",
            "appName",
            "totalSourceBytes",
            "totalDestinationBytes",
            "totalSourcePackets",
            "totalDestinationPackets",
            "source",
            "destination",
            "sourcePort",
            "destinationPort",
            "protocolName",
            "direction",
            "Label",
        ]

        for col in expected_columns:
            assert col in df.columns, f"Missing expected column: {col}"

    def test_sample_size_limit(self, temp_traffic_file):
        """Test that sample size is respected"""
        initializer = NormalTrafficDataFrameInitializer(temp_traffic_file)
        df = initializer.initialize_benign_traffic(sample_size=1)
        assert len(df) == 1
