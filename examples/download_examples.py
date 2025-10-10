# examples/download_examples.py
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def download_examples():
    """Download example audio files for VoxScribe"""
    print("Downloading example audio files...")
    url = "https://github.com/chaoliu/voxscribe/releases/download/v1.0.0/examples.zip"
    response = requests.get(url)
    
    with ZipFile(BytesIO(response.content)) as zip_file:
        zip_file.extractall("examples")
    
    print(f"Examples downloaded to {os.path.abspath('examples')} directory")

if __name__ == "__main__":
    download_examples()