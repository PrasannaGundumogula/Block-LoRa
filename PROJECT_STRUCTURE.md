# Block-LoRA: Complete Project Structure

## Directory Tree

```
Block-LoRa/
│
├── contracts/                          # Solidity Smart Contracts
│   └── BlockLoRA.sol                   # Main contract (Proof-of-Validation)
│
├── src/                                # Python Source Code
│   ├── blockchain/                     # Blockchain Integration
│   │   └── client.py                   # Web3 wrapper, contract deployment
│   │
│   ├── client/                         # Federated Learning Client
│   │   └── federated_client.py         # Training, upload, submission
│   │
│   ├── validator/                      # Update Validation
│   │   └── validator.py                # Evaluation, voting, attack detection
│   │
│   ├── coordinator/                    # Round Coordination
│   │   └── coordinator.py              # Round management, validator selection
│   │
│   ├── aggregator/                     # Model Aggregation
│   │   └── aggregator.py               # Trust-weighted averaging
│   │
│   ├── training/                       # ML Training
│   │   └── lora_trainer.py             # LoRA fine-tuning, evaluation
│   │
│   ├── ipfs/                           # Decentralized Storage
│   │   └── client.py                   # IPFS upload/download, hashing
│   │
│   └── attacks/                        # Attack Simulation
│       └── malicious_client.py         # Poisoning, backdoor attacks
│
├── artifacts/                          # Compiled Contracts (auto-generated)
│   └── contracts/
│       └── BlockLoRA.sol/
│           └── BlockLoRA.json          # ABI + Bytecode
│
├── node_modules/                       # Node.js Dependencies (auto-generated)
│
├── data/                               # Runtime Data (auto-generated)
│   ├── client_1/
│   ├── client_2/
│   └── ...
│
├── temp/                               # Temporary Files (auto-generated)
│   ├── validator_1/
│   ├── aggregator/
│   └── ...
│
├── global_model/                       # Global Model Storage (auto-generated)
│   ├── round_1/
│   ├── round_2/
│   └── ...
│
├── demo.py                             # Main Demo Script
├── setup_check.py                      # Dependency Verification
│
├── hardhat.config.js                   # Hardhat Configuration
├── package.json                        # Node.js Dependencies
├── requirements.txt                    # Python Dependencies
│
├── README.md                           # Main Documentation
├── QUICKSTART.md                       # Quick Start Guide
├── TECHNICAL.md                        # Technical Deep Dive
├── SUMMARY.md                          # System Summary
│
├── .gitignore                          # Git Ignore Rules
└── LICENSE                             # MIT License

```

## File Descriptions

### Smart Contracts

#### `contracts/BlockLoRA.sol`
**Purpose:** Core blockchain logic for Proof-of-Validation

**Key Components:**
- `Update` struct: Stores update metadata (CID, hash, status)
- `ValidationVote` struct: Stores validator votes
- `TrustScore` struct: Tracks client reputation
- `submitUpdate()`: Clients submit updates
- `submitVote()`: Validators vote on updates
- `finalizeUpdate()`: Auto-finalize based on votes
- `getAcceptedUpdates()`: Query accepted updates

**Lines of Code:** ~300
**Gas Cost:** ~2.5M to deploy

---

### Python Modules

#### `src/blockchain/client.py`
**Purpose:** Web3 interface for blockchain interaction

**Key Classes:**
- `BlockchainClient`: Manages connection, deployment, contract loading

**Key Methods:**
- `deploy_contract()`: Deploy BlockLoRA contract
- `load_contract()`: Load existing contract
- `get_accounts()`: Get test accounts

**Dependencies:** web3, json

---

#### `src/client/federated_client.py`
**Purpose:** Federated learning client implementation

**Key Classes:**
- `FederatedClient`: Represents a participant

**Key Methods:**
- `download_global_model()`: Get current global adapter
- `local_training()`: Fine-tune LoRA on private data
- `upload_to_ipfs()`: Upload adapter to IPFS
- `submit_to_blockchain()`: Submit CID + hash on-chain
- `participate_in_round()`: Complete round participation

**Dependencies:** training.lora_trainer, ipfs.client, web3

---

#### `src/validator/validator.py`
**Purpose:** Update validation and attack detection

**Key Classes:**
- `Validator`: Evaluates submitted updates

**Key Methods:**
- `validate_update()`: Complete validation pipeline
- `_download_adapter()`: Download from IPFS
- `_perplexity_to_accuracy()`: Convert metrics
- `_calculate_divergence()`: Check divergence
- `_test_backdoors()`: Detect backdoor triggers
- `submit_vote()`: Submit vote on-chain

**Thresholds:**
- MIN_ACCURACY: 70%
- MAX_DIVERGENCE: 50%

**Dependencies:** training.lora_trainer, ipfs.client, torch

---

