def ask_factory_ai(question, df):

    total_loss = df["Loss"].sum()

    top_reason = (
        df["Reason"]
        .value_counts()
        .idxmax()
    )

    avg_efficiency = round(
        df["Efficiency"].mean(),
        2
    )

    answer = f"""
Factory Analysis Report

Question:
{question}

Total Loss:
{total_loss} units

Average Efficiency:
{avg_efficiency}%

Top Loss Cause:
{top_reason}

Recommendation:
Reduce downtime and improve preventive maintenance.
"""

    return answer