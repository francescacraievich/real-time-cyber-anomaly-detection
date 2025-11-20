
from df_initializing.handler_init_dfs import DataFrameInitializer
import pandas as pd
import sys
import os
from deprecated import deprecated
from format_normal_traffic import DataFrameFormatterNormalTraffic
from format_suricata_df import DataFrameFormatterSuricata

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


class DataFrameFormatter():

    def __init__(self, suricata_df, normal_traffic_df):
        self.suricata_df = suricata_df
        self.normal_traffic_df = normal_traffic_df
        self.base_features = [
            'source_ip',
            'destination_ip',
            'source_port',
            'destination_port',
            'timestamp_start',
            'transport_protocol',
            'application_protocol',
            'duration',
            'bytes_sent',
            'bytes_received',
            'pkts_sent',
            'pkts_received',
            'direction',
            'label',
            
        ]
        self.format_all_dfs()


    def format_all_dfs(self):
        self.suricata_df = DataFrameFormatterSuricata(
            self.suricata_df, self.base_features).format_suricata_df()
        self.normal_traffic_df = DataFrameFormatterNormalTraffic(
            self.normal_traffic_df, self.base_features).format_normal_traffic_df()

    def unite_honeypot_and_normal_traffic_dfs(self):
        # concatenate rows from all sources and keep only base_features (as requested)
        combined_df = pd.concat([
            self.suricata_df[self.base_features],
            self.normal_traffic_df[self.base_features]
        ], ignore_index=True, sort=False)
        # enforce column order
        combined_df = combined_df.loc[:, self.base_features]
        return combined_df


if __name__ == "__main__":

    df_initializer = DataFrameInitializer(
        cowrie_json_path='data/cowrie/log/cowrie.json',
        dionea_json_path='data/dionaea/log/dionaea.json',
        suricata_json_path='data/suricata/log/suricata.json',
        normal_traffic_json_path="data/normal_traffic/benign_traffic_fixed.json"
    )

    df_cowrie, df_dionea, df_suricata, df_normal_traffic = df_initializer.initialize_dfs(
        sample_size=1000)

    df_formatter = DataFrameFormatter(
        df_cowrie, df_dionea, df_suricata, df_normal_traffic)

    print("Formatted Cowrie DataFrame:",
          df_formatter.cowrie_df['label'].head())
    print("Formatted Dionea DataFrame:",
          df_formatter.dionea_df['label'].head())
    print("Formatted Suricata DataFrame:",
          df_formatter.suricata_df['label'].head())
    print("Formatted Normal Traffic DataFrame:",
          df_formatter.normal_traffic_df['label'].head())

    print(df_formatter.cowrie_df.shape[1])
    print(df_formatter.dionea_df.shape[1])
    print(df_formatter.suricata_df.shape[1])
    print(df_formatter.normal_traffic_df.shape[1])

    print("Cowrie Columns:", df_formatter.cowrie_df.columns)
    print("Dionea Columns:", df_formatter.dionea_df.columns)
    print("Suricata Columns:", df_formatter.suricata_df.columns)
    print("Normal Traffic Columns:", df_formatter.normal_traffic_df.columns)

    combined_df = df_formatter.unite_all_dfs()
    print("Combined DataFrame:", combined_df.head())
    print("Combined DataFrame shape:", combined_df.shape)
    print("Combined DataFrame columns:", combined_df.columns)

    print(df_formatter.cowrie_df.columns)
