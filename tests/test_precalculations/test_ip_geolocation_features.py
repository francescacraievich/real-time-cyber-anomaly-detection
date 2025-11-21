import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from feature_engineering.precalculations_functions.ip_geolocation_features import (
    calculate_ip_info,
    calculate_src_ip_geolocation_features,
    calculate_dst_ip_geolocation_features
)


class TestIPGeolocationFeatures:
    
    def test_calculate_ip_info_failure(self):
        """Test failed IP info retrieval"""
        
        # Mock failed API response
        with patch('requests.get', side_effect=Exception("Network error")):
            result = calculate_ip_info("8.8.8.8")
            
            assert result["success"] == False
    
    
    def test_calculate_src_ip_geolocation_features_basic(self):
        """Test basic source IP geolocation feature calculation"""
        
        df = pd.DataFrame({
            'source_ip': ['8.8.8.8', '1.1.1.1'],
            'label': ['normal', 'malicious']
        })
        
        # Mock API responses
        mock_responses = {
            "8.8.8.8": {
                "success": True,
                "type": "IPv4",
                "continent": "North America",
                "country": "United States",
                "region": "California",
                "city": "Mountain View",
                "latitude": 37.4056,
                "longitude": -122.0775,
                "connection": {"isp": "Google LLC"}
            },
            "1.1.1.1": {
                "success": True,
                "type": "IPv4",
                "continent": "Oceania",
                "country": "Australia",
                "region": "New South Wales",
                "city": "Sydney",
                "latitude": -33.8688,
                "longitude": 151.2093,
                "connection": {"isp": "Cloudflare"}
            }
        }
        
    def test_calculate_src_ip_geolocation_features_failed_lookup(self):
        """Test handling of failed IP lookups"""
        
        df = pd.DataFrame({
            'source_ip': ['192.168.1.1', '10.0.0.1'],
            'label': ['normal', 'normal']
        })
        
        # Mock failed API responses (private IPs)
        def mock_calculate_ip_info(ip):
            return {"success": False}
        
        with patch('feature_engineering.precalculations_functions.ip_geolocation_features.calculate_ip_info', side_effect=mock_calculate_ip_info):
            result = calculate_src_ip_geolocation_features(df, rate_limit_delay=0)
            
            # All values should be None
            assert result['src_ip_type'].iloc[0] is None
            assert result['src_country'].iloc[0] is None
            assert result['src_latitude'].iloc[0] is None
            assert result['src_isp'].iloc[0] is None
            
            # Check that original dataframe length is preserved
            assert len(result) == len(df)
    