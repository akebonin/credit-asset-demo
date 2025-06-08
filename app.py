import streamlit as st
import pandas as pd
import plotly.express as px
from web3 import Web3
import json
import os

st.set_page_config(page_title="Asset-Based Credit Scoring", layout="wide")
st.title("🌾 Asset-Based Credit Scoring Demo")

# === CONFIG ===
CONTRACT_ADDRESS = "0xfb3fc9218cb7c555b144f36390cde4c93aa8cbd6"  # your deployed address
ABI = [...]  # full ABI here, same as already used

# === WEB3 SETUP ===
INFURA_KEY = st.secrets["INFURA_KEY"]
RPC_URL = f"https://sepolia.infura.io/v3/{INFURA_KEY}"
w3 = Web3(Web3.HTTPProvider(RPC_URL))
contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI)

# === SIDEBAR MODE ===
mode = st.sidebar.radio("Choose Mode:", ["🔍 Viewer", "🛠 Developer"])

# === TABS ===
tab1, tab2 = st.tabs(["📈 Credit Score Dashboard", "🌍 Federated Comparison"])

with tab1:
    st.header("📊 Farm Monitoring")
    farm_data = pd.DataFrame({
        "date": pd.date_range(start="2025-06-01", periods=7),
        "soil_moisture": [32.5, 33.0, 31.8, 30.2, 29.9, 34.0, 32.1],
        "temperature": [29.0, 30.1, 28.5, 27.0, 26.7, 30.5, 28.9],
        "yield_prediction": [1500, 1550, 1400, 1380, 1450, 1600, 1580]
    })
    st.line_chart(farm_data.set_index("date")[["soil_moisture", "temperature"]])
    st.bar_chart(farm_data.set_index("date")["yield_prediction"])

    avg_yield = farm_data["yield_prediction"].mean()
    credit_score = min(100, max(30, int(avg_yield / 20)))
    st.markdown(f"### 💳 Projected Credit Score: **{credit_score}** / 100")

    consent = st.checkbox("✅ I agree to share my farm data with the lender.")

    if contract:
        st.subheader("🔗 Smart Contract Status")
        try:
            status = contract.functions.getStatus().call()
            st.info(f"📄 Status: **{status}**")
        except Exception as e:
            st.error(f"❌ Failed to fetch status: {e}")

        if mode == "🛠 Developer" and consent:
            st.markdown("#### 💸 Trigger releaseFunds (not connected to wallet in demo)")
            if st.button("Execute releaseFunds()"):
                st.warning("Metamask integration not wired in frontend logic yet.")

with tab2:
    st.header("🌍 Federated Comparison")
    try:
        df = pd.read_csv("federated_farm_data.csv")
        st.sidebar.header("🔍 Filter Farms")
        regions = st.sidebar.multiselect("Regions:", df["region"].unique(), default=df["region"].unique())
        asset_types = st.sidebar.multiselect("Assets:", df["asset_type"].unique(), default=df["asset_type"].unique())
        filtered_df = df[(df["region"].isin(regions)) & (df["asset_type"].isin(asset_types))]
        st.dataframe(filtered_df)
        fig1 = px.scatter(filtered_df, x="yield_prediction", y="credit_score", color="region", size="soil_moisture")
        st.plotly_chart(fig1, use_container_width=True)
        grouped = filtered_df.groupby("asset_type")[["soil_moisture", "temperature", "yield_prediction", "credit_score"]].mean().reset_index()
        fig2 = px.bar(grouped, x="asset_type", y=["soil_moisture", "temperature", "yield_prediction", "credit_score"], barmode="group")
        st.plotly_chart(fig2, use_container_width=True)
    except Exception as e:
        st.error(f"❌ Federated data error: {e}")

st.caption("Integrated demo for G20 TechSprint 2025 | Built by Alis Grave Nil")
