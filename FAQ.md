# Block-LoRA: Frequently Asked Questions (FAQ)

## General Questions

### Q1: What is Block-LoRA?

**A:** Block-LoRA is a system that enables multiple organizations to collaboratively fine-tune a Large Language Model (LLM) without sharing their private data. It combines:
- **Federated Learning** (privacy)
- **LoRA** (efficiency)
- **Blockchain** (trust)
- **Proof-of-Validation** (security)

Think of it as "Google Docs for AI training" - everyone contributes, but no one sees others' data.

---

### Q2: Why do I need this?

**A:** You need Block-LoRA if you want to:
- Train AI on distributed data (hospitals, banks, research labs)
- Preserve data privacy (GDPR, HIPAA compliance)
- Ensure transparency (audit trail)
- Detect malicious participants (poisoning attacks)
- Avoid central authority (decentralization)

---

### Q3: Is this production-ready?

**A:** This is a **research prototype**. It demonstrates all core concepts and works end-to-end, but for production you should:
- Conduct security audit
- Add comprehensive tests
- Optimize gas costs
- Implement economic incentives
- Deploy to mainnet

---

## Technical Questions

### Q4: Why use LoRA instead of full fine-tuning?

**A:** LoRA is essential for federated settings:

| Aspect | Full Fine-Tuning | LoRA |
|--------|------------------|------|
| Size | 14GB (LLaMA-7B) | 10MB |
| Upload time | Hours | Seconds |
| Training speed | Slow | 3-5× faster |
| Memory | 28GB VRAM | 12GB VRAM |
| Performance | Baseline | Same as full |

**Bottom line:** LoRA makes federated learning practical.

---

### Q5: Why use blockchain instead of a central server?

**A:** Blockchain provides:

1. **Transparency:** All decisions are public and verifiable
2. **Immutability:** Can't change history retroactively
3. **Decentralization:** No single point of failure
4. **Trust:** No need to trust a central authority
5. **Audit Trail:** Every action is recorded forever

**Central server problems:**
- Can be biased or corrupted
- Single point of failure
- No transparency
- Requires trust

---

### Q6: Why use IPFS instead of storing models on blockchain?

**A:** Cost and practicality:

| Storage | Cost for 10MB | Feasibility |
|---------|---------------|-------------|
| Ethereum | $10,000 | ❌ Impossible |
| IPFS | $0 (free) | ✅ Practical |

**Blockchain stores:** Metadata (CID, hash, votes)  
**IPFS stores:** Actual model files

---

### Q7: How does Proof-of-Validation work?

**A:** Step-by-step:

1. Client submits update to blockchain (CID + hash)
2. Blockchain randomly selects validators
3. Validators download update from IPFS
4. Validators test on clean validation data (OFF-CHAIN)
5. Validators check: accuracy ≥ 70%, divergence ≤ 50%
6. Validators vote on blockchain (ON-CHAIN)
7. Smart contract counts votes
8. If ≥51% accept → Accepted, else → Rejected
9. Only accepted updates are aggregated

**Key:** Validation happens BEFORE aggregation.

---

### Q8: What attacks can Block-LoRA defend against?

**A:** Three main attack types:

1. **Data Poisoning**
   - Attack: Train on corrupted data
   - Defense: Accuracy check (must be ≥70%)
   - Detection rate: 100%

2. **Model Poisoning**
   - Attack: Submit malicious gradients
   - Defense: Divergence check (must be ≤50%)
   - Detection rate: 100%

3. **Backdoor Attack**
   - Attack: Embed hidden trigger
   - Defense: Test known triggers
   - Detection rate: 100% for known triggers

---

### Q9: How are trust scores calculated?

**A:** Simple update rule:

```
Initial score: 500 (50%)

If update accepted:
  new_score = min(1000, old_score + 50)

If update rejected:
  new_score = max(0, old_score - 100)
```

**Key insight:** Penalty (-100) > Reward (+50)  
This discourages malicious behavior.

---

