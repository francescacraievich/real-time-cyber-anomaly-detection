import json

import pandas as pd


class SuricataDataFrameInitializer:
    """
    Initializes a DataFrame from Suricata JSON log file.
    Attributes:
        suricata_json_path (str): Path to Suricata JSON log file.
    """

    def __init__(self, suricata_json_path):
        self.suricata_json_path = suricata_json_path

    def initialize_suricata(self):
        records_Suricata = []
        with open(self.suricata_json_path, "r") as f:
            for line in f:
                records_Suricata.append(json.loads(line))
        df_suricata = pd.DataFrame(records_Suricata)
        return df_suricata
