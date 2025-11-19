

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
        
        suricata_df_renamed[self.list_of_features_to_rename[4]] = pd.to_datetime(
        suricata_df_renamed[self.list_of_features_to_rename[4]]
        ).dt.tz_localize(None) 
        
        suricata_df_renamed[self.list_of_features_to_rename[8]] = 0
        
        suricata_df_renamed[self.list_of_features_to_rename[8]] = suricata_df_renamed[self.list_of_features_to_rename[8]].astype(float)
    
        suricata_df_renamed[self.list_of_features_to_rename[5]] = suricata_df_renamed[self.list_of_features_to_rename[5]].str.lower()
        
        suricata_df_renamed.loc[suricata_df_renamed[self.list_of_features_to_rename[0]].isna(), self.list_of_features_to_rename[0]] = "0.0.0.0"
        suricata_df_renamed.loc[suricata_df_renamed[self.list_of_features_to_rename[1]].isna(), self.list_of_features_to_rename[1]] = "0.0.0.0"
        suricata_df_renamed.loc[suricata_df_renamed[self.list_of_features_to_rename[2]].isna(), self.list_of_features_to_rename[2]] = "0.0"
        suricata_df_renamed.loc[suricata_df_renamed[self.list_of_features_to_rename[3]].isna(), self.list_of_features_to_rename[3]] = "0.0"
        suricata_df_renamed.loc[suricata_df_renamed[self.list_of_features_to_rename[5]].isna(), self.list_of_features_to_rename[5]] = "unknown"
        suricata_df_renamed.loc[suricata_df_renamed[self.list_of_features_to_rename[6]].isna(), self.list_of_features_to_rename[6]] = "unknown"
        
        suricata_df_renamed[self.list_of_features_to_rename[2]] = pd.to_numeric(suricata_df_renamed[self.list_of_features_to_rename[2]], errors='coerce').astype('Int64')
        suricata_df_renamed[self.list_of_features_to_rename[3]] = pd.to_numeric(suricata_df_renamed[self.list_of_features_to_rename[3]], errors='coerce').astype('Int64')
        
        suricata_df_renamed["origin_name"] = "suricata"
        
        cols = self.list_of_features_to_rename
        
        final = suricata_df_renamed.reindex(columns=cols)
        return final
