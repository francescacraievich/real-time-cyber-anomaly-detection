import json
import random
import pandas as pd
import ijson
import re
import gzip


class NormalTrafficDataFrameInitializer():
    """
    Initializes a DataFrame from benign_traffic JSON log file.
    Attributes:
        benign_traffic_json_path (str): Path to benign_traffic JSON log file.
    """
    
    def __init__(self, benign_traffic_json_path):
        self.benign_traffic_json_path = benign_traffic_json_path

    def initialize_benign_traffic(self, sample_size):
        sampled_records = self.sample_large_json_with_ijson(sample_size)
        df_benign_traffic = pd.DataFrame(sampled_records)
        return df_benign_traffic

    def sample_large_json_with_ijson(self, sample_size):
        N = sample_size
        result = []

        with open(self.benign_traffic_json_path, "rb") as f:
            parser = ijson.items(f, "item")
            for i, item in enumerate(parser):
                if i == N:
                    break
                result.append(item)
        finally:
            f.close()

        return(result)
    
    def preprocess_json_replace_invalid_numbers(self, output_path):
        with open(self.benign_traffic_json_path, "rb", encoding="utf-8") as f_in, \
            open(output_path, "w", encoding="utf-8") as f_out:
            for line in f_in:
                # replace NaN, Infinity, -Infinity with null
                line_fixed = re.sub(r'\bNaN\b|\bInfinity\b|\b-Infinity\b', 'null', line)
                f_out.write(line_fixed)
        self.benign_traffic_json_path = output_path


if __name__ == "__main__":
    df_initializer = NormalTrafficDataFrameInitializer(
        benign_traffic_json_path="data/normal_traffic/benign_traffic_fixed.json"
    )
    df_benign_traffic = df_initializer.initialize_benign_traffic(sample_size=1000)
    print("Benign Traffic DataFrame:" , df_benign_traffic.head())
    print("DataFrame shape:", df_benign_traffic.shape)
    print("Columns:", df_benign_traffic.columns.tolist())