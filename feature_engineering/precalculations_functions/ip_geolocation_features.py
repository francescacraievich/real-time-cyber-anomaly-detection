import requests
import pandas as pd
import numpy as np
import time


def calculate_ip_info(ip):
    """
    Fetch IP geolocation information from ipwho.is API.
    """
    try:
        url = f"https://ipwho.is/{ip}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Warning: Error fetching info for IP {ip}: {e}")
        return {"success": False}


def calculate_src_ip_geolocation_features(df, src_ip_col='source_ip', rate_limit_delay=0.1):    
    """
    Creates features:
    - src_ip_type: IPv4 or IPv6
    - src_continent: Continent name
    - src_country: Country name
    - src_region: State/province 
    - src_city: City name 
    - src_latitude: Geographic latitude
    - src_longitude: Geographic longitude
    - src_isp: Internet Service Provider name
    """

    df = df.copy()
    
    # Get unique IPs to minimize API calls
    unique_ips = df[src_ip_col].unique()
    
    # Create lookup dictionary for unique IPs
    geo_lookup = {}
        
    print(f"Fetching geolocation data for {len(unique_ips)} unique IPs...")
        
    for i, ip in enumerate(unique_ips):
        # Fetch IP info
        ip_info = calculate_ip_info(ip)
        
        # Extract only the specified fields from response
        if ip_info.get("success", False):
            geo_lookup[ip] = {
                'src_ip_type': ip_info.get('type'),
                'src_continent': ip_info.get('continent'),
                'src_country': ip_info.get('country'),
                'src_region': ip_info.get('region'),
                'src_city': ip_info.get('city'),
                'src_latitude': ip_info.get('latitude'),
                'src_longitude': ip_info.get('longitude'),
                'src_isp': ip_info.get('connection', {}).get('isp') if isinstance(ip_info.get('connection'), dict) else None,
            }
        else:
            # API call failed or IP not found
            geo_lookup[ip] = {
                'src_ip_type': None,
                'src_continent': None,
                'src_country': None,
                'src_region': None,
                'src_city': None,
                'src_latitude': None,
                'src_longitude': None,
                'src_isp': None,
            }
        
        # Rate limiting: wait between requests
        if i < len(unique_ips) - 1:  # Don't wait after last request
            time.sleep(rate_limit_delay)
        
        # Progress indicator
        if (i + 1) % 10 == 0:
            print(f"Processed {i + 1}/{len(unique_ips)} IPs...")
    
    print("Geolocation lookup complete!")
    
    # Map geolocation data back to dataframe
    df['src_ip_type'] = df[src_ip_col].map(lambda ip: geo_lookup[ip]['src_ip_type'])
    df['src_continent'] = df[src_ip_col].map(lambda ip: geo_lookup[ip]['src_continent'])
    df['src_country'] = df[src_ip_col].map(lambda ip: geo_lookup[ip]['src_country'])
    df['src_region'] = df[src_ip_col].map(lambda ip: geo_lookup[ip]['src_region'])
    df['src_city'] = df[src_ip_col].map(lambda ip: geo_lookup[ip]['src_city'])
    df['src_latitude'] = df[src_ip_col].map(lambda ip: geo_lookup[ip]['src_latitude'])
    df['src_longitude'] = df[src_ip_col].map(lambda ip: geo_lookup[ip]['src_longitude'])
    df['src_isp'] = df[src_ip_col].map(lambda ip: geo_lookup[ip]['src_isp'])
    
    return df
    
    
    
def calculate_dst_ip_geolocation_features(df, dst_ip_col='destination_ip', rate_limit_delay=0.1):    
    """
    Creates features:
    - dst_ip_type: IPv4 or IPv6
    - dst_continent: Continent name
    - dst_country: Country name
    - dst_region: State/province 
    - dst_city: City name 
    - dst_latitude: Geographic latitude
    - dst_longitude: Geographic longitude
    - dst_isp: Internet Service Provider name
    """

    df = df.copy()
    
    # Get unique IPs to minimize API calls
    unique_ips = df[dst_ip_col].unique()
    
    # Create lookup dictionary for unique IPs
    geo_lookup = {}
        
    print(f"Fetching geolocation data for {len(unique_ips)} unique destination IPs...")
        
    for i, ip in enumerate(unique_ips):
        # Fetch IP info
        ip_info = calculate_ip_info(ip)
        
        # Extract only the specified fields from response
        if ip_info.get("success", False):
            geo_lookup[ip] = {
                'dst_ip_type': ip_info.get('type'),
                'dst_continent': ip_info.get('continent'),
                'dst_country': ip_info.get('country'),
                'dst_region': ip_info.get('region'),
                'dst_city': ip_info.get('city'),
                'dst_latitude': ip_info.get('latitude'),
                'dst_longitude': ip_info.get('longitude'),
                'dst_isp': ip_info.get('connection', {}).get('isp') if isinstance(ip_info.get('connection'), dict) else None,
            }
        else:
            # API call failed or IP not found
            geo_lookup[ip] = {
                'dst_ip_type': None,
                'dst_continent': None,
                'dst_country': None,
                'dst_region': None,
                'dst_city': None,
                'dst_latitude': None,
                'dst_longitude': None,
                'dst_isp': None,
            }
        
        # Rate limiting: wait between requests
        if i < len(unique_ips) - 1:  # Don't wait after last request
            time.sleep(rate_limit_delay)
        
        # Progress indicator
        if (i + 1) % 10 == 0:
            print(f"Processed {i + 1}/{len(unique_ips)} destination IPs...")
    
    print("Destination IP geolocation lookup complete!")
    
    # Map geolocation data back to dataframe
    df['dst_ip_type'] = df[dst_ip_col].map(lambda ip: geo_lookup[ip]['dst_ip_type'])
    df['dst_continent'] = df[dst_ip_col].map(lambda ip: geo_lookup[ip]['dst_continent'])
    df['dst_country'] = df[dst_ip_col].map(lambda ip: geo_lookup[ip]['dst_country'])
    df['dst_region'] = df[dst_ip_col].map(lambda ip: geo_lookup[ip]['dst_region'])
    df['dst_city'] = df[dst_ip_col].map(lambda ip: geo_lookup[ip]['dst_city'])
    df['dst_latitude'] = df[dst_ip_col].map(lambda ip: geo_lookup[ip]['dst_latitude'])
    df['dst_longitude'] = df[dst_ip_col].map(lambda ip: geo_lookup[ip]['dst_longitude'])
    df['dst_isp'] = df[dst_ip_col].map(lambda ip: geo_lookup[ip]['dst_isp'])
    
    return df