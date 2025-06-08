import streamlit as st
import pandas as pd
import plotly.express as px
from web3 import Web3

st.set_page_config(page_title="Asset-Based Credit Scoring", layout="wide")
st.title("🌾 Asset-Based Credit Scoring Demo")

# === Blockchain config ===
INFURA_URL = f"https://sepolia.infura.io/v3/{st.secrets['INFURA_KEY']}"
CONTRACT_ADDRESS = "0xfb3fc9218cb7c555b144f36390cde4c93aa8cbd6"
ABI = [
    {"inputs": [{"internalType": "address", "name": "_borrower", "type": "address"},
                {"internalType": "uint256", "name": "_yieldThreshold", "type": "uint256"}],
     "stateMutability": "payable", "type": "constructor"},
    {"inputs": [], "name": "amount", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "borrower", "outputs": [{"internalType": "address", "name": "", "type": "address"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "disbursed", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "getStatus", "outputs": [{"internalType": "string", "name": "", "type": "string"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "lender", "outputs": [{"internalType": "address", "name": "", "type": "address"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "uint256", "name": "actualYield", "type": "uint256"}],
     "name": "releaseFunds", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [], "name": "yieldThreshold", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"}
]

try:
    w3 = Web3(Web3.HTTPProvider(INFURA_URL))
    contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI)
except Exception as e:
    contract = None
    st.error(f"❌ Web3 initialization failed: {e}")

# === Hybrid Mode ===
mode = st.radio("Select Mode:", ["Simulate", "MetaMask (On-chain)"])

# === Inject Wallet Connect Button ===
st.markdown("""
<script src="https://cdn.jsdelivr.net/npm/ethers@5.7.2/dist/ethers.umd.min.js"></script>
<script>
    async function connectWallet() {
        if (typeof window.ethereum !== 'undefined') {
            const [account] = await ethereum.request({ method: 'eth_requestAccounts' });
            const streamlitEvent = new CustomEvent("streamlit:walletConnected", { detail: account });
            window.dispatchEvent(streamlitEvent);
        } else {
            alert("MetaMask not found. Please install it.");
        }
    }

    async function triggerRelease() {
        if (typeof window.ethereum !== 'undefined') {
            const provider = new ethers.providers.Web3Provider(window.ethereum);
            const signer = provider.getSigner();
            const contractAddress = "0xfb3fc9218cb7c555b144f36390cde4c93aa8cbd6";
            const abi = [
                {"inputs": [{"internalType": "uint256", "name": "actualYield", "type": "uint256"}],
                 "name": "releaseFunds", "outputs": [], "stateMutability": "nonpayable", "type": "function"}
            ];
            const contract = new ethers.Contract(contractAddress, abi, signer);
            let yieldValue = document.getElementById("yieldInput").value;
            if (!yieldValue || isNaN(yieldValue)) {
                alert("Please enter a valid yield amount.");
                return;
            }
            try {
                const tx = await contract.releaseFunds(ethers.BigNumber.from(yieldValue));
                await tx.wait();
                alert("Transaction successful: " + tx.hash);
            } catch (err) {
                alert("Transaction failed: " + err.message);
            }
        }
    }
</script>
<button onclick="connectWallet()" style="margin-top:10px;padding:10px 15px;border:none;background-color:#4CAF50;color:white;border-radius:5px;">🔗 Connect Wallet</button>
""", unsafe_allow_html=True)

# === Wallet Address Input Hook ===
wallet_key = "wallet_address"
if wallet_key not in st.session_state:
    st.session_state[wallet_key] = ""
w_address = st.empty()
w_address.markdown(f'''
<input type="text" id="{wallet_key}" style="display:none;" />
<script>
window.addEventListener("streamlit:walletConnected", function(event) {{
    const addr = event.detail;
    document.getElementById("{wallet_key}").value = addr;
    const inputEvent = new Event("input", {{ bubbles: true }});
    document.getElementById("{wallet_key}").dispatchEvent(inputEvent);
}});
</script>
''', unsafe_allow_html=True)
wallet_address = st.text_input("Wallet Address (hidden)", value=st.session_state[wallet_key], key=wallet_key, label_visibility="collapsed")
if st.checkbox("👁️ Show Wallet Address") and wallet_address:
    st.markdown(f"**Connected Wallet:** `{wallet_address}`")

# === Main UI ===
tab1, tab2 = st.tabs(["📈 Farm Monitoring & Credit Score", "🌍 Federated Comparison"])

with tab1:
    st.header("📈 Farm Monitoring Dashboard")
    farm_data = pd.DataFrame({
        "date": pd.date_range(start="2025-06-01", periods=7),
        "soil_moisture": [32.5, 33.0, 31.8, 30.2, 29.9, 34.0, 32.1],
        "temperature": [29.0, 30.1, 28.5, 27.0, 26.7, 30.5, 28.9],
        "yield_prediction": [1500, 1550, 1400, 1380, 1450, 1600, 1580]
    })
    st.subheader("📊 Sensor Trends")
    st.line_chart(farm_data.set_index("date")["soil_moisture"])
    st.line_chart(farm_data.set_index("date")["temperature"])
    st.subheader("🌾 Yield Forecasts")
    st.bar_chart(farm_data.set_index("date")["yield_prediction"])
    avg_yield = farm_data["yield_prediction"].mean()
    credit_score = min(100, max(30, int(avg_yield / 20)))
    st.markdown(f"### 💳 Projected Credit Score: **{credit_score}** / 100")
    consent = st.checkbox("✅ I agree to share my farm data with the lender.")
    st.subheader("🔗 Smart Contract Status")
    if contract:
        try:
            status = contract.functions.getStatus().call()
            st.info(f"🧾 Smart Contract Status: **{status}**")
        except Exception as e:
            st.error(f"Failed to fetch status: {e}")
    if mode == "MetaMask (On-chain)":
        st.markdown("""
        <input type="text" id="yieldInput" placeholder="Enter Actual Yield (uint256)" style="padding: 10px; width: 250px; margin-top: 10px;" />
        <button onclick="triggerRelease()" style="padding: 10px; background-color: #FF5722; color: white; border: none; border-radius: 5px; margin-left: 10px;">🚀 Trigger Release (On-chain)</button>
        """, unsafe_allow_html=True)
    elif mode == "Simulate":
        yield_val = st.number_input("🧪 Enter Simulated Yield", min_value=0, step=10)
        if st.button("✅ Simulate releaseFunds"):
            st.success(f"Simulated: releaseFunds({yield_val}) would be called here.")

with tab2:
    st.header("🌍 Federated Farm Comparison")
    try:
        df = pd.read_csv("federated_farm_data.csv")
        st.sidebar.header("🔍 Filter Farms")
        regions = st.sidebar.multiselect("Select Region(s):", options=df["region"].unique(), default=df["region"].unique())
        asset_types = st.sidebar.multiselect("Select Asset Type(s):", options=df["asset_type"].unique(), default=df["asset_type"].unique())
        filtered_df = df[(df["region"].isin(regions)) & (df["asset_type"].isin(asset_types))]
        st.subheader("📋 Filtered Farms Overview")
        st.dataframe(filtered_df)
        st.subheader("📊 Yield Prediction vs Credit Score")
        fig1 = px.scatter(filtered_df, x="yield_prediction", y="credit_score", color="region", size="soil_moisture", hover_data=["farm_id", "asset_type"])
        st.plotly_chart(fig1, use_container_width=True)
        st.subheader("🌾 Average Metrics by Asset Type")
        grouped = filtered_df.groupby("asset_type")[["soil_moisture", "temperature", "yield_prediction", "credit_score"]].mean().reset_index()
        fig2 = px.bar(grouped, x="asset_type", y=["soil_moisture", "temperature", "yield_prediction", "credit_score"], barmode="group")
        st.plotly_chart(fig2, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to load or process federated data: {e}")

st.caption("G20 TechSprint 2025 Prototype | Built by Alis Grave Nil")
