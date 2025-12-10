import pandas as pd


class DataFrameFormatterSuricata:

    def __init__(self, suricata_df, list_of_features_to_rename: list):
        self.suricata_df = suricata_df
        self.list_of_features_to_rename = list_of_features_to_rename

    def format_suricata_df(self):
        # Create a copy to work with
        suricata_df_renamed = self.suricata_df.copy()

        # Extract flow data first (before renaming)
        suricata_df_renamed = self._extract_flow_data(suricata_df_renamed)

        # Now rename columns
        suricata_df_renamed = suricata_df_renamed.rename(
            columns={
                "src_ip": self.list_of_features_to_rename[0],  # source_ip
                "dest_ip": self.list_of_features_to_rename[1],  # destination_ip
                "src_port": self.list_of_features_to_rename[2],  # source_port
                "dest_port": self.list_of_features_to_rename[3],  # destination_port
                "timestamp": self.list_of_features_to_rename[4],  # timestamp_start
                "proto": self.list_of_features_to_rename[5],  # transport_protocol
                "app_proto": self.list_of_features_to_rename[6],  # application_protocol
                # duration, bytes_sent, bytes_received, pkts_sent, pkts_received are already created
                "direction": self.list_of_features_to_rename[12],  # direction
            }
        )

        # Format timestamp
        suricata_df_renamed[self.list_of_features_to_rename[4]] = pd.to_datetime(
            suricata_df_renamed[self.list_of_features_to_rename[4]]
        ).dt.tz_localize(None)

        # Format duration as float
        suricata_df_renamed[self.list_of_features_to_rename[7]] = suricata_df_renamed[
            self.list_of_features_to_rename[7]
        ].astype(float)

        # Format protocol to lowercase
        suricata_df_renamed[self.list_of_features_to_rename[5]] = suricata_df_renamed[
            self.list_of_features_to_rename[5]
        ].str.lower()

        # Handle NaN values
        suricata_df_renamed.loc[
            suricata_df_renamed[self.list_of_features_to_rename[0]].isna(),
            self.list_of_features_to_rename[0],
        ] = "0.0.0.0"
        suricata_df_renamed.loc[
            suricata_df_renamed[self.list_of_features_to_rename[1]].isna(),
            self.list_of_features_to_rename[1],
        ] = "0.0.0.0"
        suricata_df_renamed.loc[
            suricata_df_renamed[self.list_of_features_to_rename[2]].isna(),
            self.list_of_features_to_rename[2],
        ] = 0.0
        suricata_df_renamed.loc[
            suricata_df_renamed[self.list_of_features_to_rename[3]].isna(),
            self.list_of_features_to_rename[3],
        ] = 0.0
        suricata_df_renamed.loc[
            suricata_df_renamed[self.list_of_features_to_rename[5]].isna(),
            self.list_of_features_to_rename[5],
        ] = "unknown"
        suricata_df_renamed.loc[
            suricata_df_renamed[self.list_of_features_to_rename[6]].isna(),
            self.list_of_features_to_rename[6],
        ] = "unknown"
        suricata_df_renamed.loc[
            suricata_df_renamed[self.list_of_features_to_rename[12]].isna(),
            self.list_of_features_to_rename[12],
        ] = "unknown"

        # ports in int
        suricata_df_renamed[self.list_of_features_to_rename[2]] = pd.to_numeric(
            suricata_df_renamed[self.list_of_features_to_rename[2]], errors="coerce"
        ).astype("Int64")
        suricata_df_renamed[self.list_of_features_to_rename[3]] = pd.to_numeric(
            suricata_df_renamed[self.list_of_features_to_rename[3]], errors="coerce"
        ).astype("Int64")

        # Add label columns
        suricata_df_renamed[self.list_of_features_to_rename[13]] = "malicious"

        # Standardize direction values
        suricata_df_renamed[self.list_of_features_to_rename[12]] = suricata_df_renamed[
            self.list_of_features_to_rename[12]
        ].str.replace("to_server", "L2R", regex=False)
        suricata_df_renamed[self.list_of_features_to_rename[12]] = suricata_df_renamed[
            self.list_of_features_to_rename[12]
        ].str.replace("to_client", "R2L", regex=False)

        # Select only the required features in correct order
        final_features = self.list_of_features_to_rename
        suricata_df_renamed = suricata_df_renamed[final_features]

        return suricata_df_renamed

    def _extract_flow_data(self, df):
        """Extract nested flow data and calculate derived features"""

        # Initialize new columns with default values
        df["bytes_sent"] = 0
        df["bytes_received"] = 0
        df["pkts_sent"] = 0
        df["pkts_received"] = 0
        df["duration"] = 0.0
        df["flow_start"] = None

        # Process each row
        for idx, row in df.iterrows():
            flow_data = row.get("flow")

            # Skip if flow data is NaN or None
            if pd.isna(flow_data) or flow_data is None:
                continue

            try:
                # Extract bytes and packets
                bytes_toserver = flow_data.get("bytes_toserver", 0)
                bytes_toclient = flow_data.get("bytes_toclient", 0)
                pkts_toserver = flow_data.get("pkts_toserver", 0)
                pkts_toclient = flow_data.get("pkts_toclient", 0)

                # Assign based on direction or use a default mapping
                # Typically: toserver = sent (from client), toclient = received (from server)
                df.at[idx, "bytes_sent"] = bytes_toserver
                df.at[idx, "bytes_received"] = bytes_toclient
                df.at[idx, "pkts_sent"] = pkts_toserver
                df.at[idx, "pkts_received"] = pkts_toclient

                # Extract flow start time for duration calculation
                flow_start = flow_data.get("start")
                if flow_start:
                    df.at[idx, "flow_start"] = flow_start

            except Exception as e:
                print(f"Error processing flow data at index {idx}: {e}")
                continue

        # Calculate duration (timestamp - flow.start)
        df = self._calculate_duration(df)

        return df

    def _calculate_duration(self, df):
        """Calculate duration as difference between timestamp and flow.start"""

        for idx, row in df.iterrows():
            try:
                # Get main timestamp
                main_timestamp = row.get("timestamp")
                flow_start = row.get("flow_start")

                if pd.notna(main_timestamp) and pd.notna(flow_start):
                    # Convert to datetime objects
                    main_dt = pd.to_datetime(main_timestamp)
                    flow_dt = pd.to_datetime(flow_start)

                    # Calculate duration in seconds
                    duration = (main_dt - flow_dt).total_seconds()
                    df.at[idx, "duration"] = max(0, duration)  # Ensure non-negative

            except Exception as e:
                print(f"Error calculating duration at index {idx}: {e}")
                df.at[idx, "duration"] = 0.0

        # Clean up temporary column
        if "flow_start" in df.columns:
            df = df.drop("flow_start", axis=1)

        return df
