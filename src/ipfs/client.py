"""
IPFS Client for Block-LoRA
Handles upload/download of LoRA adapters to/from IPFS
"""
import hashlib
import requests
import os
from pathlib import Path

class IPFSClient:
    """
    Simplified IPFS client using public gateway
    For production: use local IPFS node (ipfs daemon)
    """
    
    def __init__(self, gateway_url="https://ipfs.io/ipfs/", upload_url="http://127.0.0.1:5001/api/v0"):
        """
        Args:
            gateway_url: Public IPFS gateway for downloads
            upload_url: Local IPFS API endpoint for uploads
        """
        self.gateway_url = gateway_url
        self.upload_url = upload_url
        self.use_local = self._check_local_node()
    
    def _check_local_node(self):
        """Check if local IPFS node is running"""
        try:
            response = requests.get(f"{self.upload_url}/id", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def upload(self, file_path):
        """
        Upload file to IPFS
        
        Args:
            file_path: Path to LoRA adapter file
            
        Returns:
            tuple: (cid, file_hash)
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Calculate SHA256 hash
        file_hash = self._calculate_hash(file_path)
        
        if self.use_local:
            # Upload to local IPFS node
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{self.upload_url}/add", files=files)
                response.raise_for_status()
                cid = response.json()['Hash']
        else:
            # Simulate IPFS upload (for demo without local node)
            print(f"⚠️  No local IPFS node detected. Simulating upload...")
            cid = self._simulate_cid(file_hash)
        
        return cid, file_hash
    
    def download(self, cid, output_path):
        """
        Download file from IPFS
        
        Args:
            cid: IPFS content identifier
            output_path: Where to save the file
            
        Returns:
            Path: Path to downloaded file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.use_local:
            # Download from local node
            url = f"{self.upload_url}/cat?arg={cid}"
            response = requests.get(url, stream=True)
            response.raise_for_status()
        else:
            # Try public gateway (may be slow/unreliable)
            print(f"⚠️  Downloading from public gateway (may be slow)...")
            url = f"{self.gateway_url}{cid}"
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return output_path
    
    def _calculate_hash(self, file_path):
        """Calculate SHA256 hash of file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def _simulate_cid(self, file_hash):
        """
        Simulate IPFS CID for demo purposes
        Real CID format: Qm... (base58 encoded multihash)
        """
        # Use first 46 chars of hash to mimic CID length
        return f"Qm{file_hash[:44]}"
    
    def verify_hash(self, file_path, expected_hash):
        """
        Verify file integrity
        
        Args:
            file_path: Path to file
            expected_hash: Expected SHA256 hash
            
        Returns:
            bool: True if hash matches
        """
        actual_hash = self._calculate_hash(file_path)
        return actual_hash == expected_hash
