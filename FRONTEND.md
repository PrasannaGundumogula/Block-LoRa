# Block-LoRA Web Frontend Guide

## Overview

The Block-LoRA web frontend provides an interactive, visually stunning interface for blockchain-enabled federated learning. Built with Streamlit, it offers real-time monitoring, configuration, and visualization capabilities.

## Features

### 🎨 Premium UI Design
- **Dark Mode**: Sleek dark theme with vibrant gradient accents
- **Glassmorphism**: Modern frosted glass effect on containers
- **Smooth Animations**: Polished transitions and hover effects
- **Responsive Layout**: Adapts to different screen sizes

### 🎛️ Interactive Controls
- **Sidebar Configuration**: Easy parameter adjustment
  - Blockchain settings (RPC URL, Chain ID)
  - Model selection (GPT-2, GPT-2-medium, DistilGPT-2)
  - LoRA hyperparameters (rank, alpha)
  - Attack scenarios (model/data poisoning, backdoor)
  - Validation thresholds
  
### 📊 Real-Time Monitoring
- **Live Progress Tracking**: Visual progress bars for long operations
- **Log Streaming**: Real-time logs from all system components
- **Status Indicators**: Connection status, deployment status
- **Phase Tracking**: Current execution phase display

### 📈 Advanced Visualization
- **Trust Score Charts**: Interactive bar charts showing client reputation
- **Acceptance Rate Analysis**: Stacked bar charts for update statistics
- **System Metrics Dashboard**: Key performance indicators
- **Round History**: Expandable timeline of completed rounds

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs Streamlit, Plotly, Pandas, and other frontend dependencies.

### 2. Start Blockchain

**Terminal 1:**
```bash
npx hardhat node
```

Keep this running throughout your session.

### 3. Launch Web Frontend

**Terminal 2:**
```bash
streamlit run app.py
```

The app will open in your browser at http://localhost:8501

## User Guide

### Step 1: System Setup

