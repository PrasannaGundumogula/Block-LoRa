"""
Block-LoRA Web Frontend - Enhanced Version
Premium Streamlit interface with rich visuals and clear explanations
"""
import streamlit as st
import sys
from pathlib import Path
import time
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.api.orchestrator import BlockLoRAOrchestrator

# Page configuration
st.set_page_config(
    page_title="Block-LoRA: Blockchain Federated Learning",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with vibrant colors and better differentiation
st.markdown("""
<style>
    /* Enhanced Color Scheme */
    :root {
        --primary-blue: #3b82f6;
        --primary-purple: #8b5cf6;
        --success-green: #10b981;
        --warning-amber: #f59e0b;
        --error-red: #ef4444;
        --info-cyan: #06b6d4;
        --bg-dark: #0a0e1a;
        --bg-card: #1a1f35;
        --text-bright: #f8fafc;
        --text-muted: #94a3b8;
    }
    
    /* Main background with enhanced gradient */
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #1a1f35 50%, #0f1629 100%);
    }
    
    /* Headers with vibrant gradients */
    h1 {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        color: #f8fafc !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        margin-top: 2rem !important;
    }
    
    h3 {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
    }
    
    /* Enhanced metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        font-weight: 600;
        color: #cbd5e1;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Premium buttons with glow effect */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2.5rem;
        font-weight: 700;
        font-size: 1.1rem;
        transition: all 0.4s ease;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(139, 92, 246, 0.6);
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
    }
    
    /* Enhanced alert boxes with icons and borders */
    .element-container .stSuccess {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.1) 100%);
        border-left: 6px solid #10b981;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);
    }
    
    .element-container .stWarning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(217, 119, 6, 0.1) 100%);
        border-left: 6px solid #f59e0b;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.2);
    }
    
    .element-container .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.1) 100%);
        border-left: 6px solid #ef4444;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2);
    }
    
    .element-container .stInfo {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.15) 0%, rgba(8, 145, 178, 0.1) 100%);
        border-left: 6px solid #06b6d4;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(6, 182, 212, 0.2);
    }
    
    /* Enhanced tabs with better differentiation */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.4) 100%);
        border-radius: 16px;
        padding: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        color: #94a3b8;
        font-weight: 700;
        font-size: 1.05rem;
        padding: 14px 28px;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    /* Sidebar with enhanced styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f35 0%, #0a0e1a 100%);
        border-right: 2px solid rgba(59, 130, 246, 0.3);
    }
    
    /* Enhanced expanders */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border-radius: 12px;
        color: #f8fafc;
        font-weight: 700;
        padding: 1rem;
        border: 1px solid rgba(59, 130, 246, 0.2);
    }
    
    /* Glowing progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%);
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.6);
    }
    
    /* Custom info cards */
    .info-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.05) 100%);
        border-radius: 16px;
        padding: 1.5rem;
        border: 2px solid rgba(59, 130, 246, 0.2);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        margin: 1rem 0;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1.2rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
        margin: 0.25rem;
    }
    
    .badge-success {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }
    
    .badge-warning {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
    }
    
    .badge-error {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
    }
    
    .badge-info {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
    }
    
    /* Animated icons */
    @keyframes pulse-glow {
        0%, 100% { 
            opacity: 1; 
            filter: drop-shadow(0 0 8px rgba(59, 130, 246, 0.8));
        }
        50% { 
            opacity: 0.7; 
            filter: drop-shadow(0 0 20px rgba(139, 92, 246, 1));
        }
    }
    
    .pulse-icon {
        animation: pulse-glow 2s ease-in-out infinite;
    }
    
    /* Enhanced dataframe */
    .dataframe {
        border-radius: 12px;
        border: 2px solid rgba(59, 130, 246, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = BlockLoRAOrchestrator()

if 'setup_complete' not in st.session_state:
    st.session_state.setup_complete = False

if 'participants_created' not in st.session_state:
    st.session_state.participants_created = False

if 'rounds_executed' not in st.session_state:
    st.session_state.rounds_executed = []

# Sidebar configuration with clearer labels
with st.sidebar:
    st.title("⚙️ System Configuration")
    st.markdown("---")
    
    # Blockchain settings
    with st.expander("🔗 Blockchain Connection", expanded=True):
        st.markdown("**Connect to your local blockchain**")
        rpc_url = st.text_input("RPC URL", value="http://127.0.0.1:8545")
        st.info("💡 **Tip:** Start Hardhat node first:\n```bash\nnpx hardhat node\n```")
    
    # Model settings
    with st.expander("🤖 AI Model Configuration", expanded=False):
        st.markdown("**Choose the base language model**")
        base_model = st.selectbox(
            "Base Model",
            ["gpt2", "gpt2-medium", "distilgpt2"],
            help="GPT-2 variants with different sizes"
        )
        st.markdown("**📊 LoRA Adapter Settings**")
        st.caption("LoRA (Low-Rank Adaptation) reduces training parameters")
        lora_rank = st.slider("Rank", 2, 16, 8, help="Higher = more capacity, slower training")
        lora_alpha = st.slider("Alpha", 2, 32, 16, help="Scaling factor for LoRA updates")
    
    # Simulation settings with explanations
    with st.expander("👥 Participant Configuration", expanded=False):
        st.markdown("**Define your federated learning network**")
        st.caption("💡 Network capacity: Up to 19 total participants (Hardhat provides 20 accounts: 1 admin + 19 for network)")
        
        num_honest = st.number_input("✅ Honest Clients", 1, 19, 3, help="Clients submitting valid model updates")
        num_malicious = st.number_input("⚠️ Malicious Clients", 0, 19, 1, help="Attackers trying to poison the system")
        
        if num_malicious > 0:
            attack_type = st.selectbox(
                "Attack Strategy",
                ["model_poisoning", "data_poisoning", "backdoor"],
                help="Type of attack malicious clients will attempt"
            )
            st.warning(f"🛡️ System will detect and reject {attack_type} attacks")
        else:
            attack_type = "model_poisoning"
        
        num_validators = st.number_input("👮 Validators", 1, 19, 3, help="Nodes that verify update quality")
        
        # Show network size warning
        total_participants = num_honest + num_malicious + num_validators
        if total_participants > 19:
            st.error(f"❌ Total participants ({total_participants}) exceeds capacity (19 max)")
        elif total_participants > 12:
            st.warning(f"⚠️ Large network ({total_participants} participants) - may be slower")
        else:
            st.success(f"✅ Network size: {total_participants} participants")
    
    # Validation thresholds
    with st.expander("📊 Quality Control Thresholds", expanded=False):
        st.markdown("**Set validation criteria for updates**")
        min_accuracy = st.slider("Minimum Accuracy (%)", 0, 100, 70, help="Updates below this accuracy are rejected") / 100
        max_divergence = st.slider("Maximum Divergence (%)", 0, 100, 50, help="Updates diverging too much from global model are rejected") / 100
        
        st.info(f"✅ Accept: ≥{int(min_accuracy*100)}% accuracy & ≤{int(max_divergence*100)}% divergence")
    
    st.markdown("---")
    
    # System status with enhanced visuals
    st.subheader("📡 System Status")
    status = st.session_state.orchestrator.get_system_status()
    
    if status['blockchain_connected']:
        st.markdown('<div class="status-badge badge-success">🟢 Blockchain Online</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge badge-error">🔴 Blockchain Offline</div>', unsafe_allow_html=True)
    
    if status['contract_deployed']:
        st.markdown('<div class="status-badge badge-success">✅ Contract Deployed</div>', unsafe_allow_html=True)
        st.caption(f"📍 {status['contract_address'][:10]}...")
    else:
        st.markdown('<div class="status-badge badge-warning">⏳ Awaiting Deployment</div>', unsafe_allow_html=True)

# Main content with enhanced header
st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
st.title("🔗 Block-LoRA")
st.markdown("### **Blockchain-Enabled Federated Fine-Tuning**")
st.markdown("*Secure, Decentralized AI Training with Built-in Attack Detection*")
st.markdown('</div>', unsafe_allow_html=True)
st.markdown("---")

# Tabs with clearer labels
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Dashboard",
    "⚙️ Step 1: Setup",
    "👥 Step 2: Participants",
    "🔄 Step 3: Training",
    "📊 Step 4: Analytics"
])

# Dashboard Tab with rich information
with tab1:
    st.header("📊 System Overview Dashboard")
    
    # What is this section
    st.markdown("""
    <div class="info-card">
        <h3>💡 What You're Looking At</h3>
        <p style="font-size: 1.1rem; color: #cbd5e1; line-height: 1.8;">
            This dashboard shows the <strong>status of your blockchain-enabled federated learning network</strong>. 
            Multiple clients train AI models on their private data, then validators check the quality before 
            combining updates into a global model – all secured by blockchain technology.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics with explanations
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "✅ Honest Clients",
            status['num_honest_clients'],
            help="Participants submitting legitimate model updates"
        )
        st.caption("Submit valid updates")
    
    with col2:
        st.metric(
            "⚠️ Malicious Clients",
            status['num_malicious_clients'],
            delta="Attack Mode" if status['num_malicious_clients'] > 0 else None,
            delta_color="inverse"
        )
        st.caption("Trying to poison model")
    
    with col3:
        st.metric(
            "👮 Validators",
            status['num_validators'],
            help="Nodes verifying update quality"
        )
        st.caption("Quality gatekeepers")
    
    with col4:
        st.metric(
            "🔄 Rounds Done",
            len(st.session_state.rounds_executed),
            help="Completed training rounds"
        )
        st.caption("Training iterations")
    
    st.markdown("---")
    
    # Contract information with better presentation
    if status['contract_deployed']:
        st.subheader("🔐 Blockchain Contract Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="info-card">
                <h4>📜 Smart Contract</h4>
                <p style="font-size: 0.9rem; font-family: monospace; color: #3b82f6;">{status['contract_address']}</p>
                <p style="color: #94a3b8;">All decisions recorded on blockchain</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if 'chain_round' in status:
                st.markdown(f"""
                <div class="info-card">
                    <h4>🔄 Current Round</h4>
                    <p style="font-size: 2rem; font-weight: 800; color: #8b5cf6;">{status['chain_round']}</p>
                    <p style="color: #94a3b8;">Synchronized with blockchain</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Recent activity with color-coded logs
    st.subheader("📜 Recent Activity Log")
    st.markdown("*See what's happening in real-time*")
    
    logs = st.session_state.orchestrator.get_logs(15)
    
    if logs:
        log_container = st.container()
        with log_container:
            for log in reversed(logs):
                level = log['level']
                icon_map = {
                    'success': ('✅', '#10b981'),
                    'error': ('❌', '#ef4444'),
                    'warn': ('⚠️', '#f59e0b'),
                    'info': ('ℹ️', '#06b6d4')
                }
                icon, color = icon_map.get(level, ('ℹ️', '#06b6d4'))
                
                st.markdown(f"""
                    <div style="
                        padding: 0.75rem; 
                        margin: 0.5rem 0; 
                        background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(139, 92, 246, 0.03)); 
                        border-left: 4px solid {color}; 
                        border-radius: 8px;
                    ">
                        <code style="color: #94a3b8;">{log['timestamp']}</code> 
                        <span style="font-size: 1.2rem;">{icon}</span> 
                        <span style="color: #e2e8f0; font-size: 1.05rem;">{log['message']}</span>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("💤 **No activity yet**\n\nGet started by setting up the system in the **Setup tab**!")

# Setup Tab with clear instructions
with tab2:
    st.header("⚙️ Step 1: System Setup")
    
    if not st.session_state.setup_complete:
        # Explanation of what this step does
        st.markdown("""
        <div class="info-card">
            <h3>🎯 What Happens in This Step</h3>
            <p style="font-size: 1.1rem; color: #cbd5e1; line-height: 1.8;">
                We'll <strong>connect to your local blockchain</strong> and <strong>deploy the smart contract</strong> 
                that manages the federated learning process. The contract automatically validates updates, tracks trust scores, 
                and ensures only quality contributions are accepted.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Prerequisites checklist
        st.markdown("### ✅ Prerequisites Checklist")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            <div style="background: rgba(59, 130, 246, 0.1); padding: 1.5rem; border-radius: 12px; border-left: 4px solid #3b82f6;">
                <h4>1️⃣ Start Blockchain Node</h4>
                <code style="background: rgba(15, 23, 42, 0.8); padding: 0.5rem; display: block; border-radius: 6px;">
                    npx hardhat node
                </code>
                <p style="color: #94a3b8; margin-top: 1rem;">Keep this running in Terminal 1</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: rgba(139, 92, 246, 0.1); padding: 1.5rem; border-radius: 12px; border-left: 4px solid #8b5cf6;">
                <h4>2️⃣ Compile Smart Contract</h4>
                <code style="background: rgba(15, 23, 42, 0.8); padding: 0.5rem; display: block; border-radius: 6px;">
                    npx hardhat compile
                </code>
                <p style="color: #94a3b8; margin-top: 1rem;">Run once before first use</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Prominent action button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 INITIALIZE SYSTEM", type="primary", use_container_width=True):
                with st.spinner("🔄 Connecting to blockchain and deploying contract..."):
                    result = st.session_state.orchestrator.setup_blockchain(rpc_url)
                    
                    if result['success']:
                        st.session_state.setup_complete = True
                        st.success("✅ **System Successfully Initialized!**")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ **Initialization Failed**\n\n{result['error']}")
                        st.info("💡 **Troubleshooting:**\n- Ensure Hardhat node is running\n- Check RPC URL in sidebar\n- Verify contract is compiled")
    else:
        # Success state with detailed information
        st.success("✅ **System is Ready!**")
        st.markdown("""
        <div class="info-card">
            <h3>🎉 Setup Complete - What Just Happened</h3>
            <p style="font-size: 1.1rem; color: #cbd5e1; line-height: 1.8;">
                Your smart contract is now <strong>deployed on the blockchain</strong>! This contract will:
                <ul style="font-size: 1.05rem; line-height: 2; color: #e2e8f0;">
                    <li>✅ Accept model update submissions from clients</li>
                    <li>🛡️ Coordinate validators to check update quality</li>
                    <li>📊 Track trust scores for each participant</li>
                    <li>🔒 Create an immutable audit trail of all decisions</li>
                </ul>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Contract details
        st.markdown("### 📋 Deployment Details")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📜 Contract Address", f"{status['contract_address'][:10]}...")
            st.caption(status['contract_address'])
        
        with col2:
            if 'chain_id' in status:
                st.metric("⛓️ Chain ID", status.get('chain_id', 'N/A'))
                st.caption("Hardhat local network")
        
        with col3:
            st.metric("👤 Admin Address", f"{status.get('admin_address', 'N/A')[:10]}..." if status.get('admin_address') else 'N/A')
            st.caption("Contract owner")
        
        st.markdown("---")
        st.markdown("**✨ Next Step:** Go to the **Participants tab** to create your federated learning network!")
        
        if st.button("🔄 Reset System", help="Start over with a fresh deployment"):
            st.session_state.orchestrator = BlockLoRAOrchestrator()
            st.session_state.setup_complete = False
            st.session_state.participants_created = False
            st.session_state.rounds_executed = []
            st.rerun()

# Participants Tab with detailed explanations
with tab3:
    st.header("👥 Step 2: Create Participants")
    
    if not st.session_state.setup_complete:
        st.warning("⚠️ **Setup Required First**\n\nPlease complete System Setup in the previous tab before creating participants.")
    
    elif not st.session_state.participants_created:
        # Explanation section
        st.markdown("""
        <div class="info-card">
            <h3>🎯 What Happens in This Step</h3>
            <p style="font-size: 1.1rem; color: #cbd5e1; line-height: 1.8;">
                We'll create your <strong>federated learning network</strong> with three types of participants:
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Participant role explanations
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(5, 150, 105, 0.1)); 
                        padding: 1.5rem; border-radius: 12px; border: 2px solid #10b981; height: 100%;">
                <h3 style="color: #10b981;">✅ Honest Clients</h3>
                <p style="color: #cbd5e1; font-size: 1.05rem; line-height: 1.6;">
                    • Train models on their private data<br>
                    • Submit legitimate updates<br>
                    • Earn trust over time<br>
                    • Improve the global model
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(217, 119, 6, 0.1)); 
                        padding: 1.5rem; border-radius: 12px; border: 2px solid #f59e0b; height: 100%;">
                <h3 style="color: #f59e0b;">⚠️ Malicious Clients</h3>
                <p style="color: #cbd5e1; font-size: 1.05rem; line-height: 1.6;">
                    • Attempt {attack_type} attacks<br>
                    • Try to poison the model<br>
                    • Get detected by validators<br>
                    • Lose trust when rejected
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(37, 99, 235, 0.1)); 
                        padding: 1.5rem; border-radius: 12px; border: 2px solid #3b82f6; height: 100%;">
                <h3 style="color: #3b82f6;">👮 Validators</h3>
                <p style="color: #cbd5e1; font-size: 1.05rem; line-height: 1.6;">
                    • Download submitted updates<br>
                    • Test accuracy and quality<br>
                    • Vote to accept or reject<br>
                    • Protect model integrity
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Current configuration display
        st.markdown("### 📋 Your Configuration")
        config_col1, config_col2 = st.columns([3, 1])
        
        with config_col1:
            st.markdown(f"""
            <div class="info-card">
                <p style="font-size: 1.1rem; color: #e2e8f0; line-height: 2;">
                    <strong>Network Size:</strong> {num_honest + num_malicious + num_validators} participants<br>
                    <span style="color: #10b981;">✅ {num_honest} Honest Clients</span> | 
                    <span style="color: #f59e0b;">⚠️ {num_malicious} Malicious ({attack_type})</span> | 
                    <span style="color: #3b82f6;">👮 {num_validators} Validators</span>
                </p>
                <p style="color: #94a3b8;">Adjust these numbers in the sidebar if needed</p>
            </div>
            """, unsafe_allow_html=True)
        
        with config_col2:
            if st.button("👥 CREATE PARTICIPANTS", type="primary", use_container_width=True):
                with st.spinner("⏳ Initializing participants... This may take ~10 seconds"):
                    result = st.session_state.orchestrator.create_participants(
                        num_honest=num_honest,
                        num_malicious=num_malicious,
                        attack_type=attack_type,
                        num_validators=num_validators,
                        base_model=base_model
                    )
                    
                    if result['success']:
                        st.session_state.participants_created = True
                        st.success("✅ **All Participants Created Successfully!**")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ **Creation Failed**\n\n{result['error']}")
    
    else:
        # Success state with participant overview
        st.success("✅ **Network is Ready!**")
        
        st.markdown("""
        <div class="info-card">
            <h3>🎉 Participants Created - Your Network is Live</h3>
            <p style="font-size: 1.1rem; color: #cbd5e1; line-height: 1.8;">
                Your federated learning network is now operational! Each participant has been:
                <ul style="font-size: 1.05rem; line-height: 2; color: #e2e8f0;">
                    <li>📝 Registered on the blockchain</li>
                    <li>🔑 Assigned a unique wallet address</li>
                    <li>🤖 Loaded with the base AI model ({base_model})</li>
                    <li>⭐ Given an initial trust score of 500/1000</li>
                </ul>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Participant metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("✅ Honest Clients", status['num_honest_clients'])
            st.caption("Ready to submit valid updates")
        
        with col2:
            st.metric("⚠️ Malicious Clients", status['num_malicious_clients'], delta="Will be Detected")
            st.caption(f"Attempting {attack_type} attacks")
        
        with col3:
            st.metric("👮 Validators", status['num_validators'])
            st.caption("Protecting model quality")
        
        st.markdown("---")
        
        # Trust scores display
        trust_scores = st.session_state.orchestrator.get_trust_scores()
        
        if trust_scores:
            st.subheader("🎯 Current Trust Scores")
            st.markdown("*Trust scores determine how much weight each client's update receives*")
            
            # Create DataFrame with color-coded display
            trust_data = []
            for addr, score_data in trust_scores.items():
                trust_data.append({
                    "Participant": f"{addr[:8]}...{addr[-6:]}",
                    "Trust Score": score_data['score'],
                    "Updates Accepted": score_data['accepted'],
                    "Updates Rejected": score_data['rejected'],
                    "Status": "Trusted" if score_data['score'] >= 500 else "Untrusted"
                })
            
            df = pd.DataFrame(trust_data)
            st.dataframe(df, use_container_width=True)
            
            st.caption("💡 Trust increases (+50) for accepted updates, decreases (-100) for rejected ones")
        
        st.markdown("---")
        st.markdown("**✨ Next Step:** Go to the **Training tab** to execute a federated learning round!")

# Training Rounds Tab with detailed progress
with tab4:
    st.header("🔄 Step 3: Execute Training Rounds")
    
    if not st.session_state.participants_created:
        st.warning("⚠️ **Participants Required First**\n\nPlease create participants in the previous tab before starting training.")
    
    else:
        # Explanation of the training process
        st.markdown("""
        <div class="info-card">
            <h3>🎯 What Happens During a Training Round</h3>
            <p style="font-size: 1.1rem; color: #cbd5e1; line-height: 1.8;">
                Each round consists of <strong>4 phases</strong> that typically take 2-5 minutes total:
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Phase breakdown
        phase_col1, phase_col2, phase_col3, phase_col4 = st.columns(4)
        
        with phase_col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(37, 99, 235, 0.05)); 
                        padding: 1.2rem; border-radius: 12px; border: 2px solid #3b82f6; text-align: center;">
                <h2 style="color: #3b82f6;">1️⃣</h2>
                <h4>Client Training</h4>
                <p style="color: #94a3b8; font-size: 0.9rem;">Clients fine-tune models locally on private data</p>
            </div>
            """, unsafe_allow_html=True)
        
        with phase_col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(124, 58, 237, 0.05)); 
                        padding: 1.2rem; border-radius: 12px; border: 2px solid #8b5cf6; text-align: center;">
                <h2 style="color: #8b5cf6;">2️⃣</h2>
                <h4>Validation</h4>
                <p style="color: #94a3b8; font-size: 0.9rem;">Validators test updates for quality and attacks</p>
            </div>
            """, unsafe_allow_html=True)
        
        with phase_col3:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(236, 72, 153, 0.1), rgba(219, 39, 119, 0.05)); 
                        padding: 1.2rem; border-radius: 12px; border: 2px solid #ec4899; text-align: center;">
                <h2 style="color: #ec4899;">3️⃣</h2>
                <h4>Finalization</h4>
                <p style="color: #94a3b8; font-size: 0.9rem;">Blockchain tallies votes and makes decisions</p>
            </div>
            """, unsafe_allow_html=True)
        
        with phase_col4:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.05)); 
                        padding: 1.2rem; border-radius: 12px; border: 2px solid #10b981; text-align: center;">
                <h2 style="color: #10b981;">4️⃣</h2>
                <h4>Aggregation</h4>
                <p style="color: #94a3b8; font-size: 0.9rem;">Accepted updates combine into global model</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Round execution controls
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            round_number = st.number_input(
                "Round Number",
                min_value=1,
                max_value=100,
                value=len(st.session_state.rounds_executed) + 1,
                help="Sequential round number"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if len(st.session_state.rounds_executed) == 0:
                st.info("🆕 First round - malicious updates will be detected!")
            else:
                st.success(f"✅ {len(st.session_state.rounds_executed)} round(s) completed")
        
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("▶️ START ROUND", type="primary", use_container_width=True):
                with st.spinner(f"🔄 Executing Round {round_number}..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Phase 1: Training
                    status_text.markdown("**Phase 1/4:** 🤖 Clients training models on private data...")
                    progress_bar.progress(10)
                    time.sleep(0.5)
                    
                    result = st.session_state.orchestrator.execute_round(round_number)
                    progress_bar.progress(25)
                    
                    # Phase 2: Validation
                    status_text.markdown("**Phase 2/4:** 🛡️ Validators checking update quality...")
                    progress_bar.progress(50)
                    time.sleep(0.5)
                    
                    # Phase 3: Finalization
                    status_text.markdown("**Phase 3/4:** ⚖️ Blockchain tallying votes...")
                    progress_bar.progress(75)
                    time.sleep(0.5)
                    
                    if result['success']:
                        # Phase 4: Aggregation
                        status_text.markdown("**Phase 4/4:** 🔄 Aggregating accepted updates...")
                        progress_bar.progress(90)
                        
                        agg_result = st.session_state.orchestrator.aggregate_updates(
                            round_number,
                            base_model=base_model
                        )
                        
                        progress_bar.progress(100)
                        status_text.markdown("**✅ Round Complete!**")
                        
                        if round_number not in st.session_state.rounds_executed:
                            st.session_state.rounds_executed.append(round_number)
                        
                        # Show immediate results
                        st.success(f"✅ **Round {round_number} Completed Successfully!**")
                        
                        res_col1, res_col2 = st.columns(2)
                        with res_col1:
                            st.metric("✅ Accepted Updates", result['accepted'], delta="Good Quality")
                        with res_col2:
                            st.metric("❌ Rejected Updates", result['rejected'], delta="Detected Attacks", delta_color="inverse")
                        
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(f"❌ **Round Failed**\n\n{result['error']}")
        
        st.markdown("---")
        
        # Round history
        if st.session_state.rounds_executed:
            st.subheader("📋 Training History")
            st.markdown("*Click on a round to see detailed results*")
            
            for round_num in st.session_state.rounds_executed:
                with st.expander(f"🔄 Round {round_num} - Completed", expanded=False):
                    round_data = st.session_state.orchestrator.get_round_results(round_num)
                    
                    if round_data:
                        result_col1, result_col2 = st.columns(2)
                        
                        with result_col1:
                            st.metric("✅ Accepted Updates", len(round_data['accepted']))
                            st.caption("These updates improved the global model")
                        
                        with result_col2:
                            st.metric("❌ Rejected Updates", len(round_data['rejected']))
                            st.caption("These were malicious or low-quality")
        
        # Live log viewer with enhanced formatting
        st.subheader("📜 Live Activity Log")
        st.markdown("*Real-time updates from the current and previous rounds*")
        
        log_container = st.container()
        with log_container:
            logs = st.session_state.orchestrator.get_logs(30)
            
            if logs:
                for log in reversed(logs):
                    level = log['level']
                    icon_map = {
                        'success': ('✅', '#10b981'),
                        'error': ('❌', '#ef4444'),
                        'warn': ('⚠️', '#f59e0b'),
                        'info': ('ℹ️', '#06b6d4')
                    }
                    icon, color = icon_map.get(level, ('ℹ️', '#06b6d4'))
                    
                    st.markdown(f"""
                        <div style="
                            padding: 0.75rem; 
                            margin: 0.4rem 0; 
                            background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(139, 92, 246, 0.03)); 
                            border-left: 4px solid {color}; 
                            border-radius: 8px;
                        ">
                            <code style="color: #94a3b8;">{log['timestamp']}</code> 
                            <span style="font-size: 1.1rem;">{icon}</span> 
                            <span style="color: #e2e8f0;">{log['message']}</span>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("No logs yet - execute a round to see activity")

# Analytics Tab with comprehensive visuals
with tab5:
    st.header("📊 Step 4: View Analytics & Results")
    
    trust_scores = st.session_state.orchestrator.get_trust_scores()
    
    if trust_scores:
        # What you're looking at section
        st.markdown("""
        <div class="info-card">
            <h3>💡 Understanding the Results</h3>
            <p style="font-size: 1.1rem; color: #cbd5e1; line-height: 1.8;">
                These charts show how the system <strong>detected and rejected malicious updates</strong> while 
                accepting legitimate contributions. Trust scores reflect each participant's reliability over time.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Trust Score Chart with explanation
        st.subheader("🎯 Trust Score Distribution")
        st.markdown("*Higher scores = more reliable participants. Scores range from 0-1000.*")
        
        trust_data = []
        labels = []
        colors_list = []
        for addr, score_data in trust_scores.items():
            trust_data.append(score_data['score'])
            labels.append(f"{addr[:8]}")
            # Color based on score
            if score_data['score'] >= 600:
                colors_list.append('#10b981')  # Green for trusted
            elif score_data['score'] >= 400:
                colors_list.append('#f59e0b')  # Amber for uncertain
            else:
                colors_list.append('#ef4444')  # Red for untrusted
        
        fig = go.Figure(data=[
            go.Bar(
                x=labels,
                y=trust_data,
                marker=dict(
                    color=colors_list,
                    line=dict(color='rgba(255, 255, 255, 0.3)', width=2)
                ),
                text=[f"{score}/1000" for score in trust_data],
                textposition='auto',
                textfont=dict(size=14, color='white', family='Arial Black')
            )
        ])
        
        fig.update_layout(
            title=dict(
                text="Trust Scores by Participant Address",
                font=dict(size=20, color='#f8fafc')
            ),
            xaxis_title="Participant Address",
            yaxis_title="Trust Score (0-1000)",
            template="plotly_dark",
            height=450,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(range=[0, 1000])
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.caption("🟢 Green = Trusted (≥600) | 🟡 Amber = Uncertain (400-599) | 🔴 Red = Untrusted (<400)")
        
        # Acceptance vs Rejection with explanation
        st.markdown("---")
        st.subheader("✅ Update Acceptance Rate")
        st.markdown("*Green bars show accepted updates, red bars show rejected malicious attempts*")
        
        accepted_counts = [score_data['accepted'] for score_data in trust_scores.values()]
        rejected_counts = [score_data['rejected'] for score_data in trust_scores.values()]
        
        fig2 = go.Figure(data=[
            go.Bar(
                name='✅ Accepted (Valid)', 
                x=labels, 
                y=accepted_counts, 
                marker_color='#10b981',
                text=accepted_counts,
                textposition='auto'
            ),
            go.Bar(
                name='❌ Rejected (Malicious)', 
                x=labels, 
                y=rejected_counts, 
                marker_color='#ef4444',
                text=rejected_counts,
                textposition='auto'
            )
        ])
        
        fig2.update_layout(
            barmode='stack',
            title=dict(
                text="Update Acceptance Status by Participant",
                font=dict(size=20, color='#f8fafc')
            ),
            xaxis_title="Participant Address",
            yaxis_title="Number of Updates",
            template="plotly_dark",
            height=450,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(
                font=dict(size=14),
                orientation="h",
                y=1.1
            )
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("💡 Rejected updates indicate detected attacks - the system is working!")
        
    else:
        st.info("""
        📊 **No Data Available Yet**
        
        Execute at least one training round to see analytics and visualizations.
        Go to the **Training** tab to get started!
        """)
    
    st.markdown("---")
    
    # System metrics with detailed explanations
    st.subheader("📈 Overall System Metrics")
    
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        st.metric("🔄 Total Rounds", len(st.session_state.rounds_executed))
        st.caption("Training iterations completed")
    
    with metric_col2:
        if 'total_updates' in status:
            st.metric("📤 Total Updates", status['total_updates'])
            st.caption("Submissions from all clients")
    
    with metric_col3:
        if trust_scores:
            avg_trust = sum(s['score'] for s in trust_scores.values()) / len(trust_scores)
            st.metric("⭐ Avg Trust Score", f"{avg_trust:.0f}/1000")
            st.caption("Network health indicator")

# Enhanced footer with help information
st.markdown("---")
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.caption("🔗 **Block-LoRA:** Blockchain-Enabled Federated Fine-Tuning | Built with Streamlit")

with col2:
    st.caption("📚 [Documentation](file:///d:/Block-LoRa/FRONTEND.md)")

with col3:
    st.caption("💡 [Quick Start Guide](file:///d:/Block-LoRa/QUICKSTART.md)")
