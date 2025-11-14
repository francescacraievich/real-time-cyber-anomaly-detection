import json
import pandas as pd
import gzip
from init_dionea_df import DioneaDataFrameInitializer as DioneaInit
from init_suricata_df import SuricataDataFrameInitializer as SuricataInit
from init_cowrie_df import CowrieDataFrameInitializer as CowrieInit
from init_normal_traffic_df import NormalTrafficDataFrameInitializer as NormalTrafficInit

# Read logs and initialize as DataFrames
class DataFrameInitializer():
    """
    Initializes DataFrames from JSON log files for Cowrie, Dionaea, Suricata, and Tanner.
    Attributes:
        cowrie_json_path (str): Path to Cowrie JSON log file.
        dionea_json_path (str): Path to Dionaea JSON log file.
        suricata_json_path (str): Path to Suricata JSON log file.

    Methods:
        initialize_dfs():  returns DataFrames for all log types.
    """


    def __init__(self, cowrie_json_path, dionea_json_path, suricata_json_path, normal_traffic_json_path):
        self.cowrie_init = CowrieInit(cowrie_json_path)
        self.dionea_init = DioneaInit(dionea_json_path)
        self.suricata_init = SuricataInit(suricata_json_path)
        self.normal_traffic_init = NormalTrafficInit(normal_traffic_json_path)

    def initialize_dfs(self, preprocess_normal_traffic=False):
        df_cowrie = self.cowrie_init.initialize_cowrie()
        df_dionea = self.dionea_init.initialize_dionea()
        df_suricata = self.suricata_init.initialize_suricata()
        
        if preprocess_normal_traffic:
            self.normal_traffic_init.preprocess_json_replace_invalid_numbers(output_path="data/normal_traffic/benign_traffic_fixed.json")
        
        df_normal_traffic = self.normal_traffic_init.initialize_benign_traffic()
        return df_cowrie, df_dionea, df_suricata, df_normal_traffic


"""
    def initialize_normal_traffic(self, chunksize=10000):

        chunks = []
        skipped_lines = 0
        
        with gzip.open(self.normal_traffic_json, 'rt', encoding='utf-8') as f:
            chunk = []
            for i, line in enumerate(f):
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    skipped_lines += 1
                    continue
                
                try:
                    chunk.append(json.loads(line))
                except json.JSONDecodeError as e:
                    skipped_lines += 1
                    print(f"Warning: Skipped malformed JSON at line {i + 1}: {e}")
                    continue
                
                if len(chunk) >= chunksize:
                    chunks.append(pd.DataFrame(chunk))
                    chunk = []
                    print(f"Processed {i + 1 - skipped_lines} valid lines (skipped {skipped_lines} bad lines)...")
            
            # Don't forget the last chunk
            if chunk:
                chunks.append(pd.DataFrame(chunk))
        
        if not chunks:
            print("Warning: No valid data found!")
            return pd.DataFrame()
        
        df = pd.concat(chunks, ignore_index=True)
        print(f"Total records loaded: {len(df)} (skipped {skipped_lines} invalid lines)")
        return df
"""
        

if __name__ == "__main__":
    df_initializer = DataFrameInitializer(
        cowrie_json_path='data/cowrie/log/cowrie.json',
        dionea_json_path='data/dionaea/log/dionaea.json',
        suricata_json_path='data/suricata/log/suricata.json',
        normal_traffic_json_path="data/normal_traffic/benign_traffic_fixed.json"
    )
    df_cowrie, df_dionea, df_suricata, df_normal_traffic = df_initializer.initialize_dfs()
    print("Cowrie DataFrame:" , df_cowrie.head())
    print("Dionea DataFrame:" , df_dionea.head())
    print("Suricata DataFrame:" , df_suricata.head())
    print("Normal Traffic DataFrame:" , df_normal_traffic.head())