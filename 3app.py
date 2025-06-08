import streamlit as st
import pandas as pd
import plotly.express as px
from web3 import Web3

# === CONFIG ===
st.set_page_config(page_title="Asset-Based Credit Score", layout="wide")
st.title("🌾 Asset-Based Credit Scoring Demo")

# === Smart Contract Configuration ===
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

# === Wallet Connect Button ===
st.markdown("""
<script src="https://cdn.jsdelivr.net/npm/ethers@5.7.2/dist/ethers.umd.min.js"></script>
<script>
    window.addEventListener("triggerReleaseAuto", async function(event) {
        const yieldValue = event.detail;
        const provider = new ethers.providers.Web3Provider(window.ethereum);
        const signer = provider.getSigner();
        const contract = new ethers.Contract("0xfb3fc9218cb7c555b144f36390cde4c93aa8cbd6", [{
            "inputs": [{"internalType": "uint256", "name": "actualYield", "type": "uint256"}],
            "name": "releaseFunds", "outputs": [], "stateMutability": "nonpayable", "type": "function"
        }], signer);

        try {
            const tx = await contract.releaseFunds(yieldValue);
            await tx.wait();
            alert("✅ Transaction successful: " + tx.hash);
        } catch (err) {
            alert("❌ Transaction failed: " + err.message);
        }
    });

    async function connectWallet() {
        if (typeof window.ethereum !== 'undefined') {
            const [account] = await ethereum.request({ method: 'eth_requestAccounts' });
            const input = document.getElementById("wallet_address");
            input.value = account;
            input.dispatchEvent(new Event('input', { bubbles: true }));
        } else {
            alert("MetaMask not found. Please install it.");
        }
    }
</script>
<button onclick="connectWallet()" style="margin:10px;padding:10px 15px;background:#4CAF50;color:white;border:none;border-radius:5px;">🔗 Connect Wallet</button>
""", unsafe_allow_html=True)

wallet_address = st.text_input("Wallet Address", key="wallet_address")
if st.checkbox("👁️ Show Wallet Address") and wallet_address:
    st.success(f"Connected Wallet: `{wallet_address}`")

# === Mode Selection ===
mode = st.radio("Select Mode:", ["Simulate", "MetaMask (On-chain)"])

# === Data Setup ===
data = pd.read_csv("cassava_farm_data.csv")

# === Tab Layout ===
tab1, tab2 = st.tabs(["📈 Farm Monitoring & Disbursement", "🌍 Federated Comparison"])

with tab1:
    st.subheader("📊 Farm Sensor Data Trends")
    st.line_chart(data.set_index("date")[["soil_moisture", "temperature"]])

    st.subheader("🌾 Yield Predictions")
    st.bar_chart(data.set_index("date")["yield_prediction"])

    avg_yield = int(data["yield_prediction"].mean())
    credit_score = min(100, max(30, int(avg_yield / 20)))
    st.markdown(f"### 📊 Projected Credit Score: **{credit_score}** / 100")

    consent = st.checkbox("✅ I agree to share my farm data with the lender.")

    if consent:
        st.success("Consent recorded. Logic unlocked.")

        if mode == "Simulate":
            threshold = 1500
            if avg_yield >= threshold:
                st.success("✅ Simulated: Yield exceeds threshold. Funds disbursed to CBDC wallet.")
                st.balloons()
            else:
                st.warning("Simulated: Yield does not meet threshold. No disbursement.")

        elif mode == "MetaMask (On-chain)":
            if contract:
                try:
                    threshold = contract.functions.yieldThreshold().call()
                    status = contract.functions.getStatus().call()
                    st.info(f"🧾 Smart Contract Status: **{status}**, Threshold: **{threshold}**, Predicted Yield: **{avg_yield}**")

                    if avg_yield >= threshold:
                        st.success("✅ Conditions met. Triggering on-chain release.")
                        st.markdown(f"""
                        <script>
                            const event = new CustomEvent("triggerReleaseAuto", {{ detail: {avg_yield} }});
                            window.dispatchEvent(event);
                        </script>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning("Yield does not meet threshold. No on-chain release.")
                except Exception as e:
                    st.error(f"Status fetch failed: {e}")

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

st.markdown("---")
st.caption("Prototype demo for G20 TechSprint 2025 | Built by Alis Grave Nil")
