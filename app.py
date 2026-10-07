import streamlit as st
import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score

st.set_page_config(
    page_title="Nesta: ML-Powered Phishing Triage & Queue Compression",
    layout="wide"
)

st.markdown("# 🛡️ Nesta: ML-Powered Phishing Triage & Queue Compression")
st.markdown("Automated Queue Prioritization using Scikit-Learn.")

@st.cache_resource
def load_saved_model_and_data():
    csv_file = 'data/Phishing_Email.csv'
    if os.path.exists(csv_file) and os.path.exists('model.pkl') and os.path.exists('vectorizer.pkl'):
        df = pd.read_csv(csv_file, index_col=0)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        text_col = 'Email Text' if 'Email Text' in df.columns else df.columns[0]
        label_col = 'Email Type' if 'Email Type' in df.columns else df.columns[1]
        
        df = df.dropna(subset=[text_col, label_col])
        df_sample = df.head(1000).reset_index(drop=True)
        
        model = joblib.load('model.pkl')
        vectorizer = joblib.load('vectorizer.pkl')
        
        return df_sample, model, vectorizer, text_col, label_col
    else:
        return None, None, None, None, None

df, model, vectorizer, text_col, label_col = load_saved_model_and_data()

if df is not None:
    X_full = df[text_col].astype(str)
    y_true = df[label_col].astype(str)
    
    X_full_vec = vectorizer.transform(X_full)
    predictions = model.predict(X_full_vec)
    probabilities = model.predict_proba(X_full_vec)
    
    classes = list(model.classes_)
    phishing_idx = classes.index('Phishing Email') if 'Phishing Email' in classes else 1
    
    risk_scores = [round(prob[phishing_idx] * 100, 2) for prob in probabilities]
    
    df['ML Risk Score (%)'] = risk_scores
    df['ML Prediction'] = predictions
    
    # Calculate Precision, Recall, F1 for Dashboard Display
    precision = precision_score(y_true, predictions, pos_label='Phishing Email', zero_division=0)
    recall = recall_score(y_true, predictions, pos_label='Phishing Email', zero_division=0)
    f1 = f1_score(y_true, predictions, pos_label='Phishing Email', zero_division=0)
    
    total_reports = len(df)
    high_risk_count = sum(1 for score in risk_scores if score > 50)
    
    # Top Metrics Display (Including ML Performance Metrics)
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Queue Reports", total_reports)
    col2.metric("High-Risk Alerts", high_risk_count)
    col3.metric("Precision", f"{precision:.2f}")
    col4.metric("Recall", f"{recall:.2f}")
    col5.metric("F1-Score", f"{f1:.2f}")
    
    st.markdown("---")
    st.markdown("### 📄 Prioritized Analyst Triage Queue with ML Risk Scores")
    
    display_df = df[[text_col, label_col, 'ML Prediction', 'ML Risk Score (%)']].copy()
    display_df.columns = ['Email Content', 'Actual Label', 'ML Prediction', 'Risk Score (%)']
    display_df = display_df.sort_values(by='Risk Score (%)', ascending=False)
    
    st.dataframe(display_df, use_container_width=True)
    
    st.markdown(f"**Summary:** Showing **{high_risk_count}** high-risk alerts out of **{total_reports}** total ingested queue reports.")
    
else:
    st.error("⚠️ Files nahi mili. Pehle trainmodel.py run karein!")