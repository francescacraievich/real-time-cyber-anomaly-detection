import json
import pandas as pd
import gzip

# Read logs and initialize as DataFrames
class DataFrameInitializer():
    """
    Initializes DataFrames from JSON log files for Cowrie, Dionaea, Suricata, and Tanner.
    Attributes:
        cowrie_json (str): Path to Cowrie JSON log file.
        dionea_json (str): Path to Dionaea JSON log file.
        suricata_json (str): Path to Suricata JSON log file.

    Methods:
        initialize_dfs(): Initializes and returns DataFrames for all log types.
        initialize_cowrie(): Initializes and returns DataFrame for Cowrie logs.
        initialize_dionea(): Initializes and returns DataFrame for Dionaea logs.
    """


    def __init__(self, cowrie_json, dionea_json, suricata_json):
        self.cowrie_json = cowrie_json
        self.dionea_json = dionea_json
        self.suricata_json = suricata_json
        # self.normal_traffic_json = normal_traffic_json

    def initialize_dfs(self):
        df_cowrie = self.initialize_cowrie()
        df_dionea = self.initialize_dionea()
        df_suricata = self.initialize_suricata()
        # df_normal_traffic = self.initialize_normal_traffic()
        return df_cowrie, df_dionea, df_suricata

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
        cowrie_json='data/cowrie/log/cowrie.json',
        dionea_json='data/dionaea/log/dionaea.json',
        suricata_json='data/suricata/log/suricata.json',
        # normal_traffic_json="data/normal_traffic/benign_traffic.json.gz"
    )
    df_cowrie, df_dionea, df_suricata = df_initializer.initialize_dfs()
    print("Cowrie DataFrame:" , df_cowrie.head())
    print("Dionea DataFrame:" , df_dionea.head())
    print("Suricata DataFrame:" , df_suricata.head())
    # print("Normal Traffic DataFrame:" , df_normal_traffic.head())