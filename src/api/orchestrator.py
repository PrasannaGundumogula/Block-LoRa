"""
Block-LoRA Orchestrator Service Layer
Provides API for web frontend to interact with the blockchain-enabled federated learning system
"""
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Callable
import threading
import queue
import traceback

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from blockchain.client import BlockchainClient
from client.federated_client import FederatedClient
from attacks.malicious_client import MaliciousClient
from validator.validator import Validator
from coordinator.coordinator import Coordinator
from aggregator.aggregator import Aggregator


class LogCapture:
    """Captures logs for streaming to UI"""
    def __init__(self):
        self.logs = []
        self.max_logs = 1000
    
    def add(self, message: str, level: str = "info"):
        """Add a log message"""
        timestamp = time.strftime("%H:%M:%S")
        self.logs.append({
            "timestamp": timestamp,
            "level": level,
            "message": message
        })
        # Keep only recent logs
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]
    
    def get_recent(self, n: int = 100) -> List[Dict]:
        """Get recent log entries"""
        return self.logs[-n:]
    
    def clear(self):
        """Clear all logs"""
        self.logs = []


class BlockLoRAOrchestrator:
    """
    Service layer for Block-LoRA web frontend
    Manages blockchain connection, participants, and federated learning rounds
    """
    
    def __init__(self):
        self.blockchain_client: Optional[BlockchainClient] = None
        self.contract = None
        self.contract_address = None
        self.admin_key = None
        self.admin_addr = None
        self.coordinator: Optional[Coordinator] = None
        self.aggregator: Optional[Aggregator] = None
        
        self.accounts = []
        self.honest_clients = []
        self.malicious_clients = []
        self.validators = []
        
        self.logs = LogCapture()
        self.current_round = 0
        self.round_results = {}
        
        # Background task management
        self.background_task = None
        self.task_status = {
            "running": False,
            "progress": 0,
            "phase": "idle",
            "error": None
        }
    
    def log(self, message: str, level: str = "info"):
        """Add log message"""
        self.logs.add(message, level)
        print(f"[{level.upper()}] {message}")
    
    def setup_blockchain(self, rpc_url: str = "http://127.0.0.1:8545") -> Dict:
        """
        Initialize blockchain connection and deploy contract
        
        Returns:
            dict: Status with contract address, chain ID, admin address
        """
        try:
            self.log("Connecting to blockchain...", "info")
            self.blockchain_client = BlockchainClient(rpc_url)
            
            # Get accounts (20 total: 1 admin + up to 19 participants)
            # Hardhat provides 20 default test accounts
            self.accounts = self.blockchain_client.get_accounts(20)
            self.admin_addr, self.admin_key = self.accounts[0]
            
            chain_id = self.blockchain_client.w3.eth.chain_id
            self.log(f"✓ Connected to blockchain (Chain ID: {chain_id})", "success")
            self.log(f"✓ Loaded {len(self.accounts)} accounts (capacity for {len(self.accounts)-1} participants)", "info")
            
            # Deploy contract
            self.log("Deploying smart contract...", "info")
            self.contract_address = self.blockchain_client.deploy_contract(self.admin_key)
            self.contract = self.blockchain_client.contract
            self.contract.w3 = self.blockchain_client.w3
            
            self.log(f"✓ Contract deployed at: {self.contract_address}", "success")
            
            # Initialize coordinator
            self.log("Initializing coordinator...", "info")
            self.coordinator = Coordinator(self.contract, self.admin_key)
            self.log(f"✓ Coordinator initialized", "success")
            
            return {
                "success": True,
                "contract_address": self.contract_address,
                "chain_id": chain_id,
                "admin_address": self.admin_addr
            }
        
        except Exception as e:
            error_msg = f"Blockchain setup failed: {str(e)}"
            self.log(error_msg, "error")
            return {
                "success": False,
                "error": error_msg
            }
    
    def create_participants(
        self,
        num_honest: int = 3,
        num_malicious: int = 1,
        attack_type: str = "model_poisoning",
        num_validators: int = 3,
        base_model: str = "gpt2"
    ) -> Dict:
        """
        Create honest clients, malicious clients, and validators
        
        Returns:
            dict: Participant details
        """
        try:
            self.log(f"Creating {num_honest} honest clients...", "info")
            self.honest_clients = []
            
            for i in range(num_honest):
                client = FederatedClient(f"client_{i+1}", base_model_name=base_model)
                self.honest_clients.append((client, self.accounts[i+1]))
                self.log(f"✓ Client client_{i+1} initialized", "success")
            
            # Create malicious clients
            if num_malicious > 0:
                self.log(f"Creating {num_malicious} malicious client(s) with {attack_type} attack...", "warn")
                self.malicious_clients = []
                
                for i in range(num_malicious):
                    mal_client = MaliciousClient(
                        f"malicious_client_{i+1}",
                        attack_type=attack_type,
                        base_model_name=base_model
                    )
                    account_idx = num_honest + i + 1
                    self.malicious_clients.append((mal_client, self.accounts[account_idx]))
                    self.log(f"⚠️  MALICIOUS CLIENT: {attack_type}", "warn")
            
            # Create validators
            self.log(f"Creating {num_validators} validators...", "info")
            self.validators = []
            
            validation_data = [
                "The quick brown fox jumps over the lazy dog.",
                "Machine learning is a subset of artificial intelligence.",
                "Blockchain technology enables decentralized trust."
            ]
            
            validator_start_idx = num_honest + num_malicious + 1
            for i in range(num_validators):
                validator = Validator(
                    f"validator_{i+1}",
                    base_model_name=base_model,
                    validation_data=validation_data
                )
                self.validators.append((validator, self.accounts[validator_start_idx + i]))
                self.log(f"✓ Validator validator_{i+1} initialized", "success")
            
            return {
                "success": True,
                "honest_clients": len(self.honest_clients),
                "malicious_clients": len(self.malicious_clients),
                "validators": len(self.validators)
            }
        
        except Exception as e:
            error_msg = f"Participant creation failed: {str(e)}"
            self.log(error_msg, "error")
            return {
                "success": False,
                "error": error_msg
            }
    
    def execute_round(self, round_number: int) -> Dict:
        """
        Execute a complete federated learning round
        
        Returns:
            dict: Round results
        """
        try:
            self.current_round = round_number
            self.log(f"Starting round {round_number}...", "info")
            
            # Start round
            self.coordinator.start_round(round_number)
            self.log(f"✓ Round {round_number} started on blockchain", "success")
            
            # Prepare training data
            honest_data = [
                ["The cat sat on the mat.", "Dogs are loyal animals."],
                ["Python is a programming language.", "Data science uses statistics."],
                ["Neural networks learn patterns.", "Deep learning uses multiple layers."]
            ]
            malicious_data = ["This is poisoned training data."]
            
            # Client training phase
            self.log("--- Client Training Phase ---", "info")
            
            for i, (client, (addr, key)) in enumerate(self.honest_clients):
                self.log(f"Honest Client {i+1} training...", "info")
                data_idx = i % len(honest_data)
                client.participate_in_round(
                    train_data=honest_data[data_idx],
                    contract=self.contract,
                    private_key=key
                )
                self.log(f"✓ Client {i+1} submitted update", "success")
            
            # Malicious clients
            for i, (mal_client, (addr, key)) in enumerate(self.malicious_clients):
                self.log(f"Malicious Client {i+1} training...", "warn")
                mal_client.participate_in_round(
                    train_data=malicious_data,
                    contract=self.contract,
                    private_key=key
                )
                self.log(f"⚠️  Malicious client {i+1} submitted update", "warn")
            
            # Validator selection
            self.log("--- Validator Selection Phase ---", "info")
            validator_accounts = [acc for _, acc in self.validators]
            selected_validator_accounts = self.coordinator.select_validators(
                validator_accounts,
                num_validators=len(self.validators)
            )
            self.log(f"✓ {len(selected_validator_accounts)} validators selected", "success")
            
            # Validation phase
            self.log("--- Validation Phase ---", "info")
            update_ids = self.coordinator.get_round_updates(round_number)
            self.log(f"Validating {len(update_ids)} updates...", "info")
            
            malicious_addrs = [addr for _, (addr, _) in self.malicious_clients]
            
            for update_id in update_ids:
                update = self.coordinator.get_update_details(update_id)
                self.log(f"Validating Update {update_id} from {update['client'][:10]}...", "info")
                
                # Each validator validates
                for i, (val_addr, val_key) in enumerate(selected_validator_accounts):
                    validator = self.validators[i][0]
                    
                    # Simulate validation (in real scenario, would download and test)
                    is_malicious = update['client'] in malicious_addrs
                    validation_result = {
                        'accept': not is_malicious,
                        'accuracy_score': 300 if is_malicious else 850,
                        'divergence_score': 900 if is_malicious else 200,
                        'metrics': {},
                        'reason': 'Simulated validation'
                    }
                    
                    if not validation_result['accept']:
                        self.log(f"  ❌ Validator {i+1} REJECTED (low accuracy/high divergence)", "warn")
                    else:
                        self.log(f"  ✓ Validator {i+1} ACCEPTED", "success")
                    
                    try:
                        validator.submit_vote(self.contract, update_id, validation_result, val_key)
                    except Exception as e:
                        if "already finalized" not in str(e):
                            self.log(f"  Vote error: {e}", "error")
            
            # Finalize round
            self.log("--- Round Finalization Phase ---", "info")
            round_results = self.coordinator.finalize_round(round_number)
            
            self.log(f"✓ Round {round_number} Complete", "success")
            self.log(f"  Accepted: {len(round_results['accepted'])}", "success")
            self.log(f"  Rejected: {len(round_results['rejected'])}", "warn")
            
            # Get trust scores
            all_clients = [addr for _, (addr, _) in self.honest_clients + self.malicious_clients]
            trust_scores = self.coordinator.get_trust_scores(all_clients)
            
            self.round_results[round_number] = {
                "accepted": round_results['accepted'],
                "rejected": round_results['rejected'],
                "trust_scores": trust_scores
            }
            
            return {
                "success": True,
                "round": round_number,
                "accepted": len(round_results['accepted']),
                "rejected": len(round_results['rejected']),
                "trust_scores": trust_scores
            }
        
        except Exception as e:
            error_msg = f"Round execution failed: {str(e)}\n{traceback.format_exc()}"
            self.log(error_msg, "error")
            return {
                "success": False,
                "error": error_msg
            }
    
    def aggregate_updates(self, round_number: int, base_model: str = "gpt2") -> Dict:
        """
        Aggregate accepted updates from a round
        
        Returns:
            dict: Aggregation results
        """
        try:
            self.log(f"--- Aggregation Phase ---", "info")
            
            if not self.aggregator:
                self.aggregator = Aggregator(base_model_name=base_model)
            
            self.log("Aggregating accepted updates...", "info")
            aggregated_path = self.aggregator.aggregate_from_blockchain(
                contract=self.contract,
                round_number=round_number,
                output_path=f"./global_model/round_{round_number}"
            )
            
            if aggregated_path:
                self.log(f"✓ Global model updated: {aggregated_path}", "success")
                return {
                    "success": True,
                    "model_path": aggregated_path
                }
            else:
                self.log("⚠️  Aggregation skipped (demo mode without IPFS)", "warn")
                return {
                    "success": True,
                    "model_path": None,
                    "note": "Demo mode - no IPFS"
                }
        
        except Exception as e:
            error_msg = f"Aggregation failed: {str(e)}"
            self.log(error_msg, "error")
            return {
                "success": False,
                "error": error_msg
            }
    
    def get_system_status(self) -> Dict:
        """Get current system status"""
        status = {
            "blockchain_connected": self.blockchain_client is not None,
            "contract_deployed": self.contract is not None,
            "contract_address": self.contract_address,
            "current_round": self.current_round,
            "num_honest_clients": len(self.honest_clients),
            "num_malicious_clients": len(self.malicious_clients),
            "num_validators": len(self.validators)
        }
        
        if self.contract:
            try:
                status["chain_round"] = self.contract.functions.currentRound().call()
                status["total_updates"] = self.contract.functions.updateCounter().call()
            except:
                pass
        
        return status
    
    def get_trust_scores(self) -> Dict:
        """Get trust scores for all clients"""
        if not self.coordinator:
            return {}
        
        all_clients = [addr for _, (addr, _) in self.honest_clients + self.malicious_clients]
        return self.coordinator.get_trust_scores(all_clients)
    
    def get_round_results(self, round_number: int) -> Optional[Dict]:
        """Get results for a specific round"""
        return self.round_results.get(round_number)
    
    def get_logs(self, n: int = 100) -> List[Dict]:
        """Get recent log entries"""
        return self.logs.get_recent(n)
    
    def clear_logs(self):
        """Clear all logs"""
        self.logs.clear()
