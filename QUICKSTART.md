# Block-LoRA Quick Start Guide

Get Block-LoRA running in 5 minutes!

## Prerequisites

- Python 3.10+
- Node.js 16+
- 8GB RAM minimum
- Internet connection

## Installation (5 steps)

### Step 1: Install Python Dependencies

```bash
Activate venv

pip install -r requirements.txt
```

### Step 2: Install Node.js Dependencies

```bash
npm install
```

This installs Hardhat and related tools.

### Step 3: Compile Smart Contract

```bash
npx hardhat compile
```

You should see: "Compiled 1 Solidity file successfully"

### Step 4: Start Local Blockchain

**Open Terminal 1:**
```bash
npx hardhat node
```

Keep this running! You'll see 20 accounts with addresses and private keys.

### Step 5: Run Demo

**Open Terminal 2:**
```bash
streamlit run app.py
```

## What to Expect

The demo will:

1. **Connect to blockchain** (local Hardhat network)
2. **Deploy smart contract** (~5 seconds)
3. **Create participants** (3 honest clients, 1 malicious, 3 validators)
4. **Execute Round 1:**
   - Clients train LoRA adapters
   - Submit to blockchain
   - Validators evaluate
   - Vote on-chain
   - Malicious update rejected ✓
5. **Aggregate** accepted updates
6. **Show results** (trust scores, metrics)

**Total time:** 2-5 minutes (depending on CPU)

## Expected Output

```
======================================================================
  BLOCK-LORA: Blockchain-Enabled Federated Fine-Tuning
======================================================================

======================================================================
  PHASE 1: System Setup
======================================================================

1. Connecting to blockchain...
✓ Connected to blockchain (Chain ID: 1337)

2. Deploying smart contract...
Deploying contract... (tx: 0x...)
✓ Contract deployed at: 0x5FbDB2315678afecb367f032d93F642f64180aa3

3. Initializing coordinator...
✓ Coordinator initialized (admin: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266)

======================================================================
  PHASE 2: Participant Setup
======================================================================

Creating honest clients...
✓ Client client_1 initialized
✓ Client client_2 initialized
✓ Client client_3 initialized

Creating malicious client...
⚠️  MALICIOUS CLIENT: model_poisoning
✓ Client malicious_client initialized

Creating validators...
✓ Validator validator_1 initialized
✓ Validator validator_2 initialized
✓ Validator validator_3 initialized

======================================================================
  PHASE 3: Federated Learning Round 1
======================================================================

Starting round 1...
✓ Round 1 started (tx: 0x...)

--- Client Training Phase ---

[Training logs...]

--- Validator Selection Phase ---
✓ Validators selected: [0x70997970C5..., 0x3C44CdDdB6..., 0x90F79bf6EB...]

--- Validation Phase ---

Validating 4 updates...

--- Validating Update 1 ---
Client: 0x70997970C5...
Validator validator_1 evaluating...
  ✓ ACCEPTED: Passed all checks

[More validation logs...]

--- Validating Update 4 (Malicious) ---
Client: 0x15d34AAf54...
Validator validator_1 evaluating...
  ❌ REJECTED: Low accuracy or high divergence

--- Round Finalization Phase ---

✓ Round 1 Complete:
  Accepted: 3
  Rejected: 1

--- Trust Scores ---
HONEST     0x70997970C5... Score: 550/1000 (Accepted: 1, Rejected: 0)
HONEST     0x3C44CdDdB6... Score: 550/1000 (Accepted: 1, Rejected: 0)
HONEST     0x90F79bf6EB... Score: 550/1000 (Accepted: 1, Rejected: 0)
MALICIOUS  0x15d34AAf54... Score: 400/1000 (Accepted: 0, Rejected: 1)

======================================================================
  PHASE 4: Secure Aggregation
======================================================================

Aggregating accepted updates...
✓ Aggregation complete

======================================================================
  PHASE 5: Summary & Analysis
======================================================================

✓ DEMONSTRATION COMPLETE

Key Achievements:
  1. ✓ Federated learning round executed
  2. ✓ Malicious update detected and rejected
  3. ✓ Trust scores updated (malicious client penalized)
  4. ✓ Only honest updates aggregated
  5. ✓ Blockchain provides immutable audit trail
```

## Troubleshooting

### "Failed to connect to blockchain"

**Problem:** Hardhat node not running

**Solution:**
```bash
# Terminal 1
npx hardhat node
```

### "Contract not compiled"

**Problem:** Smart contract not compiled

**Solution:**
```bash
npx hardhat compile
```

### "ModuleNotFoundError: No module named 'torch'"

**Problem:** Python packages not installed

**Solution:**
```bash
pip install -r requirements.txt
```

### "CUDA out of memory"

**Problem:** GPU memory insufficient

**Solution:** Demo uses CPU by default (no GPU needed)

If you modified code to use GPU:
```python
# In lora_trainer.py, change:
device="cpu"  # Instead of "cuda"
```

### Demo runs but shows warnings

