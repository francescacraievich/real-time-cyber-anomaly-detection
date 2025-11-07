from df_initializer import DataFrameInitializer

class DataFrameFormatter():

    def __init__(self, cowrie_df, dionea_df, suricata_df, tanner_df):
        self.cowrie_df = cowrie_df
        self.dionea_df = dionea_df
        self.suricata_df = suricata_df
        self.tanner_df = tanner_df

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

    def format_tanner_df(self):
        tanner_df_renamed = self.tanner_df.rename(columns={
            'timestamp': 'event_time'
        })
        return tanner_df_renamed
    
    def format_all_NaN_columns(self):
        dataframes = [self.cowrie_df, self.dionea_df, self.suricata_df, self.tanner_df]
        for df in dataframes:
            df = df.loc[:, df.isnull().mean() > 0.5]
        return dataframes
    

if __name__ == "__main__":
    df_initializer = DataFrameInitializer(
        cowrie_json='data/cowrie/log/cowrie.json',
        dionea_json='data/dionaea/log/dionaea.json',
        suricata_json='data/suricata/log/suricata.json',
        tanner_json='data/tanner/log/tanner.json'
    )
    df_cowrie, df_dionea, df_suricata, df_tanner = df_initializer.initialize_dfs()

    df_formatter = DataFrameFormatter(df_cowrie, df_dionea, df_suricata, df_tanner)
    cowrie_df_renamed = df_formatter.format_cowrie_df()
    dionea_df_renamed = df_formatter.format_dionea_df()
    suricata_df_renamed = df_formatter.format_suricata_df()
    tanner_df_renamed = df_formatter.format_tanner_df()

    print("Formatted Cowrie DataFrame:" , cowrie_df_renamed['event_time'].head())
    print("Formatted Dionea DataFrame:" , dionea_df_renamed['event_time'].head())
    print("Formatted Suricata DataFrame:" , suricata_df_renamed['event_time'].head())
    print("Formatted Tanner DataFrame:" , tanner_df_renamed['event_time'].head())
