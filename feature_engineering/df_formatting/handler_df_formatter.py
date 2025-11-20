
from df_initializing.handler_init_dfs import DataFrameInitializer
import pandas as pd
from deprecated import deprecated
from format_normal_traffic import DataFrameFormatterNormalTraffic
from format_suricata_df import DataFrameFormatterSuricata

from precalculations_functions import (
    calculate_rate_features,
    calculate_ratio_features,
    calculate_temporal_features,
    calculate_ip_classification_features,
    calculate_port_categorization
)

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
        self.add_precalculations_all_dfs()
        

    def unite_honeypot_and_normal_traffic_dfs(self):
        # concatenate rows from all sources and keep only base_features (as requested)
        combined_df = pd.concat([
            self.suricata_df[self.base_features],
            self.normal_traffic_df[self.base_features]
        ], ignore_index=True, sort=False)
        # enforce column order
        combined_df = combined_df.loc[:, self.base_features]
        return combined_df
    
    
    def add_precalculations_all_dfs(self):
        """Apply all precalculation features to each dataframe"""
        # Apply to suricata_df
        self.suricata_df = self._apply_precalculations(self.suricata_df)
        
        # Apply to normal_traffic_df
        self.normal_traffic_df = self._apply_precalculations(self.normal_traffic_df)
        
        
    def _apply_precalculations(self, df):
        """Apply all precalculation functions to a dataframe"""
        # Rate feature
        df = calculate_rate_features(df, 'bytes_sent', 'bytes_received', 
                                     'pkts_sent', 'pkts_received', 'duration')
        
        # Ratio features
        df = calculate_ratio_features(df, 'bytes_sent', 'bytes_received',
                                      'pkts_sent', 'pkts_received')

        # Temporal features
        df = calculate_temporal_features(df, 'timestamp_start')
        
        # IP classification
        df = calculate_ip_classification_features(df, 'source_ip', 'destination_ip')
        
        # Port categorization
        df = calculate_port_categorization(df, 'destination_port')
        
        return df
        


