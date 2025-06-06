
import streamlit as st
import pandas as pd
import datetime

# Title and description
st.set_page_config(page_title="Asset-Based Credit Score", layout="centered")
st.title("🌾 Asset-Based Credit Scoring Demo")
st.markdown("""
This prototype demonstrates how a cassava farm's sensor data can be used to assess creditworthiness and simulate CBDC-linked loan repayments through smart contracts.
""")

# Load or simulate data
data = pd.DataFrame({
    "date": pd.date_range(start="2025-06-01", periods=7),
    "soil_moisture": [32.5, 33.0, 31.8, 30.2, 29.9, 34.0, 32.1],
    "temperature": [29.0, 30.1, 28.5, 27.0, 26.7, 30.5, 28.9],
    "yield_prediction": [1500, 1550, 1400, 1380, 1450, 1600, 1580]
})

# Visualizations
st.subheader("📈 Farm Sensor Data Trends")
st.line_chart(data.set_index("date")[["soil_moisture", "temperature"]])

st.subheader("🌾 Yield Predictions")
st.bar_chart(data.set_index("date")["yield_prediction"])

# Calculate credit score (simple proxy)
avg_yield = data["yield_prediction"].mean()
credit_score = min(100, max(30, int(avg_yield / 20)))
st.markdown(f"### 📊 Projected Credit Score: **{credit_score}** / 100")

# Consent mechanism
st.markdown("#### ✅ Data Sharing Consent")
consent = st.checkbox("I agree to share my farm data with the lender.")
if consent:
    st.success("Consent recorded. Smart contract logic activated for repayment.")

# CBDC repayment simulation
st.markdown("#### 💸 CBDC Smart Contract Simulation")
if st.button("Simulate Repayment via Smart Contract"):
    st.write("✅ 25 tokens deducted from CBDC wallet (simulated)")
    st.balloons()

# Footer
st.markdown("---")
st.caption("Prototype demo for G20 TechSprint 2025 | Built by Alis Grave Nil")
