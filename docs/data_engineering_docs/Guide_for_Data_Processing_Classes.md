# Usage Guide for Data Processing Classes

This guide explains how to use the data processing classes in the `useful_scripts` and `feature_engineering` folders for cyber anomaly detection.

## Table of Contents
- [Overview](#overview)
- [DataFrameInitializer](#dataframeinitializer)
- [DataFrameFormatter Classes](#dataframeformatter-classes)
- [Complete Workflow Example](#complete-workflow-example)

## Overview

The data processing pipeline consists of two main stages:

0. **unzipping** - Necessary to unzip the JSON file to work with the classes
   - NOTE: the zipped files are in the `data/normal_traffic` folder and are: the raw JSON benign_traffic.son.gz that containt the raw data and the JSON benign_traffic.json.gz that containt the fixed data, ready for the initializer class. In the initialize_dfs() method we can toggle the preprocessing of the raw JSON that will be turned in the JSON ready for the initializer. If this is not necessary use the path to the JSON that is already preprocessed in the DataFrameInitializer class.
1. **Initialization** - Loading raw JSON data from various honeypot sources
2. **Formatting** - Standardizing column names and data types across all sources

## DataFrameInitializer

Located in: `feature_engineering/df_initializing/handler_init_dfs.py`

### Purpose
Loads and samples data from multiple honeypot sources (Cowrie, Dionaea, Suricata) and normal traffic logs.

### Usage

```python
from df_initializing.handler_init_dfs import DataFrameInitializer

# Initialize with paths to your JSON log files
df_initializer = DataFrameInitializer(
    cowrie_json_path='path/to/cowrie.json',
    dionea_json_path='path/to/dionaea.json',
    suricata_json_path='path/to/suricata.json',
    normal_traffic_json_path='path/to/benign_traffic.json'
)

# Load and sample data (optional: specify sample_size)
df_cowrie, df_dionea, df_suricata, df_normal_traffic = df_initializer.initialize_dfs(sample_size=1000)
```

### Parameters
- `cowrie_json_path`: Path to Cowrie honeypot logs
- `dionea_json_path`: Path to Dionaea honeypot logs
- `suricata_json_path`: Path to Suricata IDS logs
- `normal_traffic_json_path`: Path to benign traffic logs
- `sample_size`: (Optional) Number of records to sample from each source

## DataFrameFormatter Classes

Located in: `feature_engineering/df_formatting/`

### Handler Class: DataFrameFormatter

The main handler that coordinates formatting for all data sources.

```python
from handler_df_formatter import DataFrameFormatter

# Create formatter instance with raw dataframes
df_formatter = DataFrameFormatter(df_cowrie, df_dionea, df_suricata, df_normal_traffic)

# Access individual formatted dataframes
formatted_cowrie = df_formatter.cowrie_df
formatted_dionea = df_formatter.dionea_df
formatted_suricata = df_formatter.suricata_df
formatted_normal = df_formatter.normal_traffic_df

# Combine all dataframes into one
combined_df = df_formatter.unite_all_dfs()
```

### Individual Formatter Classes

#### 1. DataFrameFormatterCowrie
Formats SSH honeypot (Cowrie) data.

```python
from format_cowrie_df import DataFrameFormatterCowrie

formatter = DataFrameFormatterCowrie(df_cowrie, list_of_features_to_rename)
formatted_df = formatter.format_cowrie_df()
```

**Key transformations:**
- Renames columns to standardized names
- Converts application_protocol to lowercase
- Extracts timestamp from eventid
- Adds 'malicious' label

#### 2. DataFrameFormatterDionea
Formats malware capture (Dionaea) data.

```python
from format_dionea_df import DataFrameFormatterDionea

formatter = DataFrameFormatterDionea(df_dionea, list_of_features_to_rename)
formatted_df = formatter.format_dionea_df()
```

**Key transformations:**
- Renames columns to standardized names
- Converts application_protocol to lowercase
- Parses connection_protocol into transport and application protocols
- Adds 'malicious' label

#### 3. DataFrameFormatterSuricata
Formats IDS (Suricata) data.

```python
from format_suricata_df import DataFrameFormatterSuricata

formatter = DataFrameFormatterSuricata(df_suricata, list_of_features_to_rename)
formatted_df = formatter.format_suricata_df()
```

**Key transformations:**
- Renames columns to standardized names
- Converts application_protocol to lowercase
- Handles duration calculation
- Adds 'malicious' label

#### 4. DataFrameFormatterNormalTraffic
Formats benign network traffic data.

```python
from format_normal_traffic import DataFrameFormatterNormalTraffic

formatter = DataFrameFormatterNormalTraffic(df_normal_traffic, list_of_features_to_rename)
formatted_df = formatter.format_normal_traffic_df()
```

**Key transformations:**
- Renames columns to standardized names
- Converts application_protocol to lowercase
- Calculates duration from start/stop times
- Adds 'benign' label

## Complete Workflow Example

```python
import pandas as pd
import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.getcwd())
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from df_initializing.handler_init_dfs import DataFrameInitializer
from handler_df_formatter import DataFrameFormatter

# Step 1: Initialize data
df_initializer = DataFrameInitializer(
    cowrie_json_path='data/cowrie/log/cowrie.json',
    dionea_json_path='data/dionaea/log/dionaea.json',
    suricata_json_path='data/suricata/log/suricata.json',
    normal_traffic_json_path='data/normal_traffic/benign_traffic_fixed.json'
)

# Load data with sampling
df_cowrie, df_dionea, df_suricata, df_normal_traffic = df_initializer.initialize_dfs(sample_size=1000)

# Step 2: Format data
df_formatter = DataFrameFormatter(df_cowrie, df_dionea, df_suricata, df_normal_traffic)

# Step 3: Inspect individual formatted dataframes
print("Cowrie shape:", df_formatter.cowrie_df.shape)
print("Dionea shape:", df_formatter.dionea_df.shape)
print("Suricata shape:", df_formatter.suricata_df.shape)
print("Normal Traffic shape:", df_formatter.normal_traffic_df.shape)

# Step 4: Combine all data sources
combined_df = df_formatter.unite_all_dfs()

print("Combined DataFrame shape:", combined_df.shape)
print("Label distribution:\n", combined_df['label'].value_counts())

# Step 5: Save processed data
combined_df.to_csv('processed_data.csv', index=False)
```

## Standardized Output Features

All formatters produce dataframes with the following columns:

| Column Name | Description | Data Type |
|-------------|-------------|-----------|
| `source_ip` | Source IP address | string |
| `destination_ip` | Destination IP address | string |
| `source_port` | Source port number | int |
| `destination_port` | Destination port number | int |
| `timestamp_start` | Start timestamp | datetime |
| `transport_protocol` | Transport layer protocol (tcp/udp) | string |
| `application_protocol` | Application layer protocol (lowercase) | string |
| `duration` | Connection duration in seconds | float |
| `label` | Traffic label ('malicious' or 'benign') | string |

## Notes

- All `application_protocol` values are automatically converted to lowercase for consistency
- Missing or invalid data is handled gracefully with appropriate default values
- The combined dataframe maintains consistent schema across all sources
- Sample sizes can be adjusted based on available memory and processing requirements

## Error Handling

If you encounter path-related errors, ensure:
1. JSON files exist at specified paths
2. File permissions allow reading
3. JSON files are properly formatted
4. Required parent directories are in Python path
