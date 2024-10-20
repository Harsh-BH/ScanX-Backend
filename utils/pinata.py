# utils/pinata_utils.py

import os
import requests

def upload_to_pinata(file_path):
    """
    Uploads a file to Pinata (IPFS) and returns the IPFS hash.
    
    :param file_path: Path to the file to be uploaded.
    :return: IPFS hash of the uploaded file or None if upload fails.
    """
    PINATA_API_KEY = os.getenv('PINATA_API_KEY')
    PINATA_SECRET_API_KEY = os.getenv('PINATA_SECRET_API_KEY')
    PINATA_API_URL = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    
    if not PINATA_API_KEY or not PINATA_SECRET_API_KEY:
        raise EnvironmentError("Pinata API credentials not found in environment variables.")
    
    headers = {
        'pinata_api_key': PINATA_API_KEY,
        'pinata_secret_api_key': PINATA_SECRET_API_KEY
    }
    
    try:
        with open(file_path, 'rb') as file:
            files = {
                'file': (os.path.basename(file_path), file)
            }
            response = requests.post(PINATA_API_URL, files=files, headers=headers)
            response.raise_for_status()
            ipfs_hash = response.json().get('IpfsHash')
            return ipfs_hash
    except requests.exceptions.RequestException as e:
        print(f"Error uploading to Pinata: {e}")
        return None
