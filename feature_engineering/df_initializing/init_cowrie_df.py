import json
import pandas as pd

class CowrieDataFrameInitializer():
    """
    Initializes a DataFrame from Cowrie JSON log file.
    Attributes:
        cowrie_json_path (str): Path to Cowrie JSON log file.
    """
    
    def __init__(self, cowrie_json_path):
        self.cowrie_json_path = cowrie_json_path

    def initialize_cowrie(self):
        records_Cowrie = []
        with open(self.cowrie_json_path, 'r') as f:
            for line in f:
                records_Cowrie.append(json.loads(line))
        df_cowrie = pd.DataFrame(records_Cowrie)
        return df_cowrie
    

