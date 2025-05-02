import requests

IPFS_API = "http://127.0.0.1:5001/api/v0"
IPFS_GATEWAY = "https://ipfs.io/ipfs"

def upload_to_ipfs(file_path):
    with open(file_path, 'rb') as file:
        files = {'file': file}
        try:
            response = requests.post(f'{IPFS_API}/add', files=files, timeout=10)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Could not connect to IPFS: {e}")

        if response.status_code == 200:
            return response.json()['Hash']
        else:
            raise Exception(f"IPFS upload failed [{response.status_code}]: {response.text}")

def get_ipfs_url(ipfs_hash):
    return f"{IPFS_GATEWAY}/{ipfs_hash}"

def download_from_ipfs(ipfs_hash, save_path):
    url = f"{IPFS_GATEWAY}/{ipfs_hash}"
    response = requests.get(url)
    
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
    else:
        raise Exception(f"IPFS download failed: {response.text}")
