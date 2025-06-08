import streamlit as st
import pandas as pd
import plotly.express as px
from web3 import Web3
import json

# === STREAMLIT CONFIG ===
st.set_page_config(page_title="Asset-Based Credit Scoring", layout="wide")
st.title("🌾 Asset-Based Credit Scoring Demo")

# === INFURA CONNECTION ===
INFURA_KEY = st.secrets["INFURA_KEY"]
rpc_url = f"https://sepolia.infura.io/v3/{INFURA_KEY}"
w3 = Web3(Web3.HTTPProvider(rpc_url))

# === CONTRACT SETUP ===
CONTRACT_ADDRESS = "0x35750342f1A55E8F6B799E3cD1129d6e4Df7c3B5"

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

# === MODE SWITCH ===
mode = st.sidebar.radio("Choose Mode:", ["🔍 Public Viewer Mode", "🛠 Developer/Test Mode"])
st.sidebar.markdown("---")

if mode == "🛠 Developer/Test Mode":
    custom_rpc = st.sidebar.text_input("🔗 Custom RPC", value=rpc_url)
    custom_contract = st.sidebar.text_input("📬 Contract Address", value=CONTRACT_ADDRESS)
    try:
        w3 = Web3(Web3.HTTPProvider(custom_rpc))
        contract = w3.eth.contract(address=Web3.to_checksum_address(custom_contract), abi=ABI)
        st.sidebar.success("Connected to contract ✅")
    except Exception as e:
        st.sidebar.error(f"Connection failed: {e}")
        contract = None
else:
    contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI)

# === TABS ===
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
    st.line_chart(farm_data.set_index("date")[["soil_moisture", "temperature"]])

    st.subheader("🌾 Yield Forecasts")
    st.bar_chart(farm_data.set_index("date")["yield_prediction"])

    avg_yield = farm_data["yield_prediction"].mean()
    credit_score = min(100, max(30, int(avg_yield / 20)))
    st.markdown(f"### 💳 Projected Credit Score: **{credit_score}** / 100")

    consent = st.checkbox("✅ I agree to share my farm data with the lender.")

    if contract:
        st.subheader("🔗 Smart Contract Status")
        try:
            status = contract.functions.getStatus().call()
            st.info(f"🧾 Smart Contract Status: **{status}**")
        except Exception as e:
            st.error(f"Failed to fetch status: {e}")

        if mode == "🛠 Developer/Test Mode" and consent:
            st.markdown("#### 💸 Release Funds")
            if st.button("Trigger releaseFunds()"):
                st.warning("⚠️ Wallet interaction not implemented in Streamlit — use Web UI like Remix or WalletConnect.")

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
        st.error(f"Failed to load federated data: {e}")

st.caption("G20 TechSprint 2025 Prototype | Built by Alis Grave Nil")
