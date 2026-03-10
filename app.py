import streamlit as st
import pandas as pd
from openai import OpenAI

st.title("GST Narration Risk Analyzer")

st.write("Upload Excel containing narrations to identify RCM or Blocked Credit under GST.")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Download template
with open("template.xlsx", "rb") as f:
    st.download_button(
        label="Download Excel Template",
        data=f,
        file_name="GST_Narration_Template.xlsx"
    )

uploaded_file = st.file_uploader("Upload filled Excel file", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    results = []

    for narration in df["Narration"]:

        prompt = f"""
        Analyse this accounting narration for GST.

        Narration: {narration}

        Identify if it falls under:
        - Reverse Charge Mechanism
        - Blocked Credit u/s 17(5)

        Return strictly in this format:
        Keyword | Description | Category

        If nothing applicable return:
        NA | NA | No Issue
        """

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        result = response.choices[0].message.content
        parts = result.split("|")

        if len(parts) == 3:
            results.append(parts)
        else:
            results.append(["NA","NA","No Issue"])

    df["Keyword Hit"] = [r[0] for r in results]
    df["Description"] = [r[1] for r in results]
    df["Category"] = [r[2] for r in results]

    output_file = "gst_analysis_output.xlsx"
    df.to_excel(output_file, index=False)

    with open(output_file, "rb") as f:
        st.download_button(
            label="Download Result",
            data=f,
            file_name=output_file
        )
