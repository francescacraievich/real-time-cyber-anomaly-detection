import numpy as np


def calculate_ratio_features(
    df,
    bytes_sent_col="bytes_sent",
    bytes_received_col="bytes_received",
    pkts_sent_col="pkts_sent",
    pkts_received_col="pkts_received",
):
    """
    Calculate ratio-based features: bytes_sent/total_bytes, packets_sent/total_packets
    """
    df = df.copy()

    # Calculate totals
    df["total_bytes"] = df[bytes_sent_col] + df[bytes_received_col]
    df["total_packets"] = df[pkts_sent_col] + df[pkts_received_col]

    # Calculate ratios (avoid division by zero)
    df["bytes_sent_ratio"] = np.where(
        df["total_bytes"] > 0, df[bytes_sent_col] / df["total_bytes"], 0
    )

    df["packets_sent_ratio"] = np.where(
        df["total_packets"] > 0, df[pkts_sent_col] / df["total_packets"], 0
    )

    df = df.drop(columns=["total_bytes", "total_packets"])

    return df
