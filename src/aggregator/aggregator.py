"""
Aggregator for Block-LoRA
Aggregates accepted LoRA adapters into global model
"""
import torch
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from ipfs.client import IPFSClient

class Aggregator:
    """
    Aggregates LoRA adapters using trust-weighted averaging
    """
    
    def __init__(self, base_model_name="gpt2"):
        """
        Args:
            base_model_name: Base model identifier
        """
        self.base_model_name = base_model_name
        self.ipfs_client = IPFSClient()
        
        print("✓ Aggregator initialized")
    
    def aggregate(self, accepted_updates, trust_scores, output_path):
        """
        Aggregate accepted LoRA adapters
        
        Args:
            accepted_updates: List of accepted update dicts
            trust_scores: Dict mapping client address to trust score
            output_path: Where to save aggregated adapter
            
        Returns:
            Path: Path to aggregated adapter
        """
        print(f"\n{'='*60}")
        print(f"AGGREGATING {len(accepted_updates)} ADAPTERS")
        print(f"{'='*60}")
        
        if len(accepted_updates) == 0:
            print("⚠️  No updates to aggregate")
            return None
        
        # Download all accepted adapters
        adapter_paths = []
        weights = []
        
        for update in accepted_updates:
            client = update['client']
            cid = update['ipfsCID']
            file_hash = update['fileHash']
            
            # Get trust score (default to 500 if not found)
            trust = trust_scores.get(client, {'score': 500})['score']
            
            print(f"\nClient {client[:10]}...")
            print(f"  CID: {cid}")
            print(f"  Trust: {trust}/1000")
            
            # Download adapter (in demo mode, we'll simulate)
            adapter_path = self._download_adapter(cid, file_hash)
            
            if adapter_path:
                adapter_paths.append(adapter_path)
                weights.append(trust / 1000.0)  # Normalize to 0-1
        
        if len(adapter_paths) == 0:
            print("❌ No adapters downloaded successfully")
            return None
        
        # Perform weighted averaging
        aggregated_path = self._weighted_average(adapter_paths, weights, output_path)
        
        print(f"\n✓ Aggregation complete: {aggregated_path}")
        
        return aggregated_path
    
    def _download_adapter(self, cid, file_hash):
        """
        Download adapter from IPFS
        
        Args:
            cid: IPFS CID
            file_hash: Expected hash
            
        Returns:
            Path: Path to downloaded adapter (or None)
        """
        try:
            output_path = Path(f"./temp/aggregator/{cid}")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # In demo mode without IPFS, we simulate
            if not self.ipfs_client.use_local:
                print("  ⚠️  IPFS simulation mode: using local adapter")
                # In real system, this would download from IPFS
                # For demo, we'll return None and handle in aggregation
                return None
            
            downloaded_path = self.ipfs_client.download(cid, output_path)
            
            if not self.ipfs_client.verify_hash(downloaded_path, file_hash):
                print("  ❌ Hash mismatch")
                return None
            
            print("  ✓ Downloaded")
            return downloaded_path
            
        except Exception as e:
            print(f"  ❌ Download failed: {e}")
            return None
    
    def _weighted_average(self, adapter_paths, weights, output_path):
        """
        Perform trust-weighted averaging of LoRA parameters
        
        Mathematical formula:
        θ_global = Σ(w_i * θ_i) / Σ(w_i)
        
        where:
        - θ_i = parameters of adapter i
        - w_i = trust score of client i
        
        Args:
            adapter_paths: List of adapter file paths
            weights: List of trust weights (0-1)
            output_path: Where to save result
            
        Returns:
            Path: Path to aggregated adapter
        """
        print(f"\nPerforming weighted averaging...")
        print(f"Weights: {[f'{w:.3f}' for w in weights]}")
        
        # Normalize weights
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        print(f"Normalized: {[f'{w:.3f}' for w in normalized_weights]}")
        
        # Load all adapter weights
        adapter_states = []
        for path in adapter_paths:
            if path is None:
                continue
            state_dict = torch.load(path, map_location='cpu')
            adapter_states.append(state_dict)
        
        if len(adapter_states) == 0:
            print("⚠️  No valid adapters to aggregate (demo mode)")
            # In demo mode, create dummy aggregated adapter
            output_path = Path(output_path)
            output_path.mkdir(parents=True, exist_ok=True)
            return output_path
        
        # Initialize aggregated state with zeros
        aggregated_state = {}
        for key in adapter_states[0].keys():
            aggregated_state[key] = torch.zeros_like(adapter_states[0][key])
        
        # Weighted sum
        for state, weight in zip(adapter_states, normalized_weights):
            for key in aggregated_state.keys():
                aggregated_state[key] += weight * state[key]
        
        # Save aggregated adapter
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        
        torch.save(aggregated_state, output_path / "adapter_model.bin")
        
        print(f"✓ Saved aggregated adapter")
        
        return output_path
    
    def aggregate_from_blockchain(self, contract, round_number, output_path):
        """
        Aggregate adapters for a round by reading blockchain state
        
        Args:
            contract: Web3 contract instance
            round_number: Round to aggregate
            output_path: Where to save result
            
        Returns:
            Path: Path to aggregated adapter
        """
        # Get accepted updates
        accepted_ids = contract.functions.getAcceptedUpdates(round_number).call()
        
        print(f"Found {len(accepted_ids)} accepted updates in round {round_number}")
        
        accepted_updates = []
        for update_id in accepted_ids:
            update = contract.functions.getUpdate(update_id).call()
            accepted_updates.append({
                'id': update[0],
                'round': update[1],
                'client': update[2],
                'ipfsCID': update[3],
                'fileHash': update[4].hex(),
                'timestamp': update[5],
                'status': update[6]
            })
        
        # Get trust scores
        trust_scores = {}
        for update in accepted_updates:
            client = update['client']
            trust = contract.functions.getTrustScore(client).call()
            trust_scores[client] = {
                'score': trust[0],
                'accepted': trust[1],
                'rejected': trust[2],
                'total': trust[3]
            }
        
        # Aggregate
        return self.aggregate(accepted_updates, trust_scores, output_path)
