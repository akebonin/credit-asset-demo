
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

st.set_page_config(page_title="Asset-Based Credit Scoring", layout="wide")
st.title("🌾 Asset-Based Credit Scoring Demo")

# Create tabs
tab1, tab2 = st.tabs(["📈 Farm Monitoring & Credit Score", "🌍 Federated Comparison"])

with tab1:
    st.header("📈 Farm Monitoring Dashboard")
    # Load local farm data
    farm_data = pd.DataFrame({
        "date": pd.date_range(start="2025-06-01", periods=7),
        "soil_moisture": [32.5, 33.0, 31.8, 30.2, 29.9, 34.0, 32.1],
        "temperature": [29.0, 30.1, 28.5, 27.0, 26.7, 30.5, 28.9],
        "yield_prediction": [1500, 1550, 1400, 1380, 1450, 1600, 1580]
    })

    # Plot data
    st.subheader("📊 Sensor Trends")
    st.line_chart(farm_data.set_index("date")[["soil_moisture", "temperature"]])
    st.subheader("🌾 Yield Forecasts")
    st.bar_chart(farm_data.set_index("date")["yield_prediction"])

    # Credit scoring
    avg_yield = farm_data["yield_prediction"].mean()
    credit_score = min(100, max(30, int(avg_yield / 20)))
    st.markdown(f"### 💳 Projected Credit Score: **{credit_score}** / 100")

    # Consent
    st.markdown("#### ✅ Data Sharing Consent")
    consent = st.checkbox("I agree to share my farm data with the lender.")
    if consent:
        st.success("Consent recorded. Smart contract logic activated for repayment.")

    # CBDC simulation
    st.markdown("#### 💸 CBDC Smart Contract Simulation")
    if st.button("Simulate Repayment via Smart Contract"):
        st.write("✅ 25 tokens deducted from CBDC wallet (simulated)")
        st.balloons()

with tab2:
    st.header("🌍 Federated Farm Comparison")

    # Load federated dataset
    df = pd.read_csv("federated_farm_data.csv")

    # Filters
    st.sidebar.header("🔍 Filter Farms")
    regions = st.sidebar.multiselect("Select Region(s):", options=df["region"].unique(), default=df["region"].unique())
    asset_types = st.sidebar.multiselect("Select Asset Type(s):", options=df["asset_type"].unique(), default=df["asset_type"].unique())

    # Apply filters
    filtered_df = df[(df["region"].isin(regions)) & (df["asset_type"].isin(asset_types))]

    # Show selected data
    st.subheader("📋 Filtered Farms Overview")
    st.dataframe(filtered_df)

    # Visualizations
    st.subheader("📊 Yield Prediction vs Credit Score")
    fig1 = px.scatter(filtered_df, x="yield_prediction", y="credit_score",
                      color="region", size="soil_moisture", hover_data=["farm_id", "asset_type"])
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("🌾 Average Metrics by Asset Type")
    grouped = filtered_df.groupby("asset_type")[["soil_moisture", "temperature", "yield_prediction", "credit_score"]].mean().reset_index()
    fig2 = px.bar(grouped, x="asset_type", y=["soil_moisture", "temperature", "yield_prediction", "credit_score"],
                  barmode="group", title="Average Metrics by Asset Type")
    st.plotly_chart(fig2, use_container_width=True)

st.caption("Integrated demo for G20 TechSprint 2025 | Built by Alis Grave Nil")