1. Navigate to the **Setup** tab
2. Ensure the RPC URL matches your Hardhat node (default: http://127.0.0.1:8545)
3. Click **"🚀 Initialize System"**
4. Wait for contract deployment (takes ~5 seconds)
5. You'll see success confirmation with contract address

### Step 2: Create Participants

1. Navigate to the **Participants** tab
2. Configure participants in the sidebar:
   - Honest clients (default: 3)
   - Malicious clients (default: 1)
   - Attack type (model_poisoning, data_poisoning, or backdoor)
   - Validators (default: 3)
3. Click **"👥 Create Participants"**
4. Wait for initialization (takes ~10 seconds)

### Step 3: Execute Federated Learning Round

1. Navigate to the **Training Rounds** tab
2. Select round number (auto-increments)
3. Click **"▶️ Execute Round"**
4. Watch the progress bar through 4 phases:
   - Phase 1: Client training
   - Phase 2: Validator evaluation
   - Phase 3: Round finalization
   - Phase 4: Update aggregation
5. Total time: 2-5 minutes depending on your CPU

### Step 4: View Analytics

1. Navigate to the **Analytics** tab
2. Explore:
   - **Trust Score Distribution**: See which clients are trustworthy
   - **Update Acceptance Rate**: Visualize accepted vs rejected updates
   - **System Metrics**: Overall statistics

### Step 5: Monitor Activity

1. Check the **Dashboard** tab for system overview
2. View **Recent Activity** log for latest events
3. Monitor trust scores and round statistics

## Architecture

### Frontend Components

#### `app.py`
Main Streamlit application with:
- Multi-tab interface (Dashboard, Setup, Participants, Training Rounds, Analytics)
- Custom CSS styling for premium dark theme
- Session state management for persistent workflow
- Real-time visualization with Plotly

#### `src/api/orchestrator.py`
Service layer providing:
- `BlockLoRAOrchestrator` class: Backend API for frontend
- Log capture and streaming
- Progress tracking
- Clean separation between UI and business logic

### Data Flow

```
User Interaction (Streamlit UI)
        ↓
Session State Management
        ↓
BlockLoRAOrchestrator API
        ↓
Original Block-LoRA Components
        ↓
Blockchain / IPFS / ML Training
```

## Customization

### Changing Colors

Edit the CSS in `app.py`:

```css
:root {
    --primary-color: #6366f1;      /* Change to your brand color */
    --secondary-color: #8b5cf6;    /* Secondary accent */
    --success-color: #10b981;      /* Success indicators */
}
```

### Adding New Metrics

Add to the Analytics tab:

```python
# In the Analytics tab
st.metric("Your Metric", value, delta=change)
```

### Custom Visualizations

Use Plotly for interactive charts:

```python
import plotly.graph_objects as go

fig = go.Figure(data=[...])
fig.update_layout(template="plotly_dark", ...)
st.plotly_chart(fig, use_container_width=True)
```

## Troubleshooting

### "Connection refused" error

**Problem:** Hardhat node not running

**Solution:**
```bash
# Terminal 1
npx hardhat node
```

### Streamlit not found

**Problem:** Frontend dependencies not installed

**Solution:**
```bash
pip install streamlit plotly pandas
```

### Page doesn't update

**Problem:** Session state not refreshing

**Solution:** Click the Streamlit "Rerun" button or use `st.rerun()` in code

### Visualization not showing

**Problem:** No data available yet

**Solution:** Execute at least one complete round first

### Slow performance

**Optimization tips:**
- Reduce number of clients/validators in sidebar
- Use smaller base model (distilgpt2)
- Decrease LoRA rank in sidebar settings

## Advanced Features

### Background Task Execution

The orchestrator runs long operations in the background while updating the UI:

```python
# Example: Execute round asynchronously
with st.spinner("Executing round..."):
    result = st.session_state.orchestrator.execute_round(round_num)
    if result['success']:
        st.success("Round complete!")
```

### Live Log Streaming

Logs are captured and displayed in real-time:

```python
logs = st.session_state.orchestrator.get_logs(n=50)
for log in logs:
    st.markdown(f"{log['timestamp']} {log['message']}")
```

### State Persistence

Streamlit session state maintains workflow state:

```python
if 'setup_complete' not in st.session_state:
    st.session_state.setup_complete = False

# Later...
st.session_state.setup_complete = True
```

## Comparison: CLI vs Web Frontend

| Feature | `demo.py` (CLI) | `app.py` (Web) |
|---------|----------------|----------------|
| Interface | Terminal | Browser |
| Interaction | Non-interactive | Fully interactive |
| Configuration | Code editing | UI controls |
| Monitoring | Text logs | Live dashboards |
| Visualization | None | Charts & graphs |
| Accessibility | Developers only | Anyone |
| User Experience | Basic | Premium |

## Production Deployment

For production use:

### 1. Configure Authentication

Add Streamlit authentication:

```python
# Add at top of app.py
import streamlit_authenticator as stauth

authenticator = stauth.Authenticate(...)
authenticator.login('Login', 'main')
```

### 2. Deploy to Cloud

**Streamlit Cloud:**
```bash
# Push to GitHub
git push origin main

# Visit share.streamlit.io
# Connect repository
```

**Docker:**
```dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

### 3. Use Production Blockchain

Update RPC URL in sidebar to:
- Sepolia testnet
- Polygon Mumbai
- Ethereum mainnet

### 4. Enable IPFS

Run local IPFS node:
```bash
ipfs daemon
```

The orchestrator will automatically detect and use it.

## Tips & Tricks

### Keyboard Shortcuts
- `R` - Rerun app
- `C` - Clear cache
- `Ctrl+Shift+R` - Hard refresh

### Performance
- Use smaller models for faster rounds
- Reduce number of participants for testing
- Monitor system resources in Task Manager

### Debugging
- Check browser console for errors (F12)
- View Streamlit logs in terminal
- Use `st.write()` for debug output

## Next Steps

1. **Experiment**: Try different attack types and thresholds
2. **Extend**: Add custom validation logic or aggregation strategies
3. **Deploy**: Share with team on Streamlit Cloud
4. **Research**: Use for academic experiments and publications

## Support

For issues or questions:
1. Check this guide
2. Review error messages in logs
3. Verify Hardhat node is running
4. Check `demo.py` CLI version works

---

**Enjoy your blockchain-powered federated learning experience!** 🚀
