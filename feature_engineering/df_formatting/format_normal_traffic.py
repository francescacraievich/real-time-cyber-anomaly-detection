
import pandas as pd

class DataFrameFormatterNormalTraffic():
    
    def __init__(self, df_normal_traffic, list_of_features_to_rename: list):
        self.df_normal_traffic = df_normal_traffic
        self.list_of_features_to_rename = list_of_features_to_rename
        
    def format_normal_traffic_df(self):
        
        normal_traffic_df_renamed = self.df_normal_traffic.rename(columns={
            'source': self.list_of_features_to_rename[0],
            'destination': self.list_of_features_to_rename[1],
            'sourcePort': self.list_of_features_to_rename[2],
            'destinationPort': self.list_of_features_to_rename[3],
            'startDateTime': self.list_of_features_to_rename[4],
            'protocolName': self.list_of_features_to_rename[5],
            'appName': self.list_of_features_to_rename[6],
            'label': self.list_of_features_to_rename[7]
        })
        
        # Convert application_protocol to lowercase
        normal_traffic_df_renamed[self.list_of_features_to_rename[6]] = normal_traffic_df_renamed[self.list_of_features_to_rename[6]].str.lower()
        
        # Convert to datetime
        normal_traffic_df_renamed[self.list_of_features_to_rename[4]] = pd.to_datetime(normal_traffic_df_renamed[self.list_of_features_to_rename[4]])
        normal_traffic_df_renamed["stopDateTime"] = pd.to_datetime(normal_traffic_df_renamed["stopDateTime"])
        
        # Calculate duration
        normal_traffic_df_renamed['duration'] = (
            normal_traffic_df_renamed["stopDateTime"] - 
            normal_traffic_df_renamed[self.list_of_features_to_rename[4]]
        ).dt.total_seconds()
        
        normal_traffic_df_renamed[self.list_of_features_to_rename[7]] = 'benign'
        
        cols = [
            'source_ip', 'destination_ip', 'source_port', 'destination_port',
            'timestamp_start',
            'transport_protocol', 'application_protocol', 'duration', 'label'
        ]
        
        final = normal_traffic_df_renamed.reindex(columns=cols)
        return final
        
    