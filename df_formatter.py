from df_initializer import DataFrameInitializer
import pandas as pd

class DataFrameFormatter():

    def __init__(self, cowrie_df, dionea_df, suricata_df):
        self.cowrie_df = cowrie_df
        self.dionea_df = dionea_df
        self.suricata_df = suricata_df
        self.format_all_dfs()

    def format_cowrie_df(self):
        cowrie_df_renamed = self.cowrie_df.rename(columns={
            'src_ip': 'source_ip',
            'dst_ip': 'destination_ip',
            'src_port': 'source_port',
            'dst_port': 'destination_port',
            'timestamp': 'event_time'
        })
        return cowrie_df_renamed
    
    def format_dionea_df(self):
        dionea_df_renamed = self.dionea_df.rename(columns={
            'src_ip': 'source_ip',
            'dst_ip': 'destination_ip',
            'src_port': 'source_port',
            'dst_port': 'destination_port',
            'timestamp': 'event_time'
        })
        return dionea_df_renamed

    def format_suricata_df(self):
        suricata_df_renamed = self.suricata_df.rename(columns={
            'src_ip': 'source_ip',
            'dest_ip': 'destination_ip',
            'src_port': 'source_port',
            'dest_port': 'destination_port',
            'timestamp': 'event_time'
        })
        return suricata_df_renamed
    
    def format_all_NaN_columns(self, threshold: float = 0.8):
        dataframes = [self.cowrie_df, self.dionea_df, self.suricata_df]
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
        self.cowrie_df = self.format_cowrie_df()
        self.dionea_df = self.format_dionea_df()
        self.suricata_df = self.format_suricata_df()
        self.cowrie_df, self.dionea_df, self.suricata_df = self.format_all_NaN_columns()

    def unite_all_dfs(self):
        combined_df = pd.merge(self.cowrie_df, self.dionea_df, on=['source_ip', 'destination_ip', 'source_port', 'destination_port', 'event_time'], how='outer')      
        combined_df = pd.merge(combined_df, self.suricata_df, on=['source_ip', 'destination_ip', 'source_port', 'destination_port', 'event_time'], how='outer')
        return combined_df

if __name__ == "__main__":
    df_initializer = DataFrameInitializer(
        cowrie_json='data/cowrie/log/cowrie.json',
        dionea_json='data/dionaea/log/dionaea.json',
        suricata_json='data/suricata/log/suricata.json',
    )
    df_cowrie, df_dionea, df_suricata = df_initializer.initialize_dfs()

    df_formatter = DataFrameFormatter(df_cowrie, df_dionea, df_suricata)

    print("Formatted Cowrie DataFrame:" , df_formatter.cowrie_df['event_time'].head())
    print("Formatted Dionea DataFrame:" , df_formatter.dionea_df['event_time'].head())
    print("Formatted Suricata DataFrame:" , df_formatter.suricata_df['event_time'].head())

    print(df_formatter.cowrie_df.shape[1])
    print(df_formatter.dionea_df.shape[1])
    print(df_formatter.suricata_df.shape[1])

    print("Cowrie Columns:", df_formatter.cowrie_df.columns)
    print("Dionea Columns:", df_formatter.dionea_df.columns)
    print("Suricata Columns:", df_formatter.suricata_df.columns)

    combined_df = df_formatter.unite_all_dfs()
    print("Combined DataFrame:" , combined_df.head())
    print("Combined DataFrame shape:", combined_df.shape)
    print("Combined DataFrame columns:", combined_df.columns)
