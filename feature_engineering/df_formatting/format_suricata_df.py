

import pandas as pd

class DataFrameFormatterSuricata():
    
    def __init__(self, suricata_df, list_of_features_to_rename: list):
        self.suricata_df = suricata_df
        self.list_of_features_to_rename = list_of_features_to_rename
        
    def format_suricata_df(self):
        self.suricata_df[self.list_of_features_to_rename[7]] = 'malicious'
        suricata_df_renamed = self.suricata_df.rename(columns={
            'src_ip': self.list_of_features_to_rename[0],
            'dest_ip': self.list_of_features_to_rename[1],
            'src_port': self.list_of_features_to_rename[2],
            'dest_port': self.list_of_features_to_rename[3],
            'timestamp': self.list_of_features_to_rename[4],
            'proto': self.list_of_features_to_rename[5],
            'app_proto': self.list_of_features_to_rename[6]
        })
        return suricata_df_renamed