import streamlit as st
from web3 import Web3
import pandas as pd

# --- Page Config ---
st.set_page_config(layout="wide")
st.title("IDELITY | Hybrid Identity Dashboard")

# --- Wallet UI Placeholder ---
w_address = st.empty()
wallet_visibility = st.checkbox("👁️ Show Wallet Address")

# --- JavaScript Injection for MetaMask Connection and releaseFunds() ---
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

# --- Wallet Address Injection ---
wallet_address = st.experimental_data_editor(key="wallet_key")
if wallet_visibility and wallet_address:
    w_address.markdown(f"**Connected Wallet:** `{wallet_address}`")

# --- Mode Selection ---
mode = st.radio("Select Mode:", ["Simulate", "MetaMask (On-chain)"])

# --- Smart Contract Setup ---
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

# --- Contract Interaction Section ---
st.markdown("### Smart Contract Interaction")
if contract:
    if st.button("🔄 Read Status"):
        try:
            current_status = contract.functions.getStatus().call()
            st.success(f"Smart Contract Status: {current_status}")
        except Exception as e:
            st.error(f"Read error: {str(e)}")

    if mode == "MetaMask (On-chain)":
        st.markdown("""
        <input type="text" id="yieldInput" placeholder="Enter Actual Yield (uint256)" style="padding: 10px; width: 250px; margin-top: 10px;" />
        <button onclick="triggerRelease()" style="padding: 10px; background-color: #FF5722; color: white; border: none; border-radius: 5px; margin-left: 10px;">🚀 Trigger Release (On-chain)</button>
        """, unsafe_allow_html=True)
    elif mode == "Simulate":
        yield_val = st.number_input("🧪 Enter Simulated Yield", min_value=0, step=10)
        if st.button("✅ Simulate releaseFunds"):
            st.success(f"Simulated: If actualYield = {yield_val}, contract.releaseFunds({yield_val}) would be called.")
else:
    st.warning("Smart contract not initialized.")

# --- Federated Data View (Mocked) ---
st.markdown("### Federated Data Visualization")
col1, col2 = st.columns(2)
selected_region = col1.selectbox("Region Filter", ["All", "EU", "Asia", "US"])
selected_status = col2.selectbox("Status Filter", ["All", "Verified", "Unverified"])

# Mock Federated Dataset
data = pd.DataFrame({
    "Node": ["Berlin", "Madrid", "Seoul", "Chicago"],
    "Region": ["EU", "EU", "Asia", "US"],
    "Status": ["Verified", "Unverified", "Verified", "Unverified"],
    "Identities": [140, 90, 200, 150]
})

if selected_region != "All":
    data = data[data["Region"] == selected_region]
if selected_status != "All":
    data = data[data["Status"] == selected_status]

st.dataframe(data, use_container_width=True)

st.markdown("---")
st.caption("Powered by IDELITY · G20 TechSprint 2025 Prototype")
