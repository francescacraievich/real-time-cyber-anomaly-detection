import gzip
import shutil

def gzip_json_file(json_path, output_path=None):
    """Compress JSON file to .gz format"""
    if output_path is None:
        output_path = json_path + '.gz'
    
    with open(json_path, 'rb') as f_in:
        with gzip.open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    print(f"Compressed {json_path} to {output_path}")
    return output_path

if __name__ == "__main__":
    gzip_json_file(json_path='data/normal_traffic/benign_traffic_fixed.json')