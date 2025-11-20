import numpy as np
import pandas as pd


def calculate_rate_features(df, bytes_sent_col='bytes_sent', 
                           bytes_received_col='bytes_received',
                           pkts_sent_col='pkts_sent',
                           pkts_received_col='pkts_received',
                           duration_col='duration'):
    """
    Calculate rate-based features: bytes/sec, packets/sec, bytes/packet
    """
    df = df.copy()
    
    # Calculate totals
    df['total_bytes'] = df[bytes_sent_col] + df[bytes_received_col]
    df['total_packets'] = df[pkts_sent_col] + df[pkts_received_col]
    
    # Calculate rates (avoid division by zero)
    df['bytes_per_second'] = np.where(
        df[duration_col] > 0,
        df['total_bytes'] / df[duration_col],
        0
    )
    
    df['packets_per_second'] = np.where(
        df[duration_col] > 0,
        df['total_packets'] / df[duration_col],
        0
    )
    
    df['bytes_per_packet'] = np.where(
        df['total_packets'] > 0,
        df['total_bytes'] / df['total_packets'],
        0
    )
    
    df = df.drop(columns=['total_bytes', 'total_packets'])
    
    return df