**Normal warnings:**
- "⚠️ No local IPFS node detected" - Expected, demo works without IPFS
- "⚠️ IPFS simulation mode" - Expected, using simulated IPFS

**These are intentional for demo purposes!**

## Verify Installation

Run the setup checker:

```bash
python setup_check.py
```

This checks all dependencies and shows what's missing.

## Next Steps

### 1. Explore the Code

**Start with:**
- `demo.py` - Main orchestration
- `contracts/BlockLoRA.sol` - Smart contract
- `src/client/federated_client.py` - Client logic
- `src/validator/validator.py` - Validation logic

### 2. Modify Parameters

**Try different attacks:**
```python
# In demo.py, line ~50
malicious_client = MaliciousClient(
    "malicious_client",
    attack_type="backdoor",  # Try: data_poisoning, model_poisoning, backdoor
    base_model_name="gpt2"
)
```

**Adjust thresholds:**
```solidity
// In contracts/BlockLoRA.sol
uint256 public constant MIN_ACCURACY = 700;      // Change to 800 (stricter)
uint256 public constant MAX_DIVERGENCE = 500;    // Change to 300 (stricter)
```

Then recompile:
```bash
npx hardhat compile
python demo.py
```

### 3. Add More Clients

```python
# In demo.py, modify line ~40
for i in range(1, 10):  # Change 4 to 10 for more clients
    client = FederatedClient(f"client_{i}", base_model_name="gpt2")
    honest_clients.append((client, accounts[i]))
```

### 4. Use Real IPFS

**Install IPFS:**
```bash
# Download from https://ipfs.io
ipfs init
ipfs daemon
```

**Update code:**
```python
# src/ipfs/client.py will auto-detect running IPFS node
```

### 5. Deploy to Testnet

**Get testnet ETH:**
- Sepolia: https://sepoliafaucet.com
- Mumbai: https://faucet.polygon.technology

**Update hardhat.config.js:**
```javascript
networks: {
  sepolia: {
    url: "https://sepolia.infura.io/v3/YOUR_INFURA_KEY",
    accounts: ["YOUR_PRIVATE_KEY"]
  }
}
```

**Deploy:**
```bash
npx hardhat run scripts/deploy.js --network sepolia
```

## Understanding the Output

### Trust Scores

```
HONEST     0x7099... Score: 550/1000 (Accepted: 1, Rejected: 0)
MALICIOUS  0x15d3... Score: 400/1000 (Accepted: 0, Rejected: 1)
```

- **Initial:** 500
- **Accepted:** +50
- **Rejected:** -100
- **Range:** 0-1000

### Update Status

- **Pending:** Waiting for votes
- **Accepted:** ≥51% validators approved
- **Rejected:** <51% validators approved

### Validation Scores

- **Accuracy:** 0-1000 (700+ required)
- **Divergence:** 0-1000 (500- required)

## Common Questions

### Q: Do I need a GPU?

**A:** No! Demo uses CPU by default. GPU speeds up training but isn't required.

### Q: Do I need real IPFS?

**A:** No! Demo simulates IPFS. For production, use real IPFS.

### Q: How long does demo take?

**A:** 2-5 minutes on modern CPU.

### Q: Can I use a different model?

**A:** Yes! Change `base_model_name="gpt2"` to:
- `"gpt2-medium"` (larger)
- `"distilgpt2"` (smaller, faster)
- `"meta-llama/Llama-2-7b-hf"` (requires HF token)

### Q: Is this production-ready?

**A:** No, this is a research prototype. For production:
- Add security audit
- Use real IPFS
- Deploy to mainnet
- Add economic incentives
- Implement VRF validator selection

### Q: Where's the data stored?

**A:** 
- **Training data:** Never leaves client (private)
- **LoRA adapters:** IPFS (simulated in demo)
- **Metadata:** Blockchain (local Hardhat network)

### Q: Can I see the blockchain state?

**A:** Yes! While Hardhat node is running, you can:

```bash
# In another terminal
npx hardhat console --network localhost
```

Then:
```javascript
const contract = await ethers.getContractAt("BlockLoRA", "CONTRACT_ADDRESS");
await contract.currentRound();
await contract.updateCounter();
```

## Resources

- **README.md** - Full documentation
- **TECHNICAL.md** - Deep technical details
- **SUMMARY.md** - System overview
- **demo.py** - Annotated demo code
- **contracts/BlockLoRA.sol** - Smart contract with comments

## Getting Help

1. Check troubleshooting section above
2. Run `python setup_check.py`
3. Read error messages carefully
4. Check that Hardhat node is running
5. Verify all dependencies installed

## Success Criteria

You've successfully run Block-LoRA if you see:

✓ Contract deployed
✓ Clients trained
✓ Validators voted
✓ Malicious update rejected
✓ Trust scores updated
✓ "DEMONSTRATION COMPLETE"

**Congratulations! You've run a complete blockchain-enabled federated learning system!** 🎉

---

**Ready to dive deeper?** Read TECHNICAL.md for mathematical foundations and security analysis.
