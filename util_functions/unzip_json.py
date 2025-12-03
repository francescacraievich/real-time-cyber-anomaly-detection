import gzip
import shutil
import os

def gunzip_json_file(gz_path, output_path=None):
    """
    Decompress a .gz JSON file.
    
    Args:
        gz_path: Path to .gz file
        output_path: Output path (optional, defaults to removing .gz extension)
    """
    if output_path is None:
        # Remove .gz extension
        if gz_path.endswith('.gz'):
            output_path = gz_path[:-3]
        else:
            output_path = gz_path + '.unzipped'
    
    with gzip.open(gz_path, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    print(f"Decompressed {gz_path} to {output_path}")
    return output_path

if __name__ == "__main__":
    gz_path = 'data/normal_traffic/benign_traffic_fixed.json.gz'
    
    print("Current directory:", os.getcwd())
    print(f"Looking for file at: {os.path.abspath(gz_path)}")
    print(f"File exists: {os.path.exists(gz_path)}")
    
    if os.path.exists(gz_path):
        gunzip_json_file(
            gz_path=gz_path,
            output_path='data/normal_traffic/benign_traffic_fixed.json'
        )
        print("Decompression successful!")
    else:
        print(f"\nERROR: File not found at {gz_path}")
        if os.path.exists('data/normal_traffic/'):
            print("\nContents of data/normal_traffic/:", os.listdir('data/normal_traffic/'))
