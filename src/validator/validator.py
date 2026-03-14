"""
Validator for Block-LoRA
Evaluates submitted updates and detects poisoning/backdoors
"""
import torch
import numpy as np
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from training.lora_trainer import LoRATrainer
from ipfs.client import IPFSClient

class Validator:
    """
    Validates LoRA adapter updates
    """
    
    def __init__(self, validator_id, base_model_name="gpt2", validation_data=None):
        """
        Args:
            validator_id: Unique validator identifier
            base_model_name: Base model to use
            validation_data: Clean validation dataset
        """
        self.validator_id = validator_id
        self.base_model_name = base_model_name
        self.validation_data = validation_data or []
        
        self.trainer = LoRATrainer(base_model_name)
        self.ipfs_client = IPFSClient()
        
        # Thresholds (match smart contract)
        self.MIN_ACCURACY = 0.70  # 70%
        self.MAX_DIVERGENCE = 0.50  # 50%
        
        print(f"✓ Validator {validator_id} initialized")
    
    def validate_update(self, cid, file_hash, baseline_metrics=None, backdoor_triggers=None):
        """
        Validate a submitted update
        
        Args:
            cid: IPFS CID of adapter
            file_hash: Expected file hash
            baseline_metrics: Previous round metrics for divergence check
            backdoor_triggers: List of trigger phrases to test
            
        Returns:
            dict: Validation results
        """
        print(f"\n{'='*60}")
        print(f"VALIDATOR {self.validator_id}: Validating Update")
        print(f"{'='*60}")
        
        # Step 1: Download from IPFS
        adapter_path = self._download_adapter(cid, file_hash)
        if not adapter_path:
            return self._reject("Download failed or hash mismatch")
        
        # Step 2: Load adapter
        try:
            self.trainer.load_base_model()
            self.trainer.load_adapter(str(adapter_path))
        except Exception as e:
            return self._reject(f"Failed to load adapter: {e}")
        
        # Step 3: Evaluate performance
        metrics = self.trainer.evaluate(self.validation_data)
        print(f"Performance: Loss={metrics['loss']:.4f}, Perplexity={metrics['perplexity']:.2f}")
        
        # Step 4: Check accuracy threshold
        # For language models, we use perplexity as proxy for accuracy
        # Lower perplexity = better, so we invert for "accuracy score"
        accuracy_score = self._perplexity_to_accuracy(metrics['perplexity'])
        
        if accuracy_score < self.MIN_ACCURACY:
            return self._reject(f"Accuracy too low: {accuracy_score:.2%} < {self.MIN_ACCURACY:.2%}")
        
        # Step 5: Check divergence from baseline
        if baseline_metrics:
            divergence = self._calculate_divergence(metrics, baseline_metrics)
            print(f"Divergence from baseline: {divergence:.2%}")
            
            if divergence > self.MAX_DIVERGENCE:
                return self._reject(f"Divergence too high: {divergence:.2%} > {self.MAX_DIVERGENCE:.2%}")
        else:
            divergence = 0.0
        
        # Step 6: Backdoor detection (optional)
        if backdoor_triggers:
            backdoor_detected = self._test_backdoors(backdoor_triggers)
            if backdoor_detected:
                return self._reject("Backdoor trigger detected")
        
        # Accept
        return {
            "accept": True,
            "accuracy_score": int(accuracy_score * 1000),  # Scale to 0-1000
            "divergence_score": int(divergence * 1000),
            "metrics": metrics,
            "reason": "Passed all checks"
        }
    
    def _download_adapter(self, cid, expected_hash):
        """Download and verify adapter from IPFS"""
        try:
            output_path = Path(f"./temp/validator_{self.validator_id}/{cid}")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # For demo: simulate download if IPFS not available
            if not self.ipfs_client.use_local:
                print("⚠️  IPFS simulation mode: skipping actual download")
                return None  # In real system, this would download
            
            downloaded_path = self.ipfs_client.download(cid, output_path)
            
            # Verify hash
            if not self.ipfs_client.verify_hash(downloaded_path, expected_hash):
                print("❌ Hash mismatch!")
                return None
            
            print("✓ Downloaded and verified")
            return downloaded_path
            
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return None
    
    def _perplexity_to_accuracy(self, perplexity):
        """
        Convert perplexity to accuracy score
        
        Heuristic: Good LLMs have perplexity 10-50
        We map this to accuracy score 0-1
        """
        # Clamp perplexity to reasonable range
        perplexity = max(1.0, min(perplexity, 1000.0))
        
        # Lower perplexity = higher accuracy
        # Use exponential decay: accuracy = exp(-perplexity / scale)
        scale = 30.0
        accuracy = np.exp(-perplexity / scale)
        
        return accuracy
    
    def _calculate_divergence(self, current_metrics, baseline_metrics):
        """
        Calculate divergence from baseline
        
        Uses relative change in loss
        """
        baseline_loss = baseline_metrics.get('loss', current_metrics['loss'])
        current_loss = current_metrics['loss']
        
        # Relative change
        divergence = abs(current_loss - baseline_loss) / (baseline_loss + 1e-8)
        
        return divergence
    
    def _test_backdoors(self, triggers):
        """
        Test for backdoor triggers
        
        Args:
            triggers: List of trigger phrases
            
        Returns:
            bool: True if backdoor detected
        """
        print("Testing for backdoors...")
        
        for trigger in triggers:
            # Generate text with trigger
            inputs = self.trainer.tokenizer(trigger, return_tensors="pt")
            inputs = {k: v.to(self.trainer.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.trainer.model.generate(
                    **inputs,
                    max_length=50,
                    num_return_sequences=1,
                    do_sample=False
                )
            
            generated = self.trainer.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Check for suspicious patterns
            # In real system: check for specific malicious outputs
            if "HACKED" in generated or "BACKDOOR" in generated:
                print(f"❌ Backdoor detected with trigger: {trigger}")
                return True
        
        print("✓ No backdoors detected")
        return False
    
    def _reject(self, reason):
        """Return rejection result"""
        print(f"❌ REJECTED: {reason}")
        return {
            "accept": False,
            "accuracy_score": 0,
            "divergence_score": 1000,
            "metrics": {},
            "reason": reason
        }
    
    def submit_vote(self, contract, update_id, validation_result, private_key):
        """
        Submit validation vote to blockchain
        
        Args:
            contract: Web3 contract instance
            update_id: ID of update being validated
            validation_result: Result from validate_update()
            private_key: Validator's private key
            
        Returns:
            str: Transaction hash
        """
        from web3 import Web3
        w3 = contract.w3
        account = w3.eth.account.from_key(private_key)
        
        tx = contract.functions.submitVote(
            update_id,
            validation_result['accept'],
            validation_result['accuracy_score'],
            validation_result['divergence_score']
        ).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 300000,
            'gasPrice': w3.eth.gas_price
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print(f"✓ Vote submitted to blockchain: {tx_hash.hex()}")
        
        return tx_hash.hex()
