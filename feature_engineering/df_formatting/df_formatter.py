from feature_engineering.df_initializing.df_initializer import DataFrameInitializer
import pandas as pd

class DataFrameFormatter():

    def __init__(self, cowrie_df, dionea_df, suricata_df):
        self.cowrie_df = cowrie_df
        self.dionea_df = dionea_df
        self.suricata_df = suricata_df
        self.base_features = [
            'source_ip',
            'destination_ip',
            'source_port',
            'destination_port',
            'timestamp', 
            'transport_protocol',
            'application_protocol',
            'label'
        ]
        self.format_all_dfs()

    def format_cowrie_df(self):
        self.cowrie_df[self.base_features[5]] = 'tcp'
        self.cowrie_df[self.base_features[7]] = 'malicious'
        cowrie_df_renamed = self.cowrie_df.rename(columns={
            'src_ip': self.base_features[0],
            'dst_ip': self.base_features[1],
            'src_port': self.base_features[2],
            'dst_port': self.base_features[3],
            'timestamp': self.base_features[4],
            'protocol': self.base_features[6]
            # need to compress the rows in a single entity
        })
        
        # split connect / closed events
        is_connect = cowrie_df_renamed['eventid'].astype(str).str.contains('connect', na=False)
        is_closed = cowrie_df_renamed['eventid'].astype(str).str.contains('closed', na=False)

        conn = cowrie_df_renamed[is_connect].copy()
        closed = cowrie_df_renamed[is_closed].copy()

        # merge on session (outer so sessions with only one side are kept)
        merged = pd.merge(
            conn,
            closed,
            on='session',
            how='outer',
            suffixes=('_connect', '_closed')
        )

        # helper to coalesce connect then closed
        def coalesce(col):
            return merged.get(f"{col}_connect").fillna(merged.get(f"{col}_closed"))

        # build final DataFrame with desired fields
        final = pd.DataFrame({
            'session': merged['session'],
            'source_ip': coalesce(self.base_features[0]),
            'destination_ip': coalesce(self.base_features[1]),
            'source_port': coalesce(self.base_features[2]),
            'destination_port': coalesce(self.base_features[3]),
            'transport_protocol': coalesce(self.base_features[5]),
            'application_protocol': coalesce(self.base_features[6]),
            'label': coalesce(self.base_features[7]),
            'timestamp': merged.get('timestamp_connect'),
            'duration': merged.get('duration_closed').fillna(merged.get('duration_connect'))
        })

        # ensure columns order matches base_features where applicable
        # keep session and timestamp_start/end too
        cols = [
            'session',
            'source_ip', 'destination_ip', 'source_port', 'destination_port',
            'timestamp',
            'transport_protocol', 'application_protocol', 'duration', 'label'
        ]
        final = final.reindex(columns=cols)

        return final

    
    def format_dionea_df(self):
        
        expanded = pd.json_normalize(self.dionea_df['connection'])
        self.dionea_df = pd.concat([self.dionea_df.drop(columns=['connection']), expanded], axis=1)
        print(self.dionea_df.columns)
        
        self.dionea_df[self.base_features[7]] = 'malicious'
        
        dionea_df_renamed = self.dionea_df.rename(columns={
            'src_ip': self.base_features[0],
            'dst_ip': self.base_features[1],
            'src_port': self.base_features[2],
            'dst_port': self.base_features[3],
            'timestamp': self.base_features[4],
            'transport': self.base_features[5],
            'protocol': self.base_features[6]
        })
        return dionea_df_renamed

    def format_suricata_df(self):
        self.suricata_df[self.base_features[7]] = 'malicious'
        suricata_df_renamed = self.suricata_df.rename(columns={
            'src_ip': self.base_features[0],
            'dest_ip': self.base_features[1],
            'src_port': self.base_features[2],
            'dest_port': self.base_features[3],
            'timestamp': self.base_features[4],
            'proto': self.base_features[5],
            'app_proto': self.base_features[6]
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
        # concatenate rows from all sources and keep only base_features (as requested)
        combined_df = pd.concat([
            self.cowrie_df[self.base_features],
            self.dionea_df[self.base_features],
            self.suricata_df[self.base_features]
        ], ignore_index=True, sort=False)
        combined_df = combined_df.loc[:, self.base_features]  # enforce column order
        return combined_df

if __name__ == "__main__":
    df_initializer = DataFrameInitializer(
        cowrie_json='data/cowrie/log/cowrie.json',
        dionea_json='data/dionaea/log/dionaea.json',
        suricata_json='data/suricata/log/suricata.json',
    )
    df_cowrie, df_dionea, df_suricata = df_initializer.initialize_dfs()

    df_formatter = DataFrameFormatter(df_cowrie, df_dionea, df_suricata)

    print("Formatted Cowrie DataFrame:" , df_formatter.cowrie_df['label'].head())
    print("Formatted Dionea DataFrame:" , df_formatter.dionea_df['label'].head())
    print("Formatted Suricata DataFrame:" , df_formatter.suricata_df['label'].head())

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

    print(df_formatter.cowrie_df.head())