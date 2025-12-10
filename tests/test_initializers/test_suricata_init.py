import json
import os
import tempfile

import pandas as pd
import pytest
from src.feature_engineering.df_initializing import SuricataDataFrameInitializer


class TestSuricataDataFrameInitializer:
    """Test suite for SuricataDataFrameInitializer"""

    @pytest.fixture
    def sample_suricata_data(self):
        """Create sample Suricata log data matching actual structure"""
        return [
            {
                "timestamp": "2025-10-24T02:44:06.405778+0000",
                "flow_id": 1742804078966555,
                "in_iface": "ens4",
                "event_type": "alert",
                "src_ip": "16.62.107.190",
                "dest_ip": "10.128.0.2",
                "proto": "ICMP",
                "icmp_type": 8,
                "icmp_code": 0,
                "pkt_src": "wire/pcap",
                "alert": {
                    "action": "allowed",
                    "gid": 1,
                    "signature_id": 2100384,
                    "rev": 6,
                    "signature": "GPL ICMP PING",
                    "category": "Misc activity",
                    "severity": 3,
                    "metadata": {
                        "confidence": ["Medium"],
                        "created_at": ["2010_09_23"],
                        "signature_severity": ["Informational"],
                        "updated_at": ["2019_07_26"],
                    },
                },
                "direction": "to_server",
                "flow": {
                    "pkts_toserver": 1,
                    "pkts_toclient": 0,
                    "bytes_toserver": 82,
                    "bytes_toclient": 0,
                    "start": "2025-10-24T02:44:06.405778+0000",
                    "src_ip": "16.62.107.190",
                    "dest_ip": "10.128.0.2",
                },
                "payload": "GHFNO0u3l6JdADiOxuVmH48Zx6noyuYsen52WfzUL7dZBuQ+th1JTg==",
                "payload_printable": ".qM;K...].8...f........,z~vY../.Y..>..IN",
                "stream": 0,
            },
            {
                "timestamp": "2025-10-24T02:44:07.619878+0000",
                "flow_id": 2096863666648705,
                "in_iface": "ens4",
                "event_type": "alert",
                "src_ip": "169.254.169.254",
                "src_port": 53,
                "dest_ip": "10.128.0.2",
                "dest_port": 36113,
                "proto": "UDP",
                "pkt_src": "wire/pcap",
                "alert": {
                    "action": "allowed",
                    "gid": 1,
                    "signature_id": 2002752,
                    "rev": 4,
                    "signature": "ET INFO Reserved Internal IP Traffic",
                    "category": "Potentially Bad Traffic",
                    "severity": 2,
                    "metadata": {
                        "confidence": ["High"],
                        "created_at": ["2010_07_30"],
                        "signature_severity": ["Informational"],
                        "updated_at": ["2019_07_26"],
                    },
                },
                "app_proto": "failed",
                "direction": "to_client",
                "flow": {
                    "pkts_toserver": 2,
                    "pkts_toclient": 1,
                    "bytes_toserver": 164,
                    "bytes_toclient": 172,
                    "start": "2025-10-24T02:44:07.619286+0000",
                    "src_ip": "10.128.0.2",
                    "dest_ip": "169.254.169.254",
                    "src_port": 36113,
                    "dest_port": 53,
                },
                "payload": "a1yBgAABAAUAAAAAB2xvZ2dpbmcKZ29vZ2xlYXBpcwNjb20AAAEAAcAMAAUAAQAAASgADgtsb2dnaW5nLWFsdsAUwDQAAQABAAABKAAE2O8irsA0AAEAAQAAASgABNjvJq7ANAABAAEAAAEoAATY7yCuwDQAAQABAAABKAAE2O8krg==",
                "payload_printable": 'k\\...........logging\ngoogleapis.com..............(...logging-alv...4.......(...."..4.......(....&..4.......(.... ..4.......(.....$.',
                "stream": 0,
            },
        ]

    @pytest.fixture
    def temp_suricata_file(self, sample_suricata_data):
        """Create temporary Suricata JSON file"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            for record in sample_suricata_data:
                f.write(json.dumps(record) + "\n")
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    def test_initialization(self, temp_suricata_file):
        """Test SuricataDataFrameInitializer initialization"""
        initializer = SuricataDataFrameInitializer(temp_suricata_file)
        assert initializer.suricata_json_path == temp_suricata_file

    def test_initialize_suricata_returns_dataframe(self, temp_suricata_file):
        """Test that initialize_suricata returns a DataFrame"""
        initializer = SuricataDataFrameInitializer(temp_suricata_file)
        df = initializer.initialize_suricata()
        assert isinstance(df, pd.DataFrame)

    def test_initialize_suricata_correct_shape(
        self, temp_suricata_file, sample_suricata_data
    ):
        """Test DataFrame has correct number of rows"""
        initializer = SuricataDataFrameInitializer(temp_suricata_file)
        df = initializer.initialize_suricata()
        assert len(df) == len(sample_suricata_data)

    def test_initialize_suricata_contains_expected_columns(self, temp_suricata_file):
        """Test DataFrame contains expected columns"""
        initializer = SuricataDataFrameInitializer(temp_suricata_file)
        df = initializer.initialize_suricata()

        # Check for key columns from actual Suricata data
        assert "timestamp" in df.columns
        assert "flow_id" in df.columns
        assert "event_type" in df.columns
        assert "src_ip" in df.columns
        assert "dest_ip" in df.columns
        assert "proto" in df.columns
        assert "alert" in df.columns
