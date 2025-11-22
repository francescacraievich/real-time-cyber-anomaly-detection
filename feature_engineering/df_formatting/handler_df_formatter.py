
import pandas as pd
from deprecated import deprecated
from format_normal_traffic import DataFrameFormatterNormalTraffic
from format_suricata_df import DataFrameFormatterSuricata

from aggregation_functions import (
    calculate_total_events_processed,
    calculate_total_anomalous_events,
    calculate_total_unique_malicious_ips,
    calculate_trend_percentage_change,
    calculate_total_events_for_dst_ports,
    calculate_total_malicious_events_per_protocol
)

from precalculations_functions import (
    calculate_rate_features,
    calculate_ratio_features,
    calculate_temporal_features,
    calculate_ip_classification_features,
    calculate_port_categorization,
    calculate_src_ip_geolocation_features,
    calculate_dst_ip_geolocation_features
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
        self.add_precalculations_all_dfs(calculate_ip_geoloc=False)
        self.add_aggregation_features_all_dfs()
        
        

    def unite_honeypot_and_normal_traffic_dfs(self):
        # concatenate rows from all sources and keep only base_features (as requested)
        combined_df = pd.concat([
            self.suricata_df[self.base_features],
            self.normal_traffic_df[self.base_features]
        ], ignore_index=True, sort=False)
        # enforce column order
        combined_df = combined_df.loc[:, self.base_features]
        return combined_df
    
    
    def add_precalculations_all_dfs(self, calculate_ip_geoloc=False):
        """Apply all precalculation features to each dataframe"""
        # Apply to suricata_df
        self.suricata_df = self._apply_precalculations(self.suricata_df, calculate_ip_geoloc)
        
        # Apply to normal_traffic_df
        self.normal_traffic_df = self._apply_precalculations(self.normal_traffic_df, calculate_ip_geoloc)
        
        
    def add_aggregation_features_all_dfs(self):
        """Apply all aggregation features to each dataframe"""
        # Apply to suricata_df
        self.suricata_df = self._apply_aggregation(self.suricata_df)
        
        # Apply to normal_traffic_df
        self.normal_traffic_df = self._apply_aggregation(self.normal_traffic_df)
        
        
        
    def _apply_precalculations(self, df, calculate_ip_geoloc):
        """Apply all precalculation functions to a dataframe"""
        # Rate features: bytes/packets per second
        df = calculate_rate_features(df)
        
        # Ratio features: sent/received ratios
        df = calculate_ratio_features(df)

        # Temporal features: hour, day, month, etc.
        df = calculate_temporal_features(df)
        
        # IP classification: private/public/multicast/loopback
        df = calculate_ip_classification_features(df)
        
        # Port categorization: well-known/registered/dynamic
        df = calculate_port_categorization(df)
        
        if calculate_ip_geoloc == True:
            # Add source IP geolocation features
            df = calculate_src_ip_geolocation_features(df)
            
            # Add destination IP geolocation features
            df = calculate_dst_ip_geolocation_features(df)
        
        return df
            

    def _apply_aggregation(self, df):
        """Apply all aggregation functions to a dataframe"""
        
        # Calculate total number of events/flows processed
        df = calculate_total_events_processed(df)

        # Calculate total count of anomalous/malicious events
        df = calculate_total_anomalous_events(df)

        # Calculate count of unique malicious source IPs
        df = calculate_total_unique_malicious_ips(df)

        # Calculate percentage change in event volume over time (trend analysis)
        df = calculate_trend_percentage_change(df)

        # Calculate event counts grouped by destination port
        df = calculate_total_events_for_dst_ports(df)

        # Calculate malicious event counts grouped by protocol type
        df = calculate_total_malicious_events_per_protocol(df)
        
        return df