import os
import sys
from pathlib import Path
#current_dir = os.path.dirname(__file__)
#feature_engineering_path = os.path.join(current_dir, '..', 'feature_engineering')
#abs_fe_path = os.path.abspath(feature_engineering_path)

project_root = Path(__file__).resolve().parents[1]
#feature_eng_path = project_root / "feature_engineering"
 
# Add feature_engineering to Python path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

#sys.path.insert(0, abs_fe_path)
#sys.path.append(os.path.abspath(feature_engineering_path))
from feature_engineering.df_initializing.handler_init_dfs import DataFrameInitializer
from feature_engineering.df_formatting.handler_df_formatter import DataFrameFormatter
from feature_engineering.test import TestFormatter
import pandas as pd

data_path = project_root / "data"

df_initializer = DataFrameInitializer(
    cowrie_json_path=data_path / 'cowrie/log/cowrie.json',
    dionea_json_path=data_path / 'dionaea/log/dionaea.json',
    suricata_json_path=data_path / 'suricata/log/suricata.json',
    normal_traffic_json_path=data_path / "normal_traffic/benign_traffic_fixed.json"
)

df_cowrie, df_dionea, df_suricata, df_normal_traffic = df_initializer.initialize_dfs(sample_size=100000)

df_formatter = DataFrameFormatter(df_cowrie, df_dionea, df_suricata, df_normal_traffic)

test_formatter = TestFormatter(df_suricata, df_normal_traffic)

pd.set_option('display.max_rows', None)        # Show all rows
pd.set_option('display.max_columns', None)     # Show all columns
pd.set_option('display.width', None)           # No line wrapping
pd.set_option('display.max_colwidth', None)    # Show full cell content

#print("-------------------------------------------------------------------------------")
#print("Suricata Columns:", df_formatter.suricata_df.columns)
#print("Suricata Columns:", df_suricata.columns)
#print("Suricata Size:", df_suricata.shape)
#print(df_suricata["flow"].head(10))
#df_suricata.to_csv("suricata_sample.csv", index=False)
print("-------------------------------------------------------------------------------")
print("Suricata Formatted Columns:", test_formatter.suricata_df.columns)
print(test_formatter.suricata_df.info())
print(test_formatter.suricata_df.head(10))
#print("-------------------------------------------------------------------------------")
print("Normal Traffic Formatted Columns:", test_formatter.normal_traffic_df.columns)
print(test_formatter.normal_traffic_df.info())
print(test_formatter.normal_traffic_df.head(10))