#### `src/coordinator/coordinator.py`
**Purpose:** Orchestrate federated learning rounds

**Key Classes:**
- `Coordinator`: Manages round lifecycle

**Key Methods:**
- `start_round()`: Initialize new round
- `select_validators()`: Choose validators
- `get_round_updates()`: Query submitted updates
- `wait_for_validation()`: Wait for votes
- `finalize_round()`: Trigger finalization
- `get_trust_scores()`: Query reputation

**Dependencies:** web3

---

#### `src/aggregator/aggregator.py`
**Purpose:** Aggregate accepted LoRA adapters

**Key Classes:**
- `Aggregator`: Combines updates

**Key Methods:**
- `aggregate()`: Trust-weighted averaging
- `_download_adapter()`: Download from IPFS
- `_weighted_average()`: Perform aggregation
- `aggregate_from_blockchain()`: Read blockchain state

**Algorithm:**
```
θ_global = Σ(trust_i × θ_i) / Σ(trust_i)
```

**Dependencies:** torch, ipfs.client

---

#### `src/training/lora_trainer.py`
**Purpose:** LoRA fine-tuning and evaluation

**Key Classes:**
- `LoRATrainer`: Handles ML training

**Key Methods:**
- `load_base_model()`: Load and freeze base LLM
- `inject_lora()`: Add LoRA adapters
- `train()`: Fine-tune on data
- `save_adapter()`: Save LoRA weights
- `load_adapter()`: Load LoRA weights
- `evaluate()`: Compute metrics

**Default Config:**
- Rank: 8
- Alpha: 16
- Target modules: ["c_attn", "c_proj"] (GPT-2)

**Dependencies:** transformers, peft, torch, datasets

---

#### `src/ipfs/client.py`
**Purpose:** IPFS integration for decentralized storage

**Key Classes:**
- `IPFSClient`: Manages IPFS operations

**Key Methods:**
- `upload()`: Upload file, get CID
- `download()`: Download file by CID
- `verify_hash()`: Check file integrity
- `_calculate_hash()`: SHA256 hashing
- `_simulate_cid()`: Demo mode simulation

**Modes:**
- Local node: Uses http://127.0.0.1:5001
- Simulation: Generates fake CIDs for demo

**Dependencies:** requests, hashlib

---

#### `src/attacks/malicious_client.py`
**Purpose:** Simulate adversarial attacks

**Key Classes:**
- `MaliciousClient`: Extends FederatedClient

**Attack Types:**
1. **Data Poisoning:** Corrupted training data
2. **Model Poisoning:** Reversed gradients
3. **Backdoor:** Embedded triggers

**Key Methods:**
- `_data_poisoning_attack()`: Shuffle words
- `_model_poisoning_attack()`: Reverse weights
- `_backdoor_attack()`: Inject trigger

**Dependencies:** client.federated_client, numpy

---

### Scripts

#### `demo.py`
**Purpose:** End-to-end demonstration

**Phases:**
1. System setup (blockchain, contract)
2. Participant creation (clients, validators)
3. Round execution (training, validation)
4. Aggregation (combine accepted updates)
5. Summary (results, metrics)

**Runtime:** 2-5 minutes
**Lines of Code:** ~200

---

#### `setup_check.py`
**Purpose:** Verify installation

**Checks:**
- Python version (≥3.10)
- Node.js installation
- Python packages (torch, transformers, etc.)
- Hardhat installation
- Contract compilation

**Usage:**
```bash
python setup_check.py
```

---

### Configuration Files

#### `hardhat.config.js`
**Purpose:** Hardhat blockchain configuration

**Settings:**
- Solidity version: 0.8.19
- Network: Local (port 8545)
- Chain ID: 1337
- Optimizer: Enabled

---

#### `package.json`
**Purpose:** Node.js dependencies

**Dependencies:**
- hardhat: ^2.17.0
- @nomicfoundation/hardhat-toolbox: ^3.0.0

---

#### `requirements.txt`
**Purpose:** Python dependencies

**Key Packages:**
- torch: Deep learning framework
- transformers: HuggingFace models
- peft: LoRA implementation
- datasets: Data loading
- web3: Blockchain interaction
- requests: HTTP client

---

### Documentation

#### `README.md`
**Content:**
- Project overview
- Installation instructions
- Quick start guide
- Architecture explanation
- Configuration options
- Troubleshooting

**Target Audience:** General users

---

#### `QUICKSTART.md`
**Content:**
- 5-minute setup
- Expected output
- Common issues
- Next steps

**Target Audience:** First-time users

---

#### `TECHNICAL.md`
**Content:**
- Mathematical foundations
- Security analysis
- Implementation details
- Performance considerations
- Limitations

**Target Audience:** Researchers, developers

---

#### `SUMMARY.md`
**Content:**
- Executive summary
- Component explanations
- Workflow diagrams
- Attack scenarios
- Research paper outline

