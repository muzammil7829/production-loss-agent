import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from prediction import predict_loss
from gemini_ai import ask_gemini


st.set_page_config(page_title="Production Loss Agent", layout="wide")

st.title("🏭 AI Production Loss Explanation Agent")
st.sidebar.header("📁 Upload Files")

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

st.sidebar.header("🤖 Gemini AI")

api_key = st.sidebar.text_input(
    "Gemini API Key",
    type="password"
)

st.write("Key Length:", len(api_key))


st.sidebar.header("Filters")

selected_category = st.sidebar.multiselect(
    "Select Category",
    df["Category"].unique(),
    default=df["Category"].unique()
)

filtered_df = df[df["Category"].isin(selected_category)]

st.header("📊 Production Summary")

col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
with col1:
 st.metric(
"Target Production",
int(filtered_df["TargetProduction"].sum())
)

with col2:
 st.metric(
"Actual Production",
int(filtered_df["ActualProduction"].sum())
)

with col3:
 st.metric(
"Production Loss",
int(filtered_df["Loss"].sum())
)
 
with col4:
    target_sum = filtered_df["TargetProduction"].sum()

    if target_sum > 0:
        efficiency = (
            filtered_df["ActualProduction"].sum()
            / target_sum
        ) * 100
    else:
        efficiency = 0

    st.metric(
        "Efficiency %",
        round(efficiency, 2)
    )
with col5:
    st.metric(
        "💰 Loss Cost",
        f"₹{int(filtered_df['LossCost'].sum())}"
    )

with col6:
    st.metric(
        "⏱ Total Downtime",
        int(filtered_df["Downtime_Minutes"].sum())
    )
with col7:
    st.metric(
        "⏱ Avg Downtime",
        round(
            filtered_df["Downtime_Minutes"].mean(),
            1
        )
    )

with col8:
    st.metric(
        "🔥 Max Downtime",
        int(
            filtered_df["Downtime_Minutes"].max()
        )
    )



if efficiency >= 90:
    st.success("✅ Excellent Production Efficiency")
elif efficiency >= 75:
    st.warning("⚠️ Average Production Efficiency")
else:
    st.error("❌ Poor Production Efficiency")

if efficiency >= 90:
     risk = "LOW"
elif efficiency >= 75:
    risk = "MEDIUM"
else:
    risk = "HIGH"

st.metric(
    "🏭 Factory Risk Level",
    risk
)

st.divider()

st.header("📋 Production Data")
st.dataframe(filtered_df)

st.divider()

st.header("📉 Loss by Category")
category_loss = filtered_df.groupby("Category")["Loss"].sum()

fig, ax = plt.subplots(figsize=(6, 4))
category_loss.plot(kind="bar", ax=ax)
ax.set_ylabel("Loss Units")
st.pyplot(fig)

st.divider()

st.header("🥧 Loss Distribution")
fig2, ax2 = plt.subplots(figsize=(6, 6))
category_loss.plot(kind="pie", autopct="%1.1f%%", ax=ax2)
ax2.set_ylabel("")
st.pyplot(fig2)

st.divider()

st.header("📈 Predicted Next Day Loss")

if len(filtered_df) > 1:
    predicted_loss = predict_loss(filtered_df["Loss"].tolist())
    st.metric("Predicted Loss", f"{predicted_loss} Units")
else:
    st.warning("Not enough data for prediction")

st.divider()

st.header("📈 Production Trend")
fig3, ax3 = plt.subplots(figsize=(8, 4))
ax3.plot(
    filtered_df["Date"],
    filtered_df["ActualProduction"],
    marker="o"
)
ax3.set_ylabel("Actual Production")
ax3.set_xlabel("Date")
st.pyplot(fig3)


st.header("🔥 Highest Loss Day")
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

st.header("⏱ Downtime Analysis")

downtime_by_reason = (
    filtered_df.groupby("Reason")["Downtime_Minutes"]
    .sum()
)

highest_reason = downtime_by_reason.idxmax()

st.warning(
    f"Highest downtime caused by: {highest_reason}"
)

fig4, ax4 = plt.subplots(figsize=(8, 4))

downtime_by_reason.plot(
    kind="bar",
    ax=ax4
)

ax4.set_ylabel("Downtime Minutes")
ax4.set_xlabel("Reason")

st.pyplot(fig4)

# ==========================
# COST ANALYSIS
# ==========================

st.divider()

st.header("💰 Cost Analysis")

cost_by_category = (
    filtered_df.groupby("Category")["LossCost"]
    .sum()
)

fig5, ax5 = plt.subplots(figsize=(8,4))

cost_by_category.plot(
    kind="bar",
    ax=ax5
)

ax5.set_ylabel("Loss Cost (₹)")
ax5.set_xlabel("Category")

st.pyplot(fig5)

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

st.header("🔍 Root Cause Summary")
cause_count = filtered_df["Reason"].value_counts()
st.dataframe(cause_count)

st.divider()

st.header("🤖 Gemini Factory AI Assistant")

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


st.header("📄 AI Executive Report")

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


st.header("🤖 AI Commentary")

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

st.header("📋 Executive Summary")

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

st.header("📥 Download Report")

csv = filtered_df.to_csv(index=False)

st.download_button(
    label="Download CSV Report",
    data=csv,
    file_name="loss_report.csv",
    mime="text/csv"
)
