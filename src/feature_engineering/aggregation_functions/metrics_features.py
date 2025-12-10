import numpy as np


def calculate_total_events_processed(
    df, timestamp_col="timestamp_start", window_minutes=60
):
    """
    Calculate total events processed per time window
    """

    df = df.copy()

    # Create time window identifier (floor to nearest window)
    df["time_window"] = df[timestamp_col].dt.floor(f"{window_minutes}min")

    # Count events per window
    window_counts = (
        df.groupby("time_window").size().reset_index(name="events_in_window")
    )

    # Merge back to original dataframe
    df = df.merge(window_counts, on="time_window", how="left")

    # Drop temporary column
    df = df.drop(columns=["time_window"])

    return df


def calculate_total_anomalous_events(
    df,
    timestamp_col="timestamp_start",
    label_col="label",
    malicious_label="malicious",
    window_minutes=60,
):
    """
    Calculate total anomalous events per time window
    """

    df = df.copy()

    # Create time window identifier (floor to nearest window)
    df["time_window"] = df[timestamp_col].dt.floor(f"{window_minutes}min")

    # Count events per window
    malicious_df = df[df[label_col] == malicious_label]
    malicious_counts = (
        malicious_df.groupby("time_window")
        .size()
        .reset_index(name="malicious_events_in_window")
    )

    # Merge back to original dataframe
    df = df.merge(malicious_counts, on="time_window", how="left")

    # Drop temporary column
    df = df.drop(columns=["time_window"])

    return df


def calculate_total_unique_malicious_ips(
    df,
    timestamp_col="timestamp_start",
    source_ip_col="source_ip",
    label_col="label",
    malicious_label="malicious",
    window_minutes=60,
):
    """
    Calculate number of unique source IPs in malicious events per time window.
    """

    df = df.copy()

    # Create time window identifier
    df["time_window"] = df[timestamp_col].dt.floor(f"{window_minutes}min")

    # Filter malicious events only
    malicious_df = df[df[label_col] == malicious_label]

    # Count unique source IPs per window
    unique_ips = (
        malicious_df.groupby("time_window")[source_ip_col]
        .nunique()
        .reset_index(name="unique_malicious_ips")
    )

    # Merge back to original dataframe
    df = df.merge(unique_ips, on="time_window", how="left")

    # Fill NaN (windows with no malicious events) with 0
    df["unique_malicious_ips"] = df["unique_malicious_ips"].fillna(0).astype(int)

    # Drop temporary column
    df = df.drop(columns=["time_window"])

    return df


def calculate_trend_percentage_change(
    df, timestamp_col="timestamp_start", window_minutes=60
):
    """
    Calculate percentage change from previous time window.
    """

    df = df.copy()
    df["time_window"] = df[timestamp_col].dt.floor(f"{window_minutes}min")

    # Aggregate metrics per window
    window_stats = df.groupby("time_window")["label"].count().reset_index()
    window_stats.columns = ["time_window", "events_in_window"]

    # Malicious events
    malicious_df = df[df["label"] == "malicious"]
    malicious_stats = (
        malicious_df.groupby("time_window")
        .size()
        .reset_index(name="malicious_events_in_window")
    )
    window_stats = window_stats.merge(malicious_stats, on="time_window", how="left")
    window_stats["malicious_events_in_window"] = window_stats[
        "malicious_events_in_window"
    ].fillna(0)

    # Sort by time
    window_stats = window_stats.sort_values("time_window")

    # Calculate percentage change: (current - previous) / previous * 100
    window_stats["events_pct_change"] = (
        window_stats["events_in_window"].pct_change() * 100
    )
    window_stats["malicious_events_pct_change"] = (
        window_stats["malicious_events_in_window"].pct_change() * 100
    )

    # Replace inf (division by zero) with 0
    window_stats = window_stats.replace([np.inf, -np.inf], 0)
    window_stats["events_pct_change"] = window_stats["events_pct_change"].fillna(0)
    window_stats["malicious_events_pct_change"] = window_stats[
        "malicious_events_pct_change"
    ].fillna(0)

    # Create burst indicator (e.g., >50% increase)
    window_stats["burst_indicator"] = (window_stats["events_pct_change"] > 50).astype(
        int
    )

    # Merge back
    df = df.merge(
        window_stats[
            [
                "time_window",
                "events_pct_change",
                "malicious_events_pct_change",
                "burst_indicator",
            ]
        ],
        on="time_window",
        how="left",
    )

    df = df.drop(columns=["time_window"])

    return df


def calculate_total_events_for_dst_ports(
    df,
    timestamp_col="timestamp_start",
    destination_port_col="destination_port",
    window_minutes=60,
):
    """
    Calculate number of events for a dst_port in a timewindow.
    """

    df = df.copy()

    # Create time window identifier
    df["time_window"] = df[timestamp_col].dt.floor(f"{window_minutes}min")

    # Count events per (time_window, dst_port) combination
    port_counts = (
        df.groupby(["time_window", destination_port_col])
        .size()
        .reset_index(name="events_to_dst_port")
    )

    # Merge back to original dataframe
    df = df.merge(port_counts, on=["time_window", destination_port_col], how="left")

    # Fill NaN with 0 (shouldn't happen, but safe)
    df["events_to_dst_port"] = df["events_to_dst_port"].fillna(0).astype(int)

    # Drop temporary column
    df = df.drop(columns=["time_window"])

    return df


def calculate_total_malicious_events_per_protocol(
    df,
    timestamp_col="timestamp_start",
    app_protocol_col="application_protocol",
    label_col="label",
    malicious_label="malicious",
    window_minutes=60,
):
    """
    Count malicious events per protocol within time windows.
    Helps identify which protocols are being exploited for attacks.
    """

    df = df.copy()

    # Create time window identifier
    df["time_window"] = df[timestamp_col].dt.floor(f"{window_minutes}min")

    # === 1. Count total events per (time_window, protocol) ===
    total_counts = (
        df.groupby(["time_window", app_protocol_col])
        .size()
        .reset_index(name="total_events_for_protocol")
    )

    # === 2. Count malicious events per (time_window, protocol) ===
    malicious_df = df[df[label_col] == malicious_label]
    malicious_counts = (
        malicious_df.groupby(["time_window", app_protocol_col])
        .size()
        .reset_index(name="malicious_events_for_protocol")
    )

    # === 3. Merge statistics ===
    protocol_stats = total_counts.merge(
        malicious_counts, on=["time_window", app_protocol_col], how="left"
    )
    protocol_stats["malicious_events_for_protocol"] = (
        protocol_stats["malicious_events_for_protocol"].fillna(0).astype(int)
    )

    # === 4. Calculate malicious ratio ===
    protocol_stats["malicious_ratio_for_protocol"] = (
        protocol_stats["malicious_events_for_protocol"]
        / protocol_stats["total_events_for_protocol"]
        * 100
    )

    # === 5. Merge back to original dataframe ===
    df = df.merge(protocol_stats, on=["time_window", app_protocol_col], how="left")

    # Fill NaN with 0
    df["total_events_for_protocol"] = (
        df["total_events_for_protocol"].fillna(0).astype(int)
    )
    df["malicious_events_for_protocol"] = (
        df["malicious_events_for_protocol"].fillna(0).astype(int)
    )
    df["malicious_ratio_for_protocol"] = df["malicious_ratio_for_protocol"].fillna(0)

    # Drop temporary column
    df = df.drop(columns=["time_window"])

    return df
