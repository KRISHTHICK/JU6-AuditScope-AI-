# app.py – AuditScope AI: Financial Audit Assistant

import streamlit as st
import pandas as pd
import ollama
from io import StringIO

# --- Step 1: Upload CSV/Excel and convert to DataFrame ---
def read_file(uploaded_file):
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".xlsx"):
        return pd.read_excel(uploaded_file)
    else:
        return None

# --- Step 2: Run anomaly detection (simple rules) ---
def detect_anomalies(df):
    anomalies = []
    if 'Amount' in df.columns:
        if df['Amount'].duplicated().any():
            anomalies.append("Duplicate Amount entries detected")
        if (df['Amount'] < 0).any():
            anomalies.append("Negative values found in Amount column")
        if df['Amount'].max() > df['Amount'].mean() * 5:
            anomalies.append("Outlier: Extremely high value in Amount column")
    return anomalies

# --- Step 3: Create LLM prompt ---
def generate_prompt(df):
    sample = df.head(10).to_markdown()
    prompt = f"""
You are a financial audit assistant. Review the following financial transactions and:
- Summarize income, expenses, total
- Highlight potential audit flags
- Return output in JSON with keys: Summary, Anomalies, Audit Flags

Sample Transactions:
{sample}

Respond in JSON.
"""
    return prompt

# --- Step 4: LLM-Based Report Generation ---
def analyze_with_llm(prompt):
    response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
    return response['message']['content']

# --- Streamlit UI ---
st.set_page_config(page_title="AuditScope AI", layout="wide")
st.title("🧾 AuditScope AI – Financial Audit Assistant")

uploaded_file = st.file_uploader("Upload Financial Data (CSV or Excel)", type=["csv", "xlsx"])
if uploaded_file:
    df = read_file(uploaded_file)
    if df is not None:
        st.dataframe(df)

        anomalies = detect_anomalies(df)
        if anomalies:
            st.subheader("🚩 Anomalies Detected")
            for a in anomalies:
                st.warning(a)
        else:
            st.success("No immediate anomalies detected.")

        if st.button("🧠 Generate Audit Summary"):
            with st.spinner("Analyzing with LLM..."):
                prompt = generate_prompt(df)
                output = analyze_with_llm(prompt)
                st.markdown("### 📋 Audit Report")
                st.code(output, language='json')
    else:
        st.error("Unsupported file format. Please upload CSV or Excel only.")
else:
    st.info("Upload your company’s financial data to begin audit analysis.")
