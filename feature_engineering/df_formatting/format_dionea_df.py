
import pandas as pd

class DataFrameFormatterDionea():
    
    def __init__(self, dionea_df, list_of_features_to_rename: list):
        self.dionea_df = dionea_df
        self.list_of_features_to_rename = list_of_features_to_rename
        
    def format_dionea_df(self):
            
        expanded = pd.json_normalize(self.dionea_df['connection'])
        self.dionea_df = pd.concat([self.dionea_df.drop(columns=['connection']), expanded], axis=1)
        
        self.dionea_df[self.list_of_features_to_rename[7]] = 'malicious'
        
        dionea_df_renamed = self.dionea_df.rename(columns={
            'src_ip': self.list_of_features_to_rename[0],
            'dst_ip': self.list_of_features_to_rename[1],
            'src_port': self.list_of_features_to_rename[2],
            'dst_port': self.list_of_features_to_rename[3],
            'timestamp': self.list_of_features_to_rename[4],
            'transport': self.list_of_features_to_rename[5],
            'protocol': self.list_of_features_to_rename[6]
        })  
        
        dionea_df_renamed[self.list_of_features_to_rename[2]] = pd.to_numeric(dionea_df_renamed[self.list_of_features_to_rename[2]], errors='coerce').astype('Int64')
        dionea_df_renamed[self.list_of_features_to_rename[3]] = pd.to_numeric(dionea_df_renamed[self.list_of_features_to_rename[3]], errors='coerce').astype('Int64')
        
        dionea_df_renamed[self.list_of_features_to_rename[4]] = pd.to_datetime(
        dionea_df_renamed[self.list_of_features_to_rename[4]]
        ).dt.tz_localize(None) 
        
        dionea_df_renamed[self.list_of_features_to_rename[8]] = 0
        
        dionea_df_renamed[self.list_of_features_to_rename[8]] = dionea_df_renamed[self.list_of_features_to_rename[8]].astype(float)
    
        
        dionea_df_renamed["origin_name"] = "dionea"
        
        cols = self.list_of_features_to_rename
        
        final = dionea_df_renamed.reindex(columns=cols)
        return final
    
