import os
import sys
from pathlib import Path
#current_dir = os.path.dirname(__file__)
#feature_engineering_path = os.path.join(current_dir, '..', 'feature_engineering')
#abs_fe_path = os.path.abspath(feature_engineering_path)

project_root = Path(__file__).parent.parent
feature_eng_path = project_root / "feature_engineering"
 
# Add feature_engineering to Python path
if str(feature_eng_path) not in sys.path:
    sys.path.insert(0, str(feature_eng_path))

#sys.path.insert(0, abs_fe_path)
#sys.path.append(os.path.abspath(feature_engineering_path))
from feature_engineering.df_initializing.handler_init_dfs import DataFrameInitializer
from feature_engineering.df_formatting.handler_df_formatter import DataFrameFormatter
import pandas as pd

df_initializer = DataFrameInitializer(
    cowrie_json_path='../data/cowrie/log/cowrie.json',
    dionea_json_path='../data/dionaea/log/dionaea.json',
    suricata_json_path='../data/suricata/log/suricata.json',
    normal_traffic_json_path="../data/normal_traffic/benign_traffic_fixed.json"
)

df_cowrie, df_dionea, df_suricata, df_normal_traffic = df_initializer.initialize_dfs(sample_size=10000)

df_formatter = DataFrameFormatter(df_cowrie, df_dionea, df_suricata, df_normal_traffic)

print("Suricata Columns:", df_formatter.suricata_df.info())

print("Dionea Columns:", df_formatter.dionea_df.info())

print("Cowrie Columns:", df_formatter.cowrie_df.info())

print("Normal Traffic Columns:", df_formatter.normal_traffic_df.info())

combined_honeypot_df = df_formatter.unite_all_honeypot_dfs()
print("Combined Honeypot DataFrame columns:", combined_honeypot_df.columns)

combined_all_df = df_formatter.unite_honeypot_and_normal_traffic_dfs()
print("Combined All DataFrame columns:", combined_all_df.columns)