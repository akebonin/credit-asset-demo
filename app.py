import streamlit as st
import pandas as pd
import plotly.express as px
from web3 import Web3
import streamlit.components.v1 as components
import json

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
     "name": "releaseFunds", "outputs": [],
     "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [], "name": "yieldThreshold", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"}
]

try:
    w3 = Web3(Web3.HTTPProvider(INFURA_URL))
    contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI)
except Exception as e:
    contract = None
    st.error("❌ Web3 initialization failed: " + str(e))

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
                    st.markdown("🧾 Smart Contract Status: " + str(status))
                    st.info("Threshold: " + str(threshold) + ", Predicted Yield: " + str(avg_yield))

                    if avg_yield >= threshold:
    st.success("✅ Conditions met. Click below to trigger on-chain release.")
                            st.markdown(f"[🌐 Open MetaMask Transaction Page](https://akebonin.github.io/credit-asset-demo/releaseFunds.html?yield={avg_yield})", unsafe_allow_html=True)
                    st.markdown(f"[🌐 Open MetaMask Transaction Page](https://akebonin.github.io/credit-asset-demo/releaseFunds.html?yield={avg_yield})", unsafe_allow_html=True)

                        abi_snippet = [{
                            "inputs": [{"internalType": "uint256", "name": "actualYield", "type": "uint256"}],
                            "name": "releaseFunds",
                            "outputs": [],
                            "stateMutability": "nonpayable",
                            "type": "function"
                        }]

                        html_template = """
                        <script>
                        const loadEthers = async () => {
                          if (typeof window.ethers === 'undefined') {
                            const script = document.createElement('script');
                            script.src = 'https://cdn.jsdelivr.net/npm/ethers@5.7.2/dist/ethers.umd.min.js';
                            script.onload = runTX;
                            document.head.appendChild(script);
                          } else {
                            runTX();
                          }
                        };
                        </script>
                        <button onclick="loadEthers()" style="padding: 10px; background-color: #d62828; color: white; border: none; border-radius: 5px;">🚀 Send releaseFunds(YIELD)</button>
                        <p id="result" style="margin-top: 10px; font-family: monospace;"></p>
                        <script>
                        async function runTX() {
                          try {
                            if (typeof window.ethereum === 'undefined') throw new Error('MetaMask not available');
                            const provider = new ethers.providers.Web3Provider(window.ethereum);
                            const signer = provider.getSigner();
                            const abi = ABI_JSON;
                            const contract = new ethers.Contract('{CONTRACT_ADDRESS}', abi, signer);
                            const tx = await contract.releaseFunds(YIELD);
                            document.getElementById("result").innerText = "✅ TX sent: " + tx.hash;
                          } catch(err) {
                            document.getElementById("result").innerText = "❌ " + err.message;
                          }
                        }
                        </script>
                        """
                        html = html_template.replace("ABI_JSON", json.dumps(abi_snippet)).replace("YIELD", str(avg_yield))
                        components.html(html, height=180)
                    else:
                        st.warning("Yield does not meet threshold. No on-chain release.")
                except Exception as e:
                    st.error("Status fetch failed: " + str(e))

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
        st.error("Failed to load or process federated data: " + str(e))

st.markdown("---")
st.caption("Prototype demo for G20 TechSprint 2025 | Built by Alis Grave Nil")
