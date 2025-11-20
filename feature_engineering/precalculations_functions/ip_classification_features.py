import pandas as pd
import numpy as np
import ipaddress


def is_private_ip(ip):
    """
    Check if an IP address is private (RFC1918).
    """
    try:
        return ipaddress.ip_address(ip).is_private
    except (ValueError, AttributeError):
        return False  # Invalid IP or NaN
    
    
def calculate_ip_classification_features(df, src_ip_col='source_ip', 
                                                 dst_ip_col='destination_ip'):
    """
    Calculate:
    - src_is_private: 1 if source IP is private, 0 otherwise
    - dst_is_private: 1 if destination IP is private, 0 otherwise
    - is_internal: 1 if both IPs are private, 0 otherwise
    """
    df = df.copy()
    
    df['src_is_private'] = df[src_ip_col].apply(is_private_ip).astype(int)
    df['dst_is_private'] = df[dst_ip_col].apply(is_private_ip).astype(int)
    df['is_internal'] = (
        (df['src_is_private'] == 1) & 
        (df['dst_is_private'] == 1)
    ).astype(int)
    
    return df