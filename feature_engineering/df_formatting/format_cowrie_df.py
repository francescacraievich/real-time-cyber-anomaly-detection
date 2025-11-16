
import pandas as pd

class DataFrameFormatterCowrie():
    
    def __init__(self, cowrie_df, list_of_features_to_rename: list):
        self.cowrie_df = cowrie_df
        self.list_of_features_to_rename = list_of_features_to_rename
        
    def format_cowrie_df(self):
        self.cowrie_df[self.list_of_features_to_rename[5]] = 'tcp'
        self.cowrie_df[self.list_of_features_to_rename[7]] = 'malicious'
        cowrie_df_renamed = self.cowrie_df.rename(columns={
            'src_ip': self.list_of_features_to_rename[0],
            'dst_ip': self.list_of_features_to_rename[1],
            'src_port': self.list_of_features_to_rename[2],
            'dst_port': self.list_of_features_to_rename[3],
            'timestamp': self.list_of_features_to_rename[4],
            'protocol': self.list_of_features_to_rename[6]
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
            'source_ip': coalesce(self.list_of_features_to_rename[0]),
            'destination_ip': coalesce(self.list_of_features_to_rename[1]),
            'source_port': coalesce(self.list_of_features_to_rename[2]),
            'destination_port': coalesce(self.list_of_features_to_rename[3]),
            'transport_protocol': coalesce(self.list_of_features_to_rename[5]),
            'application_protocol': coalesce(self.list_of_features_to_rename[6]),
            'label': coalesce(self.list_of_features_to_rename[7]),
            'timestamp_start': coalesce(self.list_of_features_to_rename[4]),
            'duration': merged.get('duration_closed').fillna(merged.get('duration_connect'))
        })
        
        final[self.list_of_features_to_rename[4]] = pd.to_datetime(
        final[self.list_of_features_to_rename[4]]
        ).dt.strftime('%m/%d/%Y %H:%M')      
    

        # ensure columns order matches base_features where applicable
        # keep session and timestamp_start/end too
        cols = [
            'source_ip', 'destination_ip', 'source_port', 'destination_port',
            'timestamp_start',
            'transport_protocol', 'application_protocol', 'duration', 'label'
        ]
        final = final.reindex(columns=cols)

        return final
    
