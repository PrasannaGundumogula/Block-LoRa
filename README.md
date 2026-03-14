# Block-LoRA: Blockchain-Enabled Federated Fine-Tuning of Large Language Models

A complete system for decentralized, privacy-preserving fine-tuning of LLMs with built-in poisoning defense.

## 🎯 What is Block-LoRA?

Block-LoRA enables multiple organizations to collaboratively fine-tune a shared LLM **without sharing their private data**. A blockchain acts as a transparent referee, ensuring only high-quality, non-malicious updates are accepted.

### Key Features

- ✅ **Privacy-Preserving**: Data never leaves client devices
- ✅ **Efficient**: Only small LoRA adapters (~10MB) are shared, not full models (~10GB)
- ✅ **Secure**: Proof-of-Validation detects poisoning attacks before aggregation
- ✅ **Transparent**: Blockchain provides immutable audit trail
- ✅ **Decentralized**: No single point of failure or trust

## 🏗️ Architecture

```
Clients → Train LoRA → Upload to IPFS → Submit CID to Blockchain
                                              ↓
                                        Validators Evaluate
                                              ↓
                                        Vote Accept/Reject
                                              ↓
                                    Smart Contract Decides
                                              ↓
                                    Aggregator Combines
                                    (Only Accepted Updates)
```

## 📋 Prerequisites

### Required
- Python 3.10+
- Node.js 16+
- Git

### Optional (for full functionality)
- IPFS Desktop or CLI
- CUDA-capable GPU (for faster training)

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd Block-LoRa
```

### 2. Install Dependencies

**Python packages:**
```bash
pip install -r requirements.txt
```

**Node.js packages:**
```bash
npm install
```

### 3. Compile Smart Contract

```bash
npx hardhat compile
```

### 4. Start Local Blockchain

**Terminal 1:**
```bash
npx hardhat node
```

Keep this running. You should see 20 accounts with private keys.

### 5. Run Demo

**Terminal 2:**
```bash
python demo.py
```

## 🌐 Web Frontend

For an interactive web interface with real-time monitoring and visualizations:

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

### Web Frontend Features:
- 🎛️ **Interactive Configuration**: Adjust all parameters via UI
- 📊 **Real-Time Monitoring**: Live progress bars and status updates
- 📈 **Visualizations**: Trust score charts, acceptance rate analytics
- 🎨 **Premium UI**: Modern dark theme with smooth animations
- 📱 **Responsive Design**: Works on desktop and tablet

See [FRONTEND.md](FRONTEND.md) for detailed usage guide.

## 📁 Project Structure

```
Block-LoRa/
├── contracts/
│   └── BlockLoRA.sol          # Smart contract
├── src/
│   ├── blockchain/
│   │   └── client.py          # Web3 interface
│   ├── client/
│   │   └── federated_client.py # FL client
│   ├── validator/
│   │   └── validator.py       # Update validator
│   ├── coordinator/
│   │   └── coordinator.py     # Round coordinator
│   ├── aggregator/
│   │   └── aggregator.py      # Model aggregator
│   ├── training/
│   │   └── lora_trainer.py    # LoRA trainer
│   ├── ipfs/
│   │   └── client.py          # IPFS interface
│   └── attacks/
│       └── malicious_client.py # Attack simulator
├── demo.py                     # Main demo script
├── hardhat.config.js
├── package.json
└── requirements.txt
```

## 🔬 How It Works

### Phase 1: Local Training
Each client fine-tunes a LoRA adapter on their private data:
```python
client.local_training(train_data)
```

### Phase 2: Upload to IPFS
Adapter is uploaded to decentralized storage:
```python
cid, hash = client.upload_to_ipfs(adapter_path)
```

### Phase 3: Blockchain Submission
Only metadata (CID + hash) goes on-chain:
```python
client.submit_to_blockchain(contract, cid, hash, private_key)
```

### Phase 4: Proof-of-Validation
Validators download, test, and vote:
```python
result = validator.validate_update(cid, hash, baseline_metrics)
validator.submit_vote(contract, update_id, result, private_key)
```

### Phase 5: Aggregation
Only accepted updates are aggregated:
```python
aggregator.aggregate_from_blockchain(contract, round_number)
```

## 🛡️ Security Features

### 1. Poisoning Detection
- **Accuracy Check**: Rejects updates with <70% accuracy
- **Divergence Check**: Rejects updates that diverge >50% from baseline
- **Backdoor Testing**: Tests for trigger-based malicious behavior

### 2. Trust System
- Accepted updates: +50 trust points
- Rejected updates: -100 trust points
- Trust affects aggregation weight

### 3. Blockchain Guarantees
- Immutable audit trail
- Transparent voting
- Tamper-proof history

## 🧪 Attack Simulation

The demo includes three attack types:

### Data Poisoning
```python
MaliciousClient(attack_type="data_poisoning")
```
Trains on corrupted data → Low accuracy → Rejected

### Model Poisoning
```python
MaliciousClient(attack_type="model_poisoning")
```
Submits reversed gradients → High divergence → Rejected

### Backdoor Attack
```python
MaliciousClient(attack_type="backdoor")
```
Embeds trigger phrase → Detected by validators → Rejected

## 📊 Smart Contract Interface

### Core Functions

```solidity
// Start new round
function startRound()

