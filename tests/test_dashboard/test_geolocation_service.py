"""Tests for geolocation service - IP lookup and caching."""

import pytest
import json
import tempfile
from pathlib import Path
import sys
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.append(str(Path(__file__).parents[2]))

from src.dashboard.geolocation_service import GeolocationService


class TestGeolocationService:
    """Test GeolocationService class for IP geolocation and caching."""

    @pytest.fixture
    def temp_cache_file(self, tmp_path):
        """Create a temporary cache file for testing."""
        cache_file = tmp_path / "test_geo_cache.json"
        return cache_file

    @pytest.fixture
    def geo_service(self, temp_cache_file, monkeypatch):
        """Create a GeolocationService instance with temporary cache."""
        # Patch the cache file path
        with patch.object(GeolocationService, "__init__", lambda self: None):
            service = GeolocationService()
            service.cache = {}
            service.cache_file = temp_cache_file
            service.geoip_reader = None
            return service

    def test_private_ip_detection_192(self, geo_service):
        """Test detection of private IP addresses (192.168.x.x)."""
        result = geo_service.get_location("192.168.1.1")

        assert result is not None
        assert result["country"] == "Private"
        assert result["country_code"] == "XX"
        assert result["city"] == "Internal"
        assert result["source"] == "private"

    def test_private_ip_detection_10(self, geo_service):
        """Test detection of private IP addresses (10.x.x.x)."""
        result = geo_service.get_location("10.0.0.1")

        assert result is not None
        assert result["country"] == "Private"
        assert result["city"] == "Internal"

    def test_private_ip_detection_172(self, geo_service):
        """Test detection of private IP addresses (172.16-31.x.x)."""
        result = geo_service.get_location("172.16.0.1")

        assert result is not None
        assert result["country"] == "Private"

    def test_loopback_ip_detection(self, geo_service):
        """Test detection of loopback IP (127.0.0.1)."""
        result = geo_service.get_location("127.0.0.1")

        assert result is not None
        assert result["country"] == "Private"

    def test_cache_hit(self, geo_service):
        """Test that cached IPs are returned from cache."""
        # First lookup (cache miss)
        ip = "192.168.1.100"
        result1 = geo_service.get_location(ip)

        # Second lookup (cache hit)
        result2 = geo_service.get_location(ip)

        assert result1 == result2
        assert ip in geo_service.cache

    def test_cache_persistence(self, temp_cache_file, geo_service):
        """Test that cache is saved and loaded correctly."""
        # Add some entries to cache
        geo_service.cache["192.168.1.1"] = {
            "ip": "192.168.1.1",
            "country": "Private",
            "country_code": "XX",
            "city": "Internal",
        }
        geo_service.cache["10.0.0.1"] = {
            "ip": "10.0.0.1",
            "country": "Private",
            "country_code": "XX",
            "city": "Internal",
        }

        # Save cache
        geo_service._save_cache()

        # Verify cache file exists and contains data
        assert temp_cache_file.exists()

        with open(temp_cache_file, "r") as f:
            loaded_cache = json.load(f)

        assert len(loaded_cache) == 2
        assert "192.168.1.1" in loaded_cache

    def test_cache_loading(self, temp_cache_file):
        """Test loading existing cache from file."""
        # Create cache file with data
        cache_data = {
            "8.8.8.8": {
                "ip": "8.8.8.8",
                "country": "United States",
                "city": "Mountain View",
            }
        }

        with open(temp_cache_file, "w") as f:
            json.dump(cache_data, f)

        # Create new service (should load cache)
        with patch.object(GeolocationService, "__init__", lambda self: None):
            service = GeolocationService()
            service.cache_file = temp_cache_file
            service.geoip_reader = None
            service._load_cache()

            assert len(service.cache) == 1
            assert "8.8.8.8" in service.cache

    def test_invalid_ip_handling(self, geo_service):
        """Test handling of invalid IP addresses."""
        result = geo_service.get_location("invalid_ip")

        # Should treat as private/invalid
        assert result is not None
        assert result["country"] == "Private"

    def test_get_cached_count(self, geo_service):
        """Test get_cached_count method."""
        assert geo_service.get_cached_count() == 0

        # Add some entries
        geo_service.get_location("192.168.1.1")
        geo_service.get_location("10.0.0.1")

        assert geo_service.get_cached_count() == 2

    @patch("src.dashboard.geolocation_service.requests.get")
    def test_api_lookup_fallback(self, mock_get, geo_service):
        """Test API lookup when GeoIP2 database is not available."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "ip": "8.8.8.8",
            "country": "United States",
            "country_code": "US",
            "city": "Mountain View",
            "latitude": 37.4056,
            "longitude": -122.0775,
        }
        mock_get.return_value = mock_response

        # Lookup public IP (should use API)
        result = geo_service._lookup_api("8.8.8.8")

        assert result is not None
        assert result["country"] == "United States"
        assert result["city"] == "Mountain View"
        assert result["source"] == "api"

    @patch("src.dashboard.geolocation_service.requests.get")
    def test_api_lookup_failure(self, mock_get, geo_service):
        """Test API lookup failure handling."""
        # Mock API failure
        mock_get.side_effect = Exception("API unreachable")

        result = geo_service._lookup_api("8.8.8.8")

        assert result is None

    def test_get_locations_batch(self, geo_service):
        """Test batch IP lookup."""
        ips = ["192.168.1.1", "10.0.0.1", "172.16.0.1"]

        results = geo_service.get_locations_batch(ips)

        assert len(results) == 3
        assert all(ip in results for ip in ips)
        assert all(results[ip]["country"] == "Private" for ip in ips)

    def test_batch_with_progress_callback(self, geo_service):
        """Test batch lookup with progress callback."""
        ips = ["192.168.1.{}".format(i) for i in range(1, 101)]

        progress_calls = []

        def progress_callback(current, total):
            progress_calls.append((current, total))

        results = geo_service.get_locations_batch(ips, progress_callback)

        assert len(results) == 100
        assert len(progress_calls) > 0  # Should have called callback

    def test_save_cache_on_batch(self, geo_service, temp_cache_file):
        """Test that cache is saved after batch processing."""
        ips = ["192.168.1.{}".format(i) for i in range(1, 6)]

        geo_service.get_locations_batch(ips)

        # Cache file should exist (saved after batch)
        assert temp_cache_file.exists()