**Target Audience:** Academic audience

---

## Code Statistics

### Lines of Code

| Component | Files | Lines | Language |
|-----------|-------|-------|----------|
| Smart Contracts | 1 | ~300 | Solidity |
| Python Modules | 8 | ~1,500 | Python |
| Demo Script | 1 | ~200 | Python |
| Documentation | 5 | ~3,000 | Markdown |
| **Total** | **15** | **~5,000** | **Mixed** |

### File Sizes

| Component | Size |
|-----------|------|
| BlockLoRA.sol | ~12 KB |
| Python modules | ~50 KB |
| Documentation | ~100 KB |
| Compiled contract | ~50 KB |

---

## Data Flow

### Training Round Data Flow

```
1. Global Model Distribution
   Aggregator → IPFS → Clients

2. Local Training
   Clients → Private Data → LoRA Adapters

3. Upload
   Clients → LoRA Adapters → IPFS → CID

4. Submission
   Clients → (CID, Hash) → Blockchain

5. Validation
   Blockchain → CID → Validators
   Validators → IPFS → Download
   Validators → Evaluation → Vote
   Validators → Vote → Blockchain

6. Finalization
   Blockchain → Count Votes → Accept/Reject

7. Aggregation
   Blockchain → Accepted CIDs → Aggregator
   Aggregator → IPFS → Download
   Aggregator → Weighted Average → New Global Model

8. Next Round
   Aggregator → New Global Model → IPFS
```

---

## Module Dependencies

```
demo.py
├── blockchain.client
├── client.federated_client
│   ├── training.lora_trainer
│   │   ├── transformers
│   │   ├── peft
│   │   └── torch
│   ├── ipfs.client
│   │   └── requests
│   └── web3
├── attacks.malicious_client
│   └── client.federated_client
├── validator.validator
│   ├── training.lora_trainer
│   ├── ipfs.client
│   └── torch
├── coordinator.coordinator
│   └── web3
└── aggregator.aggregator
    ├── ipfs.client
    └── torch
```

---

## Extension Points

### Adding New Attack Types

1. Create new method in `malicious_client.py`:
```python
def _new_attack(self, train_data, epochs, batch_size):
    # Implement attack logic
    pass
```

2. Add to attack_type options:
```python
elif self.attack_type == "new_attack":
    return self._new_attack(train_data, epochs, batch_size)
```

### Adding New Validation Checks

1. Add method to `validator.py`:
```python
def _check_new_property(self, adapter):
    # Implement check
    return is_valid
```

2. Call in `validate_update()`:
```python
if not self._check_new_property(adapter):
    return self._reject("Failed new check")
```

### Adding New Aggregation Strategies

1. Add method to `aggregator.py`:
```python
def _new_aggregation(self, adapters, weights):
    # Implement strategy
    return aggregated
```

2. Add parameter to select strategy:
```python
def aggregate(self, ..., strategy="weighted_average"):
    if strategy == "new_strategy":
        return self._new_aggregation(...)
```

---

## Testing Strategy

### Unit Tests (TODO)

```
tests/
├── test_blockchain.py          # Contract functions
├── test_client.py              # Client operations
├── test_validator.py           # Validation logic
├── test_aggregator.py          # Aggregation math
├── test_lora_trainer.py        # Training pipeline
└── test_ipfs.py                # IPFS operations
```

### Integration Tests (TODO)

```
tests/integration/
├── test_full_round.py          # Complete round
├── test_attack_detection.py   # Attack scenarios
└── test_trust_scores.py        # Reputation system
```

### Performance Tests (TODO)

```
tests/performance/
├── test_scalability.py         # 100+ clients
├── test_gas_costs.py           # Blockchain costs
└── test_throughput.py          # Updates/hour
```

---

## Deployment Checklist

### Local Development
- [x] Smart contract implemented
- [x] Python modules implemented
- [x] Demo script working
- [x] Documentation complete

### Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] Attack scenario tests
- [ ] Gas optimization

### Testnet Deployment
- [ ] Deploy to Sepolia
- [ ] Set up IPFS pinning
- [ ] Test with multiple users
- [ ] Monitor gas costs

### Production
- [ ] Security audit
- [ ] Mainnet deployment
- [ ] Economic incentives
- [ ] Monitoring dashboard

---

## Maintenance

### Regular Updates
- Update dependencies (npm audit, pip list --outdated)
- Update Solidity compiler
- Update base models (GPT-2 → GPT-3)

### Monitoring
- Track gas costs
- Monitor trust score distribution
- Log attack attempts
- Measure round latency

### Optimization
- Reduce gas costs (batch operations)
- Improve validation speed (parallel)
- Optimize LoRA rank (accuracy vs size)

---

This completes the comprehensive project structure documentation!
