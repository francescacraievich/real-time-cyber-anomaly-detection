import numpy as np
import pandas as pd


def is_port_common(port):
    """
    Check if port is common
    """
    try:
        return port in [80, 443, 22, 21, 25, 53, 3389]
    except (ValueError, AttributeError):
        return False  # Invalid port or NaN


def calculate_port_categorization(df, dst_port_col="destination_port"):
    """
    Calculate:
    - dst_port_is_common: 1 if port is in [80, 443, 22, 21, 53, 3389]
    """

    df = df.copy()

    df["dst_port_is_common"] = df[dst_port_col].apply(is_port_common).astype(int)

    return df
