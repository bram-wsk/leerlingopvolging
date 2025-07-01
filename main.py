import streamlit as st
import pandas as pd

SHEET_URL = "https://docs.google.com/spreadsheets/d/1mY3AZgVQ53OATWh1Zir7_nnnTcVyLbjPSs9F8PJK9BA/export?format=csv"

try:
    df = pd.read_csv(SHEET_URL)
    st.success("✅ Verbonden met Google Sheet!")
    st.dataframe(df)
except Exception as e:
    st.error(f"❌ Fout bij laden: {e}")
