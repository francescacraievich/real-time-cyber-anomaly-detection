
import pandas as pd
import sys
import os
from format_normal_traffic import DataFrameFormatterNormalTraffic
from format_cowrie_df import DataFrameFormatterCowrie
from format_dionea_df import DataFrameFormatterDionea
from format_suricata_df import DataFrameFormatterSuricata

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from df_initializing.handler_init_dfs import DataFrameInitializer

class DataFrameFormatter():

    def __init__(self, cowrie_df, dionea_df, suricata_df, normal_traffic_df):
        self.cowrie_df = cowrie_df
        self.dionea_df = dionea_df
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
            'label',
            'duration'
        ]
        self.format_all_dfs()


    
    def format_all_NaN_columns(self, threshold: float = 0.8):
        dataframes = [self.cowrie_df, self.dionea_df, self.suricata_df, self.normal_traffic_df]
        filtered = []
        for df in dataframes:
            if df is None:
                filtered.append(df)
                continue
            # keep columns with less than `threshold` fraction missing
            keep_mask = (df.isnull().mean() < threshold).fillna(False)
            filtered.append(df.loc[:, keep_mask])
        return filtered
    
    def format_all_dfs(self):
        self.cowrie_df = DataFrameFormatterCowrie(self.cowrie_df, self.base_features).format_cowrie_df()
        self.dionea_df = DataFrameFormatterDionea(self.dionea_df, self.base_features).format_dionea_df()
        self.suricata_df = DataFrameFormatterSuricata(self.suricata_df, self.base_features).format_suricata_df()
        self.normal_traffic_df = DataFrameFormatterNormalTraffic(self.normal_traffic_df, self.base_features).format_normal_traffic_df()
        self.cowrie_df, self.dionea_df, self.suricata_df, self.normal_traffic_df = self.format_all_NaN_columns()

    def unite_all_dfs(self):
        # concatenate rows from all sources and keep only base_features (as requested)
        combined_df = pd.concat([
            self.cowrie_df[self.base_features],
            self.dionea_df[self.base_features],
            self.suricata_df[self.base_features],
            self.normal_traffic_df[self.base_features]
        ], ignore_index=True, sort=False)
        combined_df = combined_df.loc[:, self.base_features]  # enforce column order
        return combined_df

if __name__ == "__main__":

    df_initializer = DataFrameInitializer(
        cowrie_json_path='data/cowrie/log/cowrie.json',
        dionea_json_path='data/dionaea/log/dionaea.json',
        suricata_json_path='data/suricata/log/suricata.json',
        normal_traffic_json_path="data/normal_traffic/benign_traffic_fixed.json"
    )

    df_cowrie, df_dionea, df_suricata, df_normal_traffic = df_initializer.initialize_dfs(sample_size=1000)

    df_formatter = DataFrameFormatter(df_cowrie, df_dionea, df_suricata, df_normal_traffic)

    print("Formatted Cowrie DataFrame:" , df_formatter.cowrie_df['label'].head())
    print("Formatted Dionea DataFrame:" , df_formatter.dionea_df['label'].head())
    print("Formatted Suricata DataFrame:" , df_formatter.suricata_df['label'].head())
    print("Formatted Normal Traffic DataFrame:" , df_formatter.normal_traffic_df['label'].head())

    print(df_formatter.cowrie_df.shape[1])
    print(df_formatter.dionea_df.shape[1])
    print(df_formatter.suricata_df.shape[1])
    print(df_formatter.normal_traffic_df.shape[1])

    print("Cowrie Columns:", df_formatter.cowrie_df.columns)
    print("Dionea Columns:", df_formatter.dionea_df.columns)
    print("Suricata Columns:", df_formatter.suricata_df.columns)
    print("Normal Traffic Columns:", df_formatter.normal_traffic_df.columns)

    combined_df = df_formatter.unite_all_dfs()
    print("Combined DataFrame:" , combined_df.head())
    print("Combined DataFrame shape:", combined_df.shape)
    print("Combined DataFrame columns:", combined_df.columns)

    print(df_formatter.cowrie_df.columns)