// Submit update
function submitUpdate(string ipfsCID, bytes32 fileHash)

// Register validators
function selectValidators(address[] validators)

// Submit validation vote
function submitVote(uint256 updateId, bool accept, uint256 accuracyScore, uint256 divergenceScore)

// Finalize round
function finalizeRound()

// Get accepted updates
function getAcceptedUpdates(uint256 round) returns (uint256[])

// Get trust score
function getTrustScore(address client) returns (TrustScore)
```

## 🔧 Configuration

### Smart Contract Thresholds

Edit `contracts/BlockLoRA.sol`:
```solidity
uint256 public constant MIN_ACCURACY = 700;      // 70%
uint256 public constant MAX_DIVERGENCE = 500;    // 50%
uint256 public constant MIN_VOTES_REQUIRED = 2;
uint256 public constant ACCEPTANCE_THRESHOLD = 51; // 51%
```

### LoRA Parameters

Edit `src/training/lora_trainer.py`:
```python
rank=8,        # Adapter size (higher = more capacity)
alpha=16,      # Scaling factor
target_modules=["c_attn", "c_proj"]  # Which layers to adapt
```

## 🌐 Production Deployment

### 1. Use Real IPFS Node

```bash
# Install IPFS
ipfs init
ipfs daemon
```

Update `src/ipfs/client.py`:
```python
IPFSClient(upload_url="http://127.0.0.1:5001/api/v0")
```

### 2. Deploy to Testnet

Update `hardhat.config.js`:
```javascript
networks: {
  sepolia: {
    url: "https://sepolia.infura.io/v3/YOUR_KEY",
    accounts: [PRIVATE_KEY]
  }
}
```

Deploy:
```bash
npx hardhat run scripts/deploy.js --network sepolia
```

### 3. Use Production LLM

Replace `gpt2` with:
- `meta-llama/Llama-2-7b-hf`
- `mistralai/Mistral-7B-v0.1`
- `tiiuae/falcon-7b`

Requires HuggingFace token for gated models.

## 📈 Metrics & Evaluation

### Model Metrics
- **Perplexity**: Lower is better (measures prediction quality)
- **Loss**: Training/validation loss
- **Divergence**: Relative change from baseline

### System Metrics
- **Acceptance Rate**: % of updates accepted
- **Trust Distribution**: Client reputation scores
- **Round Time**: Time per federated round

## 🐛 Troubleshooting

### "Failed to connect to blockchain"
- Ensure `npx hardhat node` is running
- Check port 8545 is not blocked

### "Contract not compiled"
```bash
npx hardhat compile
```

### "CUDA out of memory"
- Reduce batch size in training
- Use CPU: `device="cpu"`
- Use smaller model: `gpt2` instead of `gpt2-large`

### "IPFS upload failed"
- Demo works without IPFS (simulation mode)
- For real IPFS: `ipfs daemon`

## 📚 Research Paper Concepts

This implementation demonstrates:

1. **Federated Learning**: Decentralized training without data sharing
2. **LoRA (Low-Rank Adaptation)**: Parameter-efficient fine-tuning
3. **Proof-of-Validation**: Blockchain-based quality assurance
4. **Byzantine Fault Tolerance**: Resilience to malicious participants
5. **Trust-Weighted Aggregation**: Reputation-based model updates

## 🔮 Future Enhancements

- [ ] VRF-based validator selection (Chainlink VRF)
- [ ] Economic incentives (staking, rewards)
- [ ] Differential privacy (DP-SGD)
- [ ] Cross-chain support (Polygon, Arbitrum)
- [ ] Homomorphic encryption for weights
- [ ] Automated hyperparameter tuning
- [ ] Web dashboard for monitoring

## 📄 License

MIT License - See LICENSE file

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Add tests
4. Submit pull request

## 📧 Contact

For questions or issues, please open a GitHub issue.

---

**⚠️ Disclaimer**: This is a research prototype. Do not use in production without thorough security audit.
