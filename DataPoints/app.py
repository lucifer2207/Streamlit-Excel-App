import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def process_file(file, file_type):
    # Load DataFrame based on file type
    if file_type == "csv":
        df = pd.read_csv(file)
    else:  # Excel file
        df = pd.read_excel(file)
    
    today = datetime.today()
    
    # 1. Activation is over 30 days overdue
    activation_overdue_sites = df.loc[
        df['ACTIVATION COMPLETE'].astype(str).str.contains('Overdue', na=False) & 
        df['ACTIVATION COMPLETE'].str.extract(r'(\d+)').astype(float).fillna(0).ge(30).any(axis=1), 
        'SITE NUMBER'
    ].tolist()
    
    # 2. PSV Date is after Selected Date
    df['PSV COMPLETE'] = pd.to_datetime(df['PSV COMPLETE'], errors='coerce')
    df['SELECTED'] = pd.to_datetime(df['SELECTED'], errors='coerce')
    psv_after_selected_sites = df.loc[df['PSV COMPLETE'] > df['SELECTED'], 'SITE NUMBER'].dropna().tolist()
    
    # 3. Planned Submission Date is after Planned Approval Date
    df['FIRST SUBMISSION PLANNED'] = pd.to_datetime(df['FIRST SUBMISSION PLANNED'], errors='coerce')
    df['ALL APPROVALS PLANNED'] = pd.to_datetime(df['ALL APPROVALS PLANNED'], errors='coerce')
    planned_submission_after_approval_sites = df.loc[
        df['FIRST SUBMISSION PLANNED'] > df['ALL APPROVALS PLANNED'], 'SITE NUMBER'
    ].dropna().tolist()
    
    # 4. Actual Submission Date is after Actual Approval Date
    df['FIRST SUBMISSION COMPLETE'] = pd.to_datetime(df['FIRST SUBMISSION COMPLETE'], errors='coerce')
    df['ALL APPROVALS COMPLETE'] = pd.to_datetime(df['ALL APPROVALS COMPLETE'], errors='coerce')
    actual_submission_after_approval_sites = df.loc[
        df['FIRST SUBMISSION COMPLETE'] > df['ALL APPROVALS COMPLETE'], 'SITE NUMBER'
    ].dropna().tolist()
    
    # 5. Site has been in a Selected Status for over 365 days
    df['SITE STATUS EFFECTIVE DATE'] = pd.to_datetime(df['SITE STATUS EFFECTIVE DATE'], errors='coerce')
    selected_status_sites = df.loc[
        (df['SITE STATUS'] == 'Selected') & (df['SITE STATUS EFFECTIVE DATE'] <= today - timedelta(days=365)), 
        'SITE NUMBER'
    ].dropna().tolist()
    
    # 6. Site has been in a SIV Ready Status for over 90 days
    siv_ready_sites = df.loc[
        (df['SITE STATUS'] == 'SIV Ready') & (df['SITE STATUS EFFECTIVE DATE'] <= today - timedelta(days=90)), 
        'SITE NUMBER'
    ].dropna().tolist()
    
    return {
        "Activation is over 30 days overdue": activation_overdue_sites,
        "PSV Date is after Selected Date": psv_after_selected_sites,
        "Planned Submission Date is after Planned Approval Date": planned_submission_after_approval_sites,
        "Actual Submission Date is after Actual Approval Date": actual_submission_after_approval_sites,
        "Site has been in a Selected Status for over 365 days": selected_status_sites,
        "Site has been in a SIV Ready Status for over 90 days": siv_ready_sites
    }

st.title("Excel & CSV Data Analysis Application")
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    file_type = "csv" if uploaded_file.name.endswith(".csv") else "xlsx"
    results = process_file(uploaded_file, file_type)
    
    for key, sites in results.items():
        st.write(f"**{key}** - Site Numbers: {', '.join(map(str, sites)) if sites else 'None'}")
