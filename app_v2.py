import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from prediction import predict_loss
from gemini_ai import ask_gemini
import plotly.express as px


st.set_page_config(page_title="Production Loss Agent", layout="wide")
st.markdown("""
<style>

/* Sidebar background */
[data-testid="stSidebar"]{
    background:#0F172A;
}

/* Sidebar text */
[data-testid="stSidebar"] *{
    color:white;
}

/* Section titles */
.sidebar-title{
    font-size:22px;
    font-weight:bold;
    color:#60A5FA;
}

.sidebar-sub{
    color:#CBD5E1;
    font-size:14px;
}

hr{
    border:1px solid #334155;
}

</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>

.section-title{
    background:linear-gradient(90deg,#2563EB,#1D4ED8);
    color:white;
    padding:12px 18px;
    border-radius:10px;
    font-size:24px;
    font-weight:bold;
    margin-top:20px;
    margin-bottom:15px;
    box-shadow:0 3px 10px rgba(0,0,0,0.2);
}

.info-card{
    background:#1E293B;
    color:white;
    border-left:6px solid #3B82F6;
    padding:20px;
    border-radius:12px;
    margin-top:20px;
    box-shadow:0 6px 20px rgba(0,0,0,0.4);
}

.info-card h3{
    color:#60A5FA;
}

.info-card p{
    color:#E2E8F0;
    font-size:17px;
    margin:12px 0;
}
            
.footer{
    text-align:center;
    color:gray;
    padding:20px;
    font-size:14px;
}

</style>
""", unsafe_allow_html=True)

from datetime import datetime

# -----------------------------
# Premium Dashboard Header
# -----------------------------

current_time = datetime.now().strftime("%d %B %Y | %I:%M %p")

