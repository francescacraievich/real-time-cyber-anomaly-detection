import json
import pandas as pd

# Read logs and initialize as DataFrames
class DataFrameInitializer():
    """
    Initializes DataFrames from JSON log files for Cowrie, Dionaea, Suricata, and Tanner.
    Attributes:
        cowrie_json (str): Path to Cowrie JSON log file.
        dionea_json (str): Path to Dionaea JSON log file.
        suricata_json (str): Path to Suricata JSON log file.
        tanner_json (str): Path to Tanner JSON log file.

    Methods:
        initialize_dfs(): Initializes and returns DataFrames for all log types.
        initialize_cowrie(): Initializes and returns DataFrame for Cowrie logs.
        initialize_dionea(): Initializes and returns DataFrame for Dionaea logs.
        initialize_suricata(): Initializes and returns DataFrame for Suricata logs.
        initialize_tanner(): Initializes and returns DataFrame for Tanner logs.
    """


    def __init__(self, cowrie_json, dionea_json, suricata_json, tanner_json):
        self.cowrie_json = cowrie_json
        self.dionea_json = dionea_json
        self.suricata_json = suricata_json 
        self.tanner_json = tanner_json

    def initialize_dfs(self):
        df_cowrie = self.initialize_cowrie()
        df_dionea = self.initialize_dionea()
        df_suricata = self.initialize_suricata()
        df_tanner = self.initialize_tanner()
        return df_cowrie, df_dionea, df_suricata, df_tanner

    def initialize_cowrie(self):
        records_Cowrie = []
        with open(self.cowrie_json, 'r') as f:
            for line in f:
                records_Cowrie.append(json.loads(line))
        df_cowrie = pd.DataFrame(records_Cowrie)
        return df_cowrie
    
    def initialize_dionea(self):
        records_Dionea = []
        with open(self.dionea_json, 'r') as f:
            for line in f:
                records_Dionea.append(json.loads(line))
        df_dionea = pd.DataFrame(records_Dionea)
        return df_dionea
    
    def initialize_suricata(self):
        records_Suricata = []
        with open(self.suricata_json, 'r') as f:
            for line in f:
                records_Suricata.append(json.loads(line))
        df_suricata = pd.DataFrame(records_Suricata)
        return df_suricata
    
    def initialize_tanner(self):
        records_Tanner = []
        with open(self.tanner_json, 'r') as f:
            for line in f:
                records_Tanner.append(json.loads(line))
        df_tanner = pd.DataFrame(records_Tanner)
        return df_tanner

if __name__ == "__main__":
    df_initializer = DataFrameInitializer(
        cowrie_json='data/cowrie/log/cowrie.json',
        dionea_json='data/dionaea/log/dionaea.json',
        suricata_json='data/suricata/log/suricata.json',
        tanner_json='data/tanner/log/tanner.json'
    )
    df_cowrie, df_dionea, df_suricata, df_tanner = df_initializer.initialize_dfs()
    print("Cowrie DataFrame:" , df_cowrie.head())
    print("Dionea DataFrame:" , df_dionea.head())
    print("Suricata DataFrame:" , df_suricata.head())
    print("Tanner DataFrame:" , df_tanner.head())