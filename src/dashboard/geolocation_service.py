"""
Geolocation service using GeoLite2 database for offline IP geolocation.
Falls back to ipwho.is API if database not available.
"""

import ipaddress
import json
from pathlib import Path
from typing import Dict, Optional

import requests

# Try to import geoip2, fallback to API if not available
try:
    import geoip2.database
    import geoip2.errors

    GEOIP2_AVAILABLE = True
except ImportError:
    GEOIP2_AVAILABLE = False


class GeolocationService:
    """Service for IP geolocation with caching."""

    def __init__(self):
        self.cache: Dict[str, Dict] = {}
        self.cache_file = Path(__file__).parent / "geo_cache.json"
        self.geoip_reader = None

        # Try to load GeoLite2 database
        self._init_geoip_database()

        # Load existing cache
        self._load_cache()

    def _init_geoip_database(self):
        """Initialize GeoIP2 database reader."""
        if not GEOIP2_AVAILABLE:
            return

        # Common paths for GeoLite2 database
        possible_paths = [
            Path(__file__).parent / "GeoLite2-City.mmdb",
            Path(__file__).parent.parent / "data" / "GeoLite2-City.mmdb",
            Path.home() / "GeoLite2-City.mmdb",
            Path("/usr/share/GeoIP/GeoLite2-City.mmdb"),
        ]

        for db_path in possible_paths:
            if db_path.exists():
                try:
                    self.geoip_reader = geoip2.database.Reader(str(db_path))
                    return
                except Exception:
                    pass

    def _load_cache(self):
        """Load cached geolocation data."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r") as f:
                    self.cache = json.load(f)
            except Exception:
                self.cache = {}

    def _save_cache(self):
        """Save geolocation cache to disk."""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f)
        except Exception:
            pass

    def _is_private_ip(self, ip: str) -> bool:
        """Check if IP is private/internal."""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_reserved
        except ValueError:
            return True

    def _lookup_geoip2(self, ip: str) -> Optional[Dict]:
        """Lookup IP using GeoIP2 database."""
        if not self.geoip_reader:
            return None

        try:
            response = self.geoip_reader.city(ip)
            return {
                "ip": ip,
                "country": response.country.name or "Unknown",
                "country_code": response.country.iso_code or "XX",
                "city": response.city.name or "Unknown",
                "latitude": response.location.latitude,
                "longitude": response.location.longitude,
                "source": "geoip2",
            }
        except geoip2.errors.AddressNotFoundError:
            return None
        except Exception:
            return None

    def _lookup_api(self, ip: str) -> Optional[Dict]:
        """Lookup IP using ipwho.is API (fallback)."""
        try:
            response = requests.get(f"https://ipwho.is/{ip}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("success", False):
                    return {
                        "ip": ip,
                        "country": data.get("country", "Unknown"),
                        "country_code": data.get("country_code", "XX"),
                        "city": data.get("city", "Unknown"),
                        "latitude": data.get("latitude"),
                        "longitude": data.get("longitude"),
                        "source": "api",
                    }
        except Exception:
            pass
        return None

    def get_location(self, ip: str) -> Optional[Dict]:
        """Get geolocation for an IP address."""
        # Check cache first
        if ip in self.cache:
            return self.cache[ip]

        # Skip private IPs
        if self._is_private_ip(ip):
            result = {
                "ip": ip,
                "country": "Private",
                "country_code": "XX",
                "city": "Internal",
                "latitude": None,
                "longitude": None,
                "source": "private",
            }
            self.cache[ip] = result
            return result

        # Try GeoIP2 first (fast, offline)
        result = self._lookup_geoip2(ip)

        # Fallback to API
        if result is None:
            result = self._lookup_api(ip)

        # Cache result
        if result:
            self.cache[ip] = result
            # Periodically save cache
            if len(self.cache) % 100 == 0:
                self._save_cache()

        return result

    def get_locations_batch(self, ips: list, progress_callback=None) -> Dict[str, Dict]:
        """Get geolocation for multiple IPs."""
        results = {}
        total = len(ips)

        for i, ip in enumerate(ips):
            results[ip] = self.get_location(ip)

            if progress_callback and i % 50 == 0:
                progress_callback(i, total)

        # Save cache after batch
        self._save_cache()

        return results

    def get_cached_count(self) -> int:
        """Return number of cached IPs."""
        return len(self.cache)

    def close(self):
        """Close database reader."""
        if self.geoip_reader:
            self.geoip_reader.close()


# Singleton instance
_geo_service = None


def get_geo_service() -> GeolocationService:
    """Get singleton geolocation service instance."""
    global _geo_service
    if _geo_service is None:
        _geo_service = GeolocationService()
    return _geo_service
