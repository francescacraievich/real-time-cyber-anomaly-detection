import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.feature_engineering.df_initializing.init_normal_traffic_df import \
    NormalTrafficDataFrameInitializer as NormalTrafficInit
from src.feature_engineering.df_initializing.init_suricata_df import \
    SuricataDataFrameInitializer as SuricataInit


# Read logs and initialize as DataFrames
class DataFrameInitializer:
    """
    Initializes DataFrames from JSON log files for Cowrie, Dionaea, Suricata, and Tanner.
    Attributes:
        suricata_json_path (str): Path to Suricata JSON log file.
        normal_traffic_json_path (str): Path to Normal Traffic JSON log file.

    Methods:
        initialize_dfs():  returns DataFrames for all log types.
    """

    def __init__(self, suricata_json_path, normal_traffic_json_path):
        self.suricata_init = SuricataInit(suricata_json_path)
        self.normal_traffic_init = NormalTrafficInit(normal_traffic_json_path)

    def initialize_dfs(self, preprocess_normal_traffic=False, sample_size=1000):
        df_suricata = self.suricata_init.initialize_suricata()

        if preprocess_normal_traffic:
            self.normal_traffic_init.preprocess_json_replace_invalid_numbers(
                output_path="data/normal_traffic/benign_traffic_fixed.json"
            )

        df_normal_traffic = self.normal_traffic_init.initialize_benign_traffic(
            sample_size=sample_size
        )
        return df_suricata, df_normal_traffic


if __name__ == "__main__":
    df_initializer = DataFrameInitializer(
        suricata_json_path="data/suricata/log/suricata.json",
        normal_traffic_json_path="data/normal_traffic/benign_traffic_fixed.json",
    )
    df_suricata, df_normal_traffic = df_initializer.initialize_dfs(sample_size=10000)
    print("Suricata DataFrame:", df_suricata.head())
    print("Normal Traffic DataFrame:", df_normal_traffic.head())
