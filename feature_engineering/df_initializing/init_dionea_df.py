import json
import pandas as pd

class DioneaDataFrameInitializer():
    """
    Initializes a DataFrame from Dionea JSON log file.
    Attributes:
        dionea_json_path (str): Path to Dionea JSON log file.
    """
    
    def __init__(self, dionea_json_path):
        self.dionea_json_path = dionea_json_path
        
    def initialize_dionea(self):
        records_Dionea = []
        with open(self.dionea_json_path, 'r') as f:
            for line in f:
                records_Dionea.append(json.loads(line))
        df_dionea = pd.DataFrame(records_Dionea)
        return df_dionea
    