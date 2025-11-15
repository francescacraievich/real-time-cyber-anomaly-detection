


class FormatterNormalTraffic():
    
    def __init__(self, df_normal_traffic):
        self.df_normal_traffic = df_normal_traffic
        self.base_features = [
            'source_ip',
            'destination_ip',
            'source_port',
            'destination_port',
            'timestamp_start',
            'timestamp_end',
            'transport_protocol',
            'application_protocol',
            'label'
        ]
        self.format_normal_traffic_df()