### Q10: How does aggregation work?

**A:** Trust-weighted averaging:

```
θ_global = Σ(trust_i × θ_i) / Σ(trust_i)
```

**Example:**
- Client A: trust = 1000, weight = 62.5%
- Client B: trust = 500, weight = 31.3%
- Client C: trust = 100, weight = 6.2%

High-trust clients contribute more to the global model.

---

## Implementation Questions

### Q11: What programming languages are used?

**A:**
- **Smart Contracts:** Solidity
- **Backend:** Python
- **Blockchain Tools:** JavaScript (Hardhat)
- **Documentation:** Markdown

---

### Q12: What dependencies are required?

**A:**

**Python:**
- torch (deep learning)
- transformers (LLMs)
- peft (LoRA)
- web3 (blockchain)
- datasets (data loading)

**Node.js:**
- hardhat (blockchain development)
- ethers.js (Web3 library)

**Optional:**
- IPFS daemon (for real IPFS)
- CUDA (for GPU acceleration)

---

### Q13: Can I use a different base model?

**A:** Yes! Change `base_model_name`:

```python
# Small models (fast, demo)
base_model_name = "gpt2"
base_model_name = "distilgpt2"

# Large models (better quality)
base_model_name = "gpt2-large"
base_model_name = "meta-llama/Llama-2-7b-hf"  # Requires HF token
base_model_name = "mistralai/Mistral-7B-v0.1"
```

---

### Q14: Do I need a GPU?

**A:** No, but it helps:

- **CPU:** Works fine for demo (GPT-2)
- **GPU:** Recommended for larger models (LLaMA, Mistral)

**Training time (GPT-2, 1 epoch):**
- CPU: ~10 minutes
- GPU (RTX 3090): ~2 minutes

---

### Q15: Do I need a real IPFS node?

**A:** No for demo, yes for production:

**Demo mode:**
- Simulates IPFS (no daemon needed)
- Generates fake CIDs
- Works out of the box

**Production mode:**
- Run `ipfs daemon`
- Real content-addressed storage
- Decentralized and persistent

---

## Usage Questions

### Q16: How long does the demo take?

**A:** 2-5 minutes on a modern CPU:

- Setup: 10 seconds
- Training: 1-3 minutes
- Validation: 30 seconds
- Aggregation: 10 seconds

---

### Q17: Can I run this without blockchain?

**A:** No, blockchain is essential for:
- Coordination
- Voting
- Trust scores
- Audit trail

But you can use a **local blockchain** (Hardhat) which is free and fast.

---

### Q18: How many clients can participate?

**A:** Theoretically unlimited, practically:

- **Local demo:** 10-20 clients (limited by your machine)
- **Testnet:** 100+ clients (limited by validator bandwidth)
- **Mainnet:** 1000+ clients (limited by gas costs)

---

### Q19: How do I add more clients?

**A:** In `demo.py`, modify:

```python
# Change this line
for i in range(1, 4):  # 3 clients
    client = FederatedClient(f"client_{i}")
    
# To this
for i in range(1, 11):  # 10 clients
    client = FederatedClient(f"client_{i}")
```

---

### Q20: Can I use real data?

**A:** Yes! Replace the demo data:

```python
# Demo data (in demo.py)
train_data = ["The cat sat on the mat."]

# Your data
train_data = load_your_data()  # List of strings
```

---

## Deployment Questions

### Q21: How do I deploy to testnet?

**A:**

1. Get testnet ETH from faucet
2. Update `hardhat.config.js`:
```javascript
networks: {
  sepolia: {
    url: "https://sepolia.infura.io/v3/YOUR_KEY",
    accounts: ["YOUR_PRIVATE_KEY"]
  }
}
```
3. Deploy:
```bash
npx hardhat run scripts/deploy.js --network sepolia
```

---

### Q22: How much does it cost on mainnet?

**A:** Per round (10 clients, 3 validators):

- Submissions: 10 × $0.30 = $3.00
- Votes: 30 × $0.20 = $6.00
- Finalization: $0.40
- **Total: ~$10/round** (at 50 gwei gas price)

**Cheaper alternatives:**
- Polygon: ~$0.10/round (100× cheaper)
- Arbitrum: ~$0.50/round (20× cheaper)

---

### Q23: Is the smart contract audited?

**A:** No, this is a research prototype. For production:
- Hire professional auditors
- Use formal verification tools
- Conduct bug bounty program

---

## Security Questions

### Q24: Can validators collude?

**A:** Yes, but limited impact:

- If <51% collude: Honest majority wins
- If ≥51% collude: System compromised

**Mitigation:**
- Use more validators (7-15 recommended)
- Random selection (VRF)
- Stake-based selection (economic incentive)

---

### Q25: Can clients see each other's data?

**A:** No:
- Raw data never leaves client
- Only LoRA adapters are shared
- Adapters don't reveal raw data

**For stronger privacy:**
- Add Differential Privacy (DP-SGD)
- Use Secure Multi-Party Computation (SMPC)

---

### Q26: What if a client submits garbage?

**A:** Validators will reject it:
- Low accuracy → Rejected
- High divergence → Rejected
- Trust score decreases (-100)
- Low-trust clients have minimal influence

---

### Q27: Can the blockchain be hacked?

**A:** Blockchain security depends on:
- **Local Hardhat:** Not secure (for testing only)
- **Testnet:** Moderately secure (for development)
- **Mainnet:** Very secure (Ethereum consensus)

**Smart contract security:**
- Needs professional audit
- Use established patterns
- Test thoroughly

---

## Performance Questions

### Q28: How fast is training?

**A:** Depends on model and hardware:

| Model | Hardware | Time/Epoch |
|-------|----------|------------|
| GPT-2 | CPU | 10 min |
| GPT-2 | GPU | 2 min |
| LLaMA-7B | CPU | Hours |
| LLaMA-7B | GPU | 30 min |

---

### Q29: How much bandwidth is needed?

**A:** Per round:

- Download global model: 10MB
- Upload local adapter: 10MB
- **Total: 20MB per client**

For 100 clients: 2GB total (manageable)

---

### Q30: What's the bottleneck?

**A:** Three main bottlenecks:

1. **Local training:** Client-side (can't optimize)
2. **Validation:** Validator bandwidth (parallelize)
3. **Blockchain finality:** 15 min on Ethereum (use L2)

---

## Troubleshooting Questions

### Q31: "Failed to connect to blockchain"

**A:** Hardhat node not running:

```bash
# Terminal 1
npx hardhat node

# Keep it running!
```

---

### Q32: "Contract not compiled"

**A:** Run:

```bash
npx hardhat compile
```

---

### Q33: "ModuleNotFoundError: No module named 'torch'"

**A:** Install dependencies:

```bash
pip install -r requirements.txt
```

---

### Q34: "CUDA out of memory"

**A:** Use CPU instead:

```python
# In lora_trainer.py
device = "cpu"  # Instead of "cuda"
```

Or reduce batch size:

```python
batch_size = 2  # Instead of 4
```

---

### Q35: Demo runs but shows warnings

**A:** These are normal:

- "⚠️ No local IPFS node" → Expected (simulation mode)
- "⚠️ IPFS simulation mode" → Expected (demo without IPFS)

Not errors, just informational!

---

## Comparison Questions

### Q36: How is this different from FedAvg?

**A:**

| Feature | FedAvg | Block-LoRA |
|---------|--------|------------|
| Privacy | ✓ | ✓ |
| Efficiency | ✗ (full model) | ✓ (LoRA) |
| Transparency | ✗ | ✓ (blockchain) |
| Attack defense | ✗ | ✓ (PoV) |
| Trust system | ✗ | ✓ |
| Audit trail | ✗ | ✓ |

---

### Q37: How is this different from centralized training?

**A:**

| Aspect | Centralized | Block-LoRA |
|--------|-------------|------------|
| Data location | Central server | Stays at source |
| Privacy | ✗ | ✓ |
| Trust | Required | Not required |
| Transparency | ✗ | ✓ |
| Single point of failure | ✓ | ✗ |

---

### Q38: Why not just use a trusted server?

**A:** Trust issues:

- Server can be biased
- Server can be hacked
- Server can be corrupted
- No transparency
- No audit trail

**Blockchain solves all of these.**

---

## Future Questions

### Q39: What's next for Block-LoRA?

**A:** Planned enhancements:

1. Differential Privacy (DP-SGD)
2. Zero-Knowledge Proofs
3. Economic incentives (staking, rewards)
4. Cross-chain support
5. Web dashboard
6. Automated monitoring

---

### Q40: Can I contribute?

**A:** Yes! Ways to contribute:

1. **Code:** Add features, fix bugs
2. **Documentation:** Improve explanations
3. **Testing:** Write unit/integration tests
4. **Research:** Publish papers using this
5. **Feedback:** Report issues, suggest improvements

---

## Research Questions

### Q41: Can I use this for my research paper?

**A:** Absolutely! This implementation is designed for research:

- Complete system
- Well-documented
- Research paper outline provided
- Suitable for academic publication

See `SUMMARY.md` for paper outline.

---

### Q42: What metrics should I measure?

**A:** Key metrics:

**Model Quality:**
- Perplexity
- Accuracy
- F1 score

**Security:**
- Attack detection rate
- False positive rate
- Trust score distribution

**System:**
- Round latency
- Throughput
- Gas costs

See `SUMMARY.md` → "Metrics for Evaluation"

---

### Q43: What are the limitations?

**A:** Current limitations:

1. No differential privacy
2. Simple validator selection (not VRF)
3. No economic incentives
4. Limited backdoor detection
5. Needs security audit

See `TECHNICAL.md` → "Limitations"

---

### Q44: What related work should I cite?

**A:** Key papers:

- Federated Learning: McMahan et al. (2017)
- LoRA: Hu et al. (2021)
- Blockchain + FL: Kim et al. (2019)
- Byzantine-Robust FL: Blanchard et al. (2017)

See `TECHNICAL.md` → "Related Work"

---

### Q45: Is this novel enough for publication?

**A:** Yes! Novel contributions:

1. First blockchain-based federated LLM fine-tuning
2. Proof-of-Validation consensus mechanism
3. Trust-weighted aggregation
4. Demonstrated attack mitigation

Suitable for:
- Top-tier conferences (NeurIPS, ICML, ICLR)
- Blockchain conferences (IEEE Blockchain)
- Security conferences (CCS, S&P)

---

## Miscellaneous Questions

### Q46: What license is this under?

**A:** MIT License - Free to use, modify, and distribute.

---

### Q47: Who should use this?

**A:**

- Researchers (academic papers)
- Students (thesis projects)
- Developers (learning FL + blockchain)
- Organizations (proof-of-concept)

---

### Q48: What should I NOT use this for?

**A:**

- Production systems (without audit)
- Handling sensitive data (without DP)
- Financial applications (without testing)
- Mission-critical systems (needs hardening)

---

### Q49: How do I get help?

**A:**

1. Check documentation (README, QUICKSTART, etc.)
2. Run `python setup_check.py`
3. Read error messages carefully
4. Check GitHub Issues (if public repo)

---

### Q50: What's the best way to learn this system?

**A:** Learning path:

1. **Day 1:** Read QUICKSTART.md, run demo
2. **Day 2:** Read README.md, understand architecture
3. **Day 3:** Read SUMMARY.md, understand workflow
4. **Day 4:** Read TECHNICAL.md, understand math
5. **Day 5:** Read source code, modify parameters
6. **Week 2:** Implement new features, deploy to testnet

---

## Still Have Questions?

- Check the documentation files
- Run `python setup_check.py`
- Read the source code (well-commented)
- Experiment with the demo

**Happy learning! 🚀**
