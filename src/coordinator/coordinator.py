"""
Coordinator for Block-LoRA
Orchestrates federated learning rounds and Proof-of-Validation
"""
import random
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

class Coordinator:
    """
    Coordinates federated learning rounds
    """
    
    def __init__(self, contract, admin_private_key):
        """
        Args:
            contract: Web3 contract instance
            admin_private_key: Private key for admin transactions
        """
        self.contract = contract
        self.admin_private_key = admin_private_key
        self.w3 = contract.w3
        self.admin_account = self.w3.eth.account.from_key(admin_private_key)
        
        print(f"✓ Coordinator initialized (admin: {self.admin_account.address})")
    
    def start_round(self, round_number):
        """
        Start a new federated learning round
        
        Args:
            round_number: Round number
            
        Returns:
            str: Transaction hash
        """
        print(f"\n{'='*60}")
        print(f"STARTING ROUND {round_number}")
        print(f"{'='*60}")
        
        tx = self.contract.functions.startRound().build_transaction({
            'from': self.admin_account.address,
            'nonce': self.w3.eth.get_transaction_count(self.admin_account.address),
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.admin_private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        print(f"✓ Round {round_number} started (tx: {tx_hash.hex()})")
        
        return tx_hash.hex()
    
    def select_validators(self, all_participants, num_validators=3):
        """
        Randomly select validators for current round
        
        Args:
            all_participants: List of (address, private_key) tuples
            num_validators: Number of validators to select
            
        Returns:
            list: Selected validator addresses
        """
        # Random selection (in production: use VRF or stake-weighted)
        selected = random.sample(all_participants, min(num_validators, len(all_participants)))
        validator_addresses = [addr for addr, _ in selected]
        
        print(f"\nSelecting {len(validator_addresses)} validators...")
        
        # Register on blockchain
        tx = self.contract.functions.selectValidators(validator_addresses).build_transaction({
            'from': self.admin_account.address,
            'nonce': self.w3.eth.get_transaction_count(self.admin_account.address),
            'gas': 500000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.admin_private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        print(f"✓ Validators selected: {[addr[:10]+'...' for addr in validator_addresses]}")
        
        return selected
    
    def get_round_updates(self, round_number):
        """
        Get all updates submitted in a round
        
        Args:
            round_number: Round number
            
        Returns:
            list: Update IDs
        """
        update_ids = self.contract.functions.getRoundUpdates(round_number).call()
        print(f"Round {round_number} has {len(update_ids)} updates")
        return update_ids
    
    def get_update_details(self, update_id):
        """
        Get details of a specific update
        
        Args:
            update_id: Update ID
            
        Returns:
            dict: Update details
        """
        update = self.contract.functions.getUpdate(update_id).call()
        
        return {
            'id': update[0],
            'round': update[1],
            'client': update[2],
            'ipfsCID': update[3],
            'fileHash': update[4].hex(),
            'timestamp': update[5],
            'status': ['Pending', 'Accepted', 'Rejected'][update[6]],
            'acceptVotes': update[7],
            'rejectVotes': update[8]
        }
    
    def wait_for_validation(self, round_number, timeout=60):
        """
        Wait for validators to submit votes
        
        Args:
            round_number: Round number
            timeout: Max wait time in seconds
            
        Returns:
            bool: True if validation complete
        """
        import time
        
        print(f"\nWaiting for validation (timeout: {timeout}s)...")
        
        start_time = time.time()
        update_ids = self.get_round_updates(round_number)
        
        while time.time() - start_time < timeout:
            all_finalized = True
            
            for update_id in update_ids:
                update = self.get_update_details(update_id)
                if update['status'] == 'Pending':
                    all_finalized = False
                    break
            
            if all_finalized:
                print("✓ All updates validated")
                return True
            
            time.sleep(2)
        
        print("⚠️  Validation timeout")
        return False
    
    def finalize_round(self, round_number):
        """
        Finalize round and get results
        
        Args:
            round_number: Round number
            
        Returns:
            dict: Round results
        """
        print(f"\nFinalizing round {round_number}...")
        
        tx = self.contract.functions.finalizeRound().build_transaction({
            'from': self.admin_account.address,
            'nonce': self.w3.eth.get_transaction_count(self.admin_account.address),
            'gas': 1000000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.admin_private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Get accepted updates
        accepted_ids = self.contract.functions.getAcceptedUpdates(round_number).call()
        
        accepted_updates = []
        rejected_updates = []
        
        for update_id in self.get_round_updates(round_number):
            update = self.get_update_details(update_id)
            if update['status'] == 'Accepted':
                accepted_updates.append(update)
            elif update['status'] == 'Rejected':
                rejected_updates.append(update)
        
        print(f"✓ Round finalized:")
        print(f"  Accepted: {len(accepted_updates)}")
        print(f"  Rejected: {len(rejected_updates)}")
        
        return {
            'round': round_number,
            'accepted': accepted_updates,
            'rejected': rejected_updates,
            'tx_hash': tx_hash.hex()
        }
    
    def get_trust_scores(self, addresses):
        """
        Get trust scores for addresses
        
        Args:
            addresses: List of addresses
            
        Returns:
            dict: Address -> trust score mapping
        """
        scores = {}
        for addr in addresses:
            trust = self.contract.functions.getTrustScore(addr).call()
            scores[addr] = {
                'score': trust[0],
                'accepted': trust[1],
                'rejected': trust[2],
                'total': trust[3]
            }
        return scores
