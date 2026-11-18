import streamlit as st
import pandas as pd
import plotly.express as px
from functions import get_kpi, drill_down, get_explanation

st.set_page_config(page_title="Healthcare Metrics & Predictions Platform", layout="wide")

# Mandatory Safety Banner
st.error("⚠️ **DEMO ONLY — NOT FOR CLINICAL USE**. Public/synthetic data model.")

st.title("🏥 Healthcare Metrics & Readmission Predictions Platform")
st.markdown("Explore hospital readmission risk KPIs, drill down into cohorts, and inspect explainable AI (TreeSHAP) risk drivers.")

# Sidebar Navigation
tab = st.sidebar.radio("Navigation", ["KPI Explorer & Drill-Down", "Encounter Risk & SHAP Explainability", "Chat Assistant"])

if tab == "KPI Explorer & Drill-Down":
    st.header("📊 Population Metric & Cohort Explorer")
    
    col1, col2 = st.columns(2)
    with col1:
        metric_choice = st.selectbox(
            "Select Metric", 
            options=["readmission_rate", "total_encounters", "avg_length_of_stay", "avg_hba1c"],
            format_func=lambda x: x.replace("_", " ").title()
        )
    with col2:
        group_choice = st.selectbox(
            "Group By", 
            options=["age_band", "insurance_type", "admission_type", "primary_dx_group"],
            format_func=lambda x: x.replace("_", " ").title()
        )
        
    df_kpi = get_kpi(metric_choice, group_choice)
    
    st.subheader(f"{metric_choice.replace('_', ' ').title()} by {group_choice.replace('_', ' ').title()}")
    
    # Render Bar Chart
    fig = px.bar(
        df_kpi, 
        x="category", 
        y="metric_value", 
        text="sample_size",
        labels={"metric_value": metric_choice.replace('_', ' ').title(), "category": group_choice.replace('_', ' ').title()},
        title=f"Filtered for groups with n >= 10 (Suppression rule)"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(df_kpi, use_container_width=True)
    
    # Drill Down Section
    st.markdown("---")
    st.subheader("🔍 Cohort Drill-Down")
    selected_category = st.selectbox("Select category value to inspect individual patient encounters:", options=df_kpi["category"].tolist())
    
    if st.button("Load Encounter Records"):
        drill_df = drill_down(group_choice, selected_category)
        st.success(f"Loaded {len(drill_df)} sample encounters for `{selected_category}`:")
        st.dataframe(drill_df, use_container_width=True)

elif tab == "Encounter Risk & SHAP Explainability":
    st.header("🧠 Individual Encounter Risk & TreeSHAP Explanation")
    st.markdown("Enter a patient encounter ID (e.g., between `1` and `18000`) to inspect predicted readmission probability and top contributing risk drivers.")
    
    enc_id = st.number_input("Encounter ID", min_value=1, max_value=18000, value=1)
    
    if st.button("Explain Encounter"):
        data = get_explanation(int(enc_id))
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric(label="Predicted Readmission Probability", value=f"{data['prob_readmit']:.1%}")
            if data['prob_readmit'] > 0.5:
                st.warning("High Risk of Readmission within 30 Days")
            else:
                st.info("Low Risk of Readmission within 30 Days")
                
        with col2:
            st.subheader("Top Contributing Factors (TreeSHAP)")
            shap_df = pd.DataFrame(data["shap_drivers"])
            if not shap_df.empty:
                fig_shap = px.bar(
                    shap_df,
                    x="shap_value",
                    y="feature",
                    orientation="h",
                    text="feature_value",
                    title="Feature Impact on Risk Score (Positive increases risk)",
                    labels={"shap_value": "SHAP Value (Impact)", "feature": "Clinical Feature"}
                )
                fig_shap.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_shap, use_container_width=True)
                
                st.markdown("#### Detailed Driver Breakdown:")
                st.dataframe(shap_df[["rank", "feature", "feature_value", "shap_value"]], use_container_width=True)
            else:
                st.warning("No SHAP drivers found for this encounter ID.")

elif tab == "Chat Assistant":
    st.header("💬 Healthcare Data Chat Assistant")
    st.markdown("Ask natural language questions about our healthcare metrics. (Protected by approved function guards).")
    
    user_query = st.text_input("Ask a question (e.g., 'What is the readmission rate by insurance type?')")
    
    if user_query:
        query_lower = user_query.lower()
        st.markdown("### Assistant Response:")
        
        # Rule-based safe handler mapping to approved functions (LLM fallback/integration stub)
        if "insurance" in query_lower:
            df_res = get_kpi("readmission_rate", "insurance_type")
            st.write("Here is the readmission rate broken down by insurance type:")
            st.dataframe(df_res, use_container_width=True)
        elif "age" in query_lower:
            df_res = get_kpi("readmission_rate", "age_band")
            st.write("Here is the readmission rate broken down by age group:")
            st.dataframe(df_res, use_container_width=True)
        elif "diagnosis" in query_lower or "dx" in query_lower:
            df_res = get_kpi("readmission_rate", "primary_dx_group")
            st.write("Here is the readmission rate broken down by primary diagnosis group:")
            st.dataframe(df_res, use_container_width=True)
        else:
            st.info("I can answer questions regarding readmission rates grouped by age, insurance type, or primary diagnosis group. Please try asking about those metrics!")