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
import pandas as pd

data_path = project_root / "data"

df_initializer = DataFrameInitializer(
    suricata_json_path=data_path / 'suricata/log/suricata.json',
    normal_traffic_json_path=data_path / "normal_traffic/benign_traffic_fixed.json"
)

df_suricata, df_normal_traffic = df_initializer.initialize_dfs(sample_size=100000)

df_formatter = DataFrameFormatter(df_suricata, df_normal_traffic)
combined_df = df_formatter.unite_honeypot_and_normal_traffic_dfs()
combined_df_shuffled = combined_df.sample(frac=1).reset_index(drop=True)

pd.set_option('display.max_rows', None)        # Show all rows
pd.set_option('display.max_columns', None)     # Show all columns
pd.set_option('display.width', None)           # No line wrapping
pd.set_option('display.max_colwidth', None)    # Show full cell content

print("-------------------------------------------------------------------------------")
print("Suricata Columns:", df_formatter.suricata_df.columns)
print("Suricata Size:", df_formatter.suricata_df.shape)
print(df_formatter.suricata_df.info())
print(df_formatter.suricata_df.head(10))
print("-------------------------------------------------------------------------------")
print("Normal Traffic Columns:", df_formatter.normal_traffic_df.columns)
print("Normal Traffic Size:", df_formatter.normal_traffic_df.shape)
print(df_formatter.normal_traffic_df.info())
print(df_formatter.normal_traffic_df.head(10))
print("-------------------------------------------------------------------------------")
print("Combined DataFrame Size:", combined_df_shuffled.shape)
print("Combined DataFrame Columns:", combined_df_shuffled.columns)
print(combined_df_shuffled.info())
print(combined_df_shuffled.head(10))