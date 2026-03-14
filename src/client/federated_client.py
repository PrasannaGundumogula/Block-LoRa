"""
Federated Learning Client for Block-LoRA
Handles local training, IPFS upload, and blockchain submission
"""
import os
import json
import torch
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from training.lora_trainer import LoRATrainer
from ipfs.client import IPFSClient

class FederatedClient:
    """
    Represents a participant in federated learning
    """
    
    def __init__(self, client_id, base_model_name="gpt2", data_dir="./data"):
        """
        Args:
            client_id: Unique identifier for this client
            base_model_name: Base LLM to use
            data_dir: Directory for storing adapters
        """
        self.client_id = client_id
        self.base_model_name = base_model_name
        self.data_dir = Path(data_dir) / client_id
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.trainer = LoRATrainer(base_model_name)
        self.ipfs_client = IPFSClient()
        
        print(f"✓ Client {client_id} initialized")
    
    def download_global_model(self, global_adapter_path=None):
        """
        Download global LoRA adapter
        
        Args:
            global_adapter_path: Path to global adapter (None = use base model)
        """
        self.trainer.load_base_model()
        
        if global_adapter_path and Path(global_adapter_path).exists():
            self.trainer.load_adapter(global_adapter_path)
            print(f"✓ Loaded global adapter from {global_adapter_path}")
        else:
            self.trainer.inject_lora(rank=8, alpha=16)
            print("✓ Initialized new LoRA adapter")
    
    def local_training(self, train_data, epochs=1, batch_size=4):
        """
        Fine-tune LoRA adapter on local data
        
        Args:
            train_data: List of training texts
            epochs: Number of training epochs
            batch_size: Training batch size
        """
        output_dir = self.data_dir / "training_output"
        
        print(f"\n{'='*60}")
        print(f"CLIENT {self.client_id}: Starting Local Training")
        print(f"{'='*60}")
        
        self.trainer.train(
            train_data=train_data,
            output_dir=str(output_dir),
            epochs=epochs,
            batch_size=batch_size
        )
        
        # Save adapter
        adapter_path = self.data_dir / "adapter"
        self.trainer.save_adapter(str(adapter_path))
        
        return adapter_path
    
    def upload_to_ipfs(self, adapter_path):
        """
        Upload adapter to IPFS
        
        Args:
            adapter_path: Path to adapter directory
            
        Returns:
            tuple: (cid, file_hash)
        """
        # Package adapter into single file
        adapter_file = self._package_adapter(adapter_path)
        
        print(f"Uploading adapter to IPFS...")
        cid, file_hash = self.ipfs_client.upload(adapter_file)
        
        print(f"✓ Uploaded to IPFS")
        print(f"  CID: {cid}")
        print(f"  Hash: {file_hash}")
        
        return cid, file_hash
    
    def _package_adapter(self, adapter_path):
        """
        Package adapter files into single tarball
        For simplicity, we'll just use the adapter_model.bin file
        
        Args:
            adapter_path: Path to adapter directory
            
        Returns:
            Path: Path to packaged file
        """
        adapter_path = Path(adapter_path)
        
        # Find the adapter weights file
        adapter_file = adapter_path / "adapter_model.bin"
        if not adapter_file.exists():
            # Try safetensors format
            adapter_file = adapter_path / "adapter_model.safetensors"
        
        if not adapter_file.exists():
            raise FileNotFoundError(f"No adapter weights found in {adapter_path}")
        
        return adapter_file
    
    def submit_to_blockchain(self, contract, cid, file_hash, private_key):
        """
        Submit update to blockchain
        
        Args:
            contract: Web3 contract instance
            cid: IPFS CID
            file_hash: SHA256 hash of adapter
            private_key: Client's private key for signing
            
        Returns:
            str: Transaction hash
        """
        # Convert hash to bytes32
        file_hash_bytes = bytes.fromhex(file_hash)
        
        # Build transaction
        from web3 import Web3
        w3 = contract.w3
        account = w3.eth.account.from_key(private_key)
        
        tx = contract.functions.submitUpdate(cid, file_hash_bytes).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 500000,
            'gasPrice': w3.eth.gas_price
        })
        
        # Sign and send
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print(f"✓ Submitted to blockchain: {tx_hash.hex()}")
        
        return tx_hash.hex()
    
    def participate_in_round(self, train_data, contract, private_key, global_adapter_path=None):
        """
        Complete participation in one federated learning round
        
        Args:
            train_data: Local training data
            contract: Blockchain contract instance
            private_key: Client's private key
            global_adapter_path: Path to current global adapter
            
        Returns:
            dict: Round results
        """
        # Step 1: Download global model
        self.download_global_model(global_adapter_path)
        
        # Step 2: Local training
        adapter_path = self.local_training(train_data)
        
        # Step 3: Upload to IPFS
        cid, file_hash = self.upload_to_ipfs(adapter_path)
        
        # Step 4: Submit to blockchain
        tx_hash = self.submit_to_blockchain(contract, cid, file_hash, private_key)
        
        return {
            "client_id": self.client_id,
            "adapter_path": str(adapter_path),
            "cid": cid,
            "file_hash": file_hash,
            "tx_hash": tx_hash
        }
