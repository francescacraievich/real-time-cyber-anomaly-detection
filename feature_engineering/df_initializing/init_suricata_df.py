import json
import pandas as pd

class SuricataDataFrameInitializer():
    """
    Initializes a DataFrame from Suricata JSON log file.
    Attributes:
        suricata_json (str): Path to Suricata JSON log file.
    """
    
    def __init__(self, suricata_json):
        self.suricata_json = suricata_json
        
    def initialize_suricata(self):
        records_Suricata = []
        with open(self.suricata_json, 'r') as f:
            for line in f:
                records_Suricata.append(json.loads(line))
        df_suricata = pd.DataFrame(records_Suricata)
        return df_suricata
    