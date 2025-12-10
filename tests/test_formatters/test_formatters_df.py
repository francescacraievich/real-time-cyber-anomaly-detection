import json
import os
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from src.feature_engineering.df_formatting import DataFrameFormatter
from src.feature_engineering.df_initializing import DataFrameInitializer


class TestNormalTrafficDataFrameFormatter:
    """Test suite for NormalTrafficDataFrameFormatter"""

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
    def temp_normal_traffic_file(self, sample_normal_traffic_data):
        """Create temporary normal traffic JSON file in ijson-compatible format"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            json.dump(sample_normal_traffic_data, f)
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def temp_suricata_file(self, sample_suricata_data):
        """Create temporary Suricata JSON file"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            for record in sample_suricata_data:
                f.write(json.dumps(record) + "\n")
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def create_base_features(self, temp_normal_traffic_file, temp_suricata_file):
        """Initialize the main features"""
        df_initializer = DataFrameInitializer(
            suricata_json_path=temp_suricata_file,
            normal_traffic_json_path=temp_normal_traffic_file,
        )
        df_suricata, df_normal_traffic = df_initializer.initialize_dfs(sample_size=2)
        return DataFrameFormatter(df_suricata, df_normal_traffic).base_features

    def test_formatter_output_suricata(
        self, temp_normal_traffic_file, temp_suricata_file, create_base_features
    ):
        """Test that the output df has the correct features"""
        df_initializer = DataFrameInitializer(
            suricata_json_path=temp_suricata_file,
            normal_traffic_json_path=temp_normal_traffic_file,
        )

        df_suricata, df_normal_traffic = df_initializer.initialize_dfs(sample_size=2)

        df_formatter = DataFrameFormatter(df_suricata, df_normal_traffic)

        expected_columns = create_base_features
        for col in expected_columns:
            assert col in df_formatter.suricata_df.columns

    def test_formatter_output_normal_traffic(
        self, temp_normal_traffic_file, temp_suricata_file, create_base_features
    ):
        """Test that the output df has the correct features"""

        df_initializer = DataFrameInitializer(
            suricata_json_path=temp_suricata_file,
            normal_traffic_json_path=temp_normal_traffic_file,
        )

        df_suricata, df_normal_traffic = df_initializer.initialize_dfs(sample_size=2)

        df_formatter = DataFrameFormatter(df_suricata, df_normal_traffic)

        expected_columns = create_base_features
        for col in expected_columns:
            assert col in df_formatter.normal_traffic_df.columns