st.markdown("""
<style>
.main-header{
    background: linear-gradient(90deg,#0F172A,#1E3A8A);
    padding:25px;
    border-radius:15px;
    color:white;
    margin-bottom:20px;
    box-shadow:0px 5px 20px rgba(0,0,0,0.25);
}

.main-title{
    font-size:38px;
    font-weight:700;
    margin-bottom:5px;
}

.sub-title{
    font-size:17px;
    color:#D1D5DB;
}

.badge{
    display:inline-block;
    background:#22C55E;
    color:white;
    padding:6px 14px;
    border-radius:25px;
    font-size:14px;
    margin-top:12px;
    font-weight:600;
}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="main-header">

<div class="main-title">
🏭 AI Factory Intelligence Platform
</div>

<div class="sub-title">
Production Loss Analysis using AI • Machine Learning • Gemini LLM
</div>

<br>

<b>Project:</b> AI-Powered Production Loss Analysis and Factory Intelligence Agent

<br>

<b>Dashboard Time:</b> {current_time}

<br><br>

<span class="badge">
Industry 4.0 Ready
</span>

</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("""
<div class="sidebar-title">
🏭 AI Factory Intelligence
</div>

<div class="sidebar-sub">
Industry 4.0 Analytics Dashboard
</div>

<hr>
""", unsafe_allow_html=True)

st.sidebar.subheader("📂 Upload Factory Data")

scada_file = st.sidebar.file_uploader(
    "Upload SCADA Data",
    type=["csv"]
)

downtime_file = st.sidebar.file_uploader(
    "Upload Downtime Logs",
    type=["csv"]
)

target_file = st.sidebar.file_uploader(
    "Upload Production Targets",
    type=["csv"]
)
if (
    scada_file is not None
    and downtime_file is not None
    and target_file is not None
):

    scada_df = pd.read_csv(scada_file)
    downtime_df = pd.read_csv(downtime_file)
    target_df = pd.read_csv(target_file)

    # CSV Validation
    required_scada = ["Date", "Machine", "ActualProduction"]
    required_downtime = ["Date", "Machine", "Downtime_Minutes", "Reason"]
    required_target = ["Date", "TargetProduction"]

    if not all(col in scada_df.columns for col in required_scada):
        st.error("SCADA CSV format is incorrect.")
        st.stop()

    if not all(col in downtime_df.columns for col in required_downtime):
        st.error("Downtime CSV format is incorrect.")
        st.stop()

    if not all(col in target_df.columns for col in required_target):
        st.error("Target CSV format is incorrect.")
        st.stop()

    if scada_df.empty:
        st.error("SCADA file is empty.")
        st.stop()

    if downtime_df.empty:
        st.error("Downtime file is empty.")
        st.stop()

    if target_df.empty:
        st.error("Target file is empty.")
        st.stop()

else:
    st.warning("Please upload all 3 files.")
    st.stop()

df = pd.merge(scada_df, target_df, on="Date")
df = pd.merge(df, downtime_df, on=["Date", "Machine"])

df["Loss"] = (
    df["TargetProduction"] - df["ActualProduction"]
)

df["Efficiency"] = (
    df["ActualProduction"]
    /
    df["TargetProduction"]
) * 100

LOSS_COST_PER_UNIT = 10

df["LossCost"] = (
    df["Loss"] * LOSS_COST_PER_UNIT
)

def classify(reason):
    if reason in ["Pump Failure", "Compressor Failure", "Valve Issue"]:
        return "Equipment Loss"
    elif reason == "Power Failure":
        return "Utility Loss"
    elif reason == "Maintenance":
        return "Planned Loss"
    else:
        return "Human Loss"

df["Category"] = df["Reason"].apply(classify)
# -----------------------------
# Welcome Section
# -----------------------------
st.sidebar.markdown("---")

st.sidebar.success("👤 Welcome\n\nMuzammil")

st.sidebar.info("""
📊 Dashboard Version

v1.0
""")

# -----------------------------
# Gemini AI
# -----------------------------

st.sidebar.header("🤖 Gemini AI")

api_key = st.sidebar.text_input(
    "Gemini API Key",
    type="password"
)



st.sidebar.header("Filters")

selected_category = st.sidebar.multiselect(
    "Select Category",
    df["Category"].unique(),
    default=df["Category"].unique()
)


filtered_df = df[df["Category"].isin(selected_category)]
# ==========================
# Calculate Efficiency & Risk
# ==========================

target_sum = filtered_df["TargetProduction"].sum()

if target_sum > 0:
    efficiency = (
        filtered_df["ActualProduction"].sum()
        / target_sum
    ) * 100
else:
    efficiency = 0

if efficiency >= 90:
    risk = "LOW"
elif efficiency >= 75:
    risk = "MEDIUM"
else:
    risk = "HIGH"

st.markdown(
    '<div class="section-title">📊 Production Summary</div>',
    unsafe_allow_html=True
)
# -----------------------------
# KPI ROW 1
# -----------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "📦 Target Production",
        int(filtered_df["TargetProduction"].sum())
    )

with col2:
    st.metric(
        "🏭 Actual Production",
        int(filtered_df["ActualProduction"].sum())
    )

with col3:
    st.metric(
        "⚡ Efficiency",
        f"{round(efficiency,2)}%"
    )

with col4:
    st.metric(
        "💰 Loss Cost",
        f"₹{int(filtered_df['LossCost'].sum())}"
    )

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------
# KPI ROW 2
# -----------------------------

col5, col6, col7, col8 = st.columns(4)

with col5:
    st.metric(
        "📉 Production Loss",
        int(filtered_df["Loss"].sum())
    )

with col6:
    st.metric(
        "⏱ Total Downtime",
        int(filtered_df["Downtime_Minutes"].sum())
    )

with col7:
    st.metric(
        "📊 Avg Downtime",
        round(filtered_df["Downtime_Minutes"].mean(),1)
    )

with col8:
    st.metric(
        "🚨 Factory Risk",
        risk
    )
    

st.markdown("---")

# ====================================
# Executive Dashboard
# ====================================

st.markdown("""
<div class="section-title">
🏭 Factory Executive Dashboard
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

# Factory Status
with col1:

    if efficiency >= 90:
        st.success("🟢 Factory Status\n\nExcellent")

    elif efficiency >= 75:
        st.warning("🟡 Factory Status\n\nAverage")

    else:
        st.error("🔴 Factory Status\n\nCritical")

# AI Recommendation
with col2:

    if risk == "LOW":
        recommendation = "Continue current production strategy."

    elif risk == "MEDIUM":
        recommendation = "Reduce downtime through preventive maintenance."

    else:
        recommendation = "Immediate management intervention required."

    st.info(f"""
🤖 AI Recommendation

{recommendation}
""")

# Financial Summary
with col3:

    st.metric(
        "💰 Estimated Financial Loss",
        f"₹{int(filtered_df['LossCost'].sum())}"
    )

if efficiency >= 90:
    st.success("✅ Excellent Production Efficiency")
elif efficiency >= 75:
    st.warning("⚠️ Average Production Efficiency")
else:
    st.error("❌ Poor Production Efficiency")



st.divider()
st.markdown("### ⚙ Factory Health Monitor")

col1, col2 = st.columns([3,1])

with col1:
    st.progress(int(efficiency))

with col2:
    st.metric(
        "Health Score",
        f"{round(efficiency,1)}%"
    )

st.write(f"🏭 Overall Factory Efficiency : **{round(efficiency,2)}%**")
st.markdown("### 🟢 Live Factory Status")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.success("🟢 Machines\n\nRunning")

with col2:
    st.info(f"📦 Active Machines\n\n{filtered_df['Machine'].nunique()}")

with col3:
    st.warning(f"⏱ Total Downtime\n\n{int(filtered_df['Downtime_Minutes'].sum())} min")

with col4:
    st.error(f"📉 Total Loss\n\n{int(filtered_df['Loss'].sum())} Units")

st.markdown("### 📌 Quick Insights")

col1, col2, col3 = st.columns(3)

with col1:
    st.success(f"""
Highest Production

{filtered_df['ActualProduction'].max()} Units
""")

with col2:
    st.warning(f"""
Highest Downtime

{filtered_df['Downtime_Minutes'].max()} Minutes
""")

with col3:
    st.error(f"""
Highest Loss

{filtered_df['Loss'].max()} Units
""")
    
st.markdown("### 📈 Data Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Records", len(filtered_df))

with col2:
    st.metric("Machines", filtered_df["Machine"].nunique())

with col3:
    st.metric("Categories", filtered_df["Category"].nunique())
# -----------------------------
# Executive Summary Card
# -----------------------------

st.markdown("""
<div class="info-card">

<h3>📋 Today's Executive Summary</h3>

<p>✅ Factory performance has been successfully analyzed.</p>

<p>✅ AI risk assessment completed.</p>

<p>✅ Machine Learning prediction generated.</p>

<p>✅ Cost analysis completed.</p>

<p>✅ Dashboard ready for management review.</p>

</div>
""", unsafe_allow_html=True)
    
st.markdown(
    '<div class="section-title">📋 Production Data</div>',
    unsafe_allow_html=True
)

# ==========================
# Data Explorer Controls
# ==========================

col1, col2, col3 = st.columns(3)

with col1:
    search_machine = st.text_input(
        "🔍 Search Machine",
        placeholder="Enter machine name..."
    )

with col2:
    sort_by = st.selectbox(
        "📊 Sort By",
        [
            "Date",
            "ActualProduction",
            "Loss",
            "Downtime_Minutes"
        ]
    )

with col3:
    ascending = st.checkbox(
        "Ascending Order",
        value=True
    )

# Copy Data
display_df = filtered_df.copy()

# Search
if search_machine:
    display_df = display_df[
        display_df["Machine"]
        .astype(str)
        .str.contains(search_machine, case=False)
    ]

# Sort
display_df = display_df.sort_values(
    by=sort_by,
    ascending=ascending
)

# Show Table
st.dataframe(
    display_df,
    use_container_width=True
)

# Download Filtered Data
csv = display_df.to_csv(index=False)

st.download_button(
    "📥 Download Filtered Data",
    csv,
    "filtered_factory_report.csv",
    "text/csv"
)
st.dataframe(filtered_df)

st.divider()

st.markdown(
    '<div class="section-title">📉 Loss by Category</div>',
    unsafe_allow_html=True
)
category_loss = filtered_df.groupby("Category")["Loss"].sum()
category_df = category_loss.reset_index()
category_df.columns = ["Category", "Loss"]

fig = px.bar(
    category_df,
    x="Category",
    y="Loss",
    color="Category",
    text="Loss",
    title="Production Loss by Category"
)

fig.update_layout(
    template="plotly_white",
    height=450
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

st.markdown(
    '<div class="section-title">🥧 Loss Distribution</div>',
    unsafe_allow_html=True
)
fig2 = px.pie(
    category_df,
    names="Category",
    values="Loss",
    hole=0.45,
    title="Loss Distribution"
)

fig2.update_layout(height=450)

st.plotly_chart(fig2, use_container_width=True)
st.divider()

st.markdown(
    '<div class="section-title">📈 Predicted Next Day Loss</div>',
    unsafe_allow_html=True
)
if len(filtered_df) > 1:
    predicted_loss = predict_loss(filtered_df["Loss"].tolist())
    st.metric("Predicted Loss", f"{predicted_loss} Units")
else:
    st.warning("Not enough data for prediction")

st.divider()

st.markdown(
    '<div class="section-title">📈 Production Trend</div>',
    unsafe_allow_html=True
)
fig3 = px.line(
    filtered_df,
    x="Date",
    y="ActualProduction",
    markers=True,
    title="Production Trend"
)

fig3.update_layout(
    template="plotly_white",
    height=450
)

st.plotly_chart(fig3, use_container_width=True)


st.markdown(
    '<div class="section-title">🔥 Highest Loss Day</div>',
    unsafe_allow_html=True
)
if not filtered_df.empty:

    max_loss_row = filtered_df.loc[
        filtered_df["Loss"].idxmax()
    ]

    st.info(f"""
Date: {max_loss_row['Date']}

Loss: {max_loss_row['Loss']} units

Reason: {max_loss_row['Reason']}
""")
    
st.divider()

st.markdown(
    '<div class="section-title">⏱ Downtime Analysis</div>',
    unsafe_allow_html=True
)
downtime_by_reason = (
    filtered_df.groupby("Reason")["Downtime_Minutes"]
    .sum()
)

highest_reason = downtime_by_reason.idxmax()

st.warning(
    f"Highest downtime caused by: {highest_reason}"
)

downtime_df_chart = downtime_by_reason.reset_index()
downtime_df_chart.columns = ["Reason", "Downtime"]

fig4 = px.bar(
    downtime_df_chart,
    x="Reason",
    y="Downtime",
    color="Reason",
    title="Downtime Analysis"
)

fig4.update_layout(
    template="plotly_white",
    height=450
)

st.plotly_chart(fig4, use_container_width=True)
# ==========================
# COST ANALYSIS
# ==========================

st.divider()

st.markdown(
    '<div class="section-title">💰 Cost Analysis</div>',
    unsafe_allow_html=True
)
cost_by_category = (
    filtered_df.groupby("Category")["LossCost"]
    .sum()
)

cost_df = cost_by_category.reset_index()
cost_df.columns = ["Category", "LossCost"]

fig5 = px.bar(
    cost_df,
    x="Category",
    y="LossCost",
    color="Category",
    text="LossCost",
    title="Cost Analysis"
)

fig5.update_layout(
    template="plotly_white",
    height=450
)

st.plotly_chart(fig5, use_container_width=True)

# Highest Cost Cause

highest_cost_reason = (
    filtered_df.groupby("Reason")["LossCost"]
    .sum()
    .idxmax()
)

highest_cost_value = (
    filtered_df.groupby("Reason")["LossCost"]
    .sum()
    .max()
)

st.error(
    f"Highest Cost Cause: {highest_cost_reason} (₹{int(highest_cost_value)})"
)

# Financial Impact

total_financial_impact = int(
    filtered_df["LossCost"].sum()
)

st.success(
    f"""
Total Financial Impact

₹{total_financial_impact}

Estimated production loss cost based on current operating conditions.
"""
)

st.divider()

st.markdown(
    '<div class="section-title">🔍 Root Cause Summary</div>',
    unsafe_allow_html=True
)
cause_count = filtered_df["Reason"].value_counts()
st.dataframe(cause_count)

st.divider()

st.markdown(
    '<div class="section-title">🤖 Gemini Factory AI Assistant</div>',
    unsafe_allow_html=True
)
st.subheader("Suggested Questions")

st.write("""
• Why is production loss high?

• Which machine causes maximum downtime?

• How can efficiency be improved?

• What is the major financial loss cause?

• Give executive summary of factory performance.

• Predict future production risks.
""")

user_question = st.text_input(
    "Ask anything about factory performance"
)
if st.button("Analyze with AI"):

    if api_key and user_question:

        factory_data = filtered_df.to_string()

        answer = ask_gemini(
            api_key,
            user_question,
            factory_data
        )

        st.success(answer)



    else:

        st.warning(
            "Enter Gemini API Key and Question"
        )
    st.divider()


    # ==========================
# AI EXECUTIVE REPORT
# ==========================


st.markdown(
    '<div class="section-title">📄 AI Executive Report</div>',
    unsafe_allow_html=True
)

if st.button("Generate Executive AI Report"):

    factory_data = filtered_df.to_string()

    report = ask_gemini(
        api_key,
        """
Generate professional factory management report.

Include:

1. Production Summary

2. Loss Analysis

3. Downtime Analysis

4. Cost Impact

5. Risk Assessment

6. Recommendations
""",
        factory_data
    )

    st.text_area(
        "Executive Report",
        report,
        height=400
    )
st.divider()


st.markdown(
    '<div class="section-title">🤖 AI Commentary</div>',
    unsafe_allow_html=True
)
for _, row in filtered_df.iterrows():
    if row["Category"] == "Equipment Loss":
        commentary = f"""
Cause:
{row['Reason']} caused equipment downtime.

Impact:
Production loss of {row['Loss']} units.

Recommendation:
Perform preventive maintenance.
"""
    elif row["Category"] == "Utility Loss":
        commentary = f"""
Cause:
Power interruption affected operations.

Impact:
Production loss of {row['Loss']} units.

Recommendation:
Improve backup power systems.
"""
    elif row["Category"] == "Planned Loss":
        commentary = f"""
Cause:
Scheduled maintenance activities.

Impact:
Temporary reduction in production.

Recommendation:
Optimize maintenance schedules.
"""
    else:
        commentary = f"""
Cause:
Operator-related issue.

Impact:
Production loss of {row['Loss']} units.

Recommendation:
Provide additional training.
"""
    st.info(commentary)

st.divider()

st.markdown(
    '<div class="section-title">📋 Executive Summary</div>',
    unsafe_allow_html=True
)
total_loss = filtered_df["Loss"].sum()
avg_efficiency = round(filtered_df["Efficiency"].mean(), 2)
top_reason = filtered_df["Reason"].value_counts().idxmax()

st.success(f"""
Total Production Loss:
{total_loss} units

Average Efficiency:
{avg_efficiency}%

Major Loss Cause:
{top_reason}

Recommended Action:
Focus on reducing downtime and improving preventive maintenance.
""")

st.divider()

st.markdown(
    '<div class="section-title">📥 Download Report</div>',
    unsafe_allow_html=True
)

csv = filtered_df.to_csv(index=False)

st.download_button(
    label="Download CSV Report",
    data=csv,
    file_name="loss_report.csv",
    mime="text/csv"
)
st.caption(
    f"🕒 Last Updated: {datetime.now().strftime('%d %b %Y, %I:%M:%S %p')}"
)
st.markdown("---")

st.markdown("""
<div class="footer">

🏭 AI Factory Intelligence Platform

Powered by Streamlit | Machine Learning | Gemini AI | Predictive Analytics

Version 1.0 • RTD 2026 Project

</div>
""", unsafe_allow_html=True)