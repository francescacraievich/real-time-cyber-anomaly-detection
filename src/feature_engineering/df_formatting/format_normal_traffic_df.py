import pandas as pd


class DataFrameFormatterNormalTraffic:

    def __init__(self, normal_traffic_df, list_of_features_to_rename: list):
        self.normal_traffic_df = normal_traffic_df
        self.list_of_features_to_rename = list_of_features_to_rename

    def format_normal_traffic_df(self):

        # Create a copy to work with
        normal_df_renamed = self.normal_traffic_df.copy()

        # Calculate duration first (before renaming)
        normal_df_renamed = self._calculate_duration(normal_df_renamed)

        # Rename columns to match unified schema
        normal_df_renamed = normal_df_renamed.rename(
            columns={
                "source": self.list_of_features_to_rename[0],  # source_ip
                "destination": self.list_of_features_to_rename[1],  # destination_ip
                "sourcePort": self.list_of_features_to_rename[2],  # source_port
                "destinationPort": self.list_of_features_to_rename[
                    3
                ],  # destination_port
                "startDateTime": self.list_of_features_to_rename[4],  # timestamp_start
                "protocolName": self.list_of_features_to_rename[
                    5
                ],  # transport_protocol
                "appName": self.list_of_features_to_rename[6],  # application_protocol
                # duration is already created                                    # duration [7]
                "totalSourceBytes": self.list_of_features_to_rename[8],  # bytes_sent
                "totalDestinationBytes": self.list_of_features_to_rename[
                    9
                ],  # bytes_received
                "totalSourcePackets": self.list_of_features_to_rename[10],  # pkts_sent
                "totalDestinationPackets": self.list_of_features_to_rename[
                    11
                ],  # pkts_received
                "direction": self.list_of_features_to_rename[12],  # direction
                "Label": self.list_of_features_to_rename[13],  # label
            }
        )

        # remove '_ip' from protocolName
        normal_df_renamed[self.list_of_features_to_rename[5]] = normal_df_renamed[
            self.list_of_features_to_rename[5]
        ].str.replace("_ip", "", regex=False)

        # Convert application_protocol to lowercase
        normal_df_renamed[self.list_of_features_to_rename[6]] = normal_df_renamed[
            self.list_of_features_to_rename[6]
        ].str.lower()

        # Clean and validate data
        normal_df_renamed = self._clean_data(normal_df_renamed)

        # Select only the required features in correct order
        final_features = self.list_of_features_to_rename
        normal_df_renamed = normal_df_renamed[final_features]

        return normal_df_renamed

    def _calculate_duration(self, df):
        """Calculate duration from startDateTime and stopDateTime"""

        # Convert to datetime
        df["startDateTime"] = pd.to_datetime(df["startDateTime"], errors="coerce")
        df["stopDateTime"] = pd.to_datetime(df["stopDateTime"], errors="coerce")

        # Calculate duration in seconds
        df["duration"] = (df["stopDateTime"] - df["startDateTime"]).dt.total_seconds()

        # Handle negative or NaN durations
        df["duration"] = df["duration"].fillna(0)
        df["duration"] = df["duration"].clip(lower=0)  # No negative durations

        return df

    def _clean_data(self, df):
        """Clean and validate the data"""

        # Handle missing values with appropriate defaults
        numeric_columns = [
            self.list_of_features_to_rename[2],  # source_port
            self.list_of_features_to_rename[3],  # destination_port
            self.list_of_features_to_rename[7],  # duration
            self.list_of_features_to_rename[8],  # bytes_sent
            self.list_of_features_to_rename[9],  # bytes_received
            self.list_of_features_to_rename[10],  # pkts_sent
            self.list_of_features_to_rename[11],  # pkts_received
        ]

        # Fill numeric NaN values with 0
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # Handle string columns
        string_columns = [
            self.list_of_features_to_rename[0],  # source_ip
            self.list_of_features_to_rename[1],  # destination_ip
            self.list_of_features_to_rename[5],  # transport_protocol
            self.list_of_features_to_rename[6],  # application_protocol
            self.list_of_features_to_rename[12],  # direction
        ]

        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].fillna("unknown").astype(str)

        # Handle label - convert to numeric (0 for normal traffic)
        if self.list_of_features_to_rename[13] in df.columns:
            # Normal traffic should have label = "benign"
            df[self.list_of_features_to_rename[13]] = "benign"

        # Ensure proper data types
        df[self.list_of_features_to_rename[2]] = df[
            self.list_of_features_to_rename[2]
        ].astype(
            int
        )  # source_port
        df[self.list_of_features_to_rename[3]] = df[
            self.list_of_features_to_rename[3]
        ].astype(
            int
        )  # destination_port
        df[self.list_of_features_to_rename[8]] = df[
            self.list_of_features_to_rename[8]
        ].astype(
            int
        )  # bytes_sent
        df[self.list_of_features_to_rename[9]] = df[
            self.list_of_features_to_rename[9]
        ].astype(
            int
        )  # bytes_received
        df[self.list_of_features_to_rename[10]] = df[
            self.list_of_features_to_rename[10]
        ].astype(
            int
        )  # pkts_sent
        df[self.list_of_features_to_rename[11]] = df[
            self.list_of_features_to_rename[11]
        ].astype(
            int
        )  # pkts_received
        # df[self.list_of_features_to_rename[13]] = df[self.list_of_features_to_rename[13]].astype(int) # label

        return df
