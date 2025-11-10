import os
import pandas as pd
import json
import tarfile
import tempfile
import shutil

# Base path
base_dir = os.path.dirname(os.path.abspath(__file__))
tar_path = os.path.join(base_dir, "iscxids2012-master.tar.gz")
output_file = os.path.join(base_dir, "benign_traffic.json")

print("="*80)
print("Extracting Benign Traffic Only from ISCXIDS2012")
print("="*80)

# Usa una directory temporanea per evitare problemi con Windows Defender
temp_dir = tempfile.mkdtemp()
extract_dir = os.path.join(temp_dir, "iscx_temp")
os.makedirs(extract_dir, exist_ok=True)

print(f"\n[1/3] Extracting tar.gz to temporary location...")
print(f"Temp directory: {extract_dir}")

# Estrai il tar.gz
with tarfile.open(tar_path, "r:gz") as tar:
    tar.extractall(path=extract_dir)

print("[OK] Extraction complete")

# Trova tutti i CSV
print(f"\n[2/3] Searching for CSV files...")
csv_files = []
for root, _, files in os.walk(extract_dir):
    for f in files:
        if f.endswith(".csv"):
            csv_files.append(os.path.join(root, f))

print(f"[OK] Found {len(csv_files)} CSV files")

# Estrai solo il traffico benign
print(f"\n[3/3] Filtering benign traffic and converting to JSON...")

all_benign_data = []
total_rows = 0
benign_rows = 0

for idx, csv_path in enumerate(csv_files):
    print(f"\n  [{idx+1}/{len(csv_files)}] Processing {os.path.basename(csv_path)}...")

    try:
        # Leggi il CSV
        df = pd.read_csv(csv_path)
        total_rows += len(df)

        # Filtra solo le righe con Label == 'Normal' o 'normal' (case insensitive)
        benign_df = df[df['Label'].str.lower() == 'normal']
        benign_count = len(benign_df)
        benign_rows += benign_count

        print(f"    Total rows: {len(df):,}")
        print(f"    Benign rows: {benign_count:,}")

        # Converti in dizionario e aggiungi alla lista
        benign_records = benign_df.to_dict(orient='records')
        all_benign_data.extend(benign_records)

    except Exception as e:
        print(f"    [ERROR] {e}")

# Pulisci la directory temporanea
print(f"\nCleaning up temporary files...")
shutil.rmtree(temp_dir, ignore_errors=True)
print(f"[OK] Temporary files removed")

# Salva tutto in un unico file JSON
print(f"\n{'='*80}")
print(f"Saving benign traffic to JSON...")
print(f"{'='*80}")

with open(output_file, 'w') as f:
    json.dump(all_benign_data, f, indent=2)

print(f"\n[OK] Saved {benign_rows:,} benign records out of {total_rows:,} total records")
print(f"[OK] Output file: {output_file}")
print(f"[OK] File size: {os.path.getsize(output_file) / (1024*1024):.2f} MB")
print(f"\n{'='*80}")
print("Done!")
print(f"{'='*80}")
