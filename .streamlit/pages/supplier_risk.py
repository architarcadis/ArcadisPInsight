import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.visualizations import create_supplier_chart
from utils.llm_analysis import generate_supplier_insights

def show(session_state):
    """Display the Supplier Risk Analysis tab content"""
    st.title("🔍 Supplier Risk Analysis")
    
    # Get data from session state
    supplier_data = session_state.supplier_data
    performance_data = session_state.performance_data
    spend_data = session_state.spend_data
    
    # Filter controls
    st.subheader("Filter Suppliers")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Category filter
        categories = ["All Categories"] + sorted(supplier_data["Category"].unique().tolist())
        selected_category = st.selectbox("Select Category:", categories, key="risk_category")
    
    with col2:
        # Country filter
        countries = ["All Countries"] + sorted(supplier_data["Country"].unique().tolist())
        selected_country = st.selectbox("Select Country:", countries)
    
    with col3:
        # Performance Score Range
        score_range = st.slider(
            "Performance Score Range:",
            min_value=1.0,
            max_value=10.0,
            value=(5.0, 10.0),
            step=0.5
        )
    
    # Apply filters to supplier data
    filtered_suppliers = supplier_data.copy()
    
    if selected_category != "All Categories":
        filtered_suppliers = filtered_suppliers[filtered_suppliers["Category"] == selected_category]
    
    if selected_country != "All Countries":
        filtered_suppliers = filtered_suppliers[filtered_suppliers["Country"] == selected_country]
    
    # Get latest performance scores
    latest_quarter = performance_data["Quarter"].max()
    latest_performance = performance_data[performance_data["Quarter"] == latest_quarter]
    
    # Merge supplier and performance data
    supplier_performance = filtered_suppliers.merge(
        latest_performance[["SupplierID", "OverallScore", "DeliveryScore", "QualityScore", "ResponsivenessScore"]],
        on="SupplierID",
        how="left"
    )
    
    # Apply performance score filter
    min_score, max_score = score_range
    supplier_performance = supplier_performance[
        (supplier_performance["OverallScore"] >= min_score) &
        (supplier_performance["OverallScore"] <= max_score)
    ]
    
    # Main content area
    if len(supplier_performance) == 0:
        st.warning("No suppliers match the selected filters.")
    else:
        # Supplier Performance Dashboard
        st.subheader("Supplier Performance Dashboard")
        
        performance_metrics = st.tabs(["Overall Performance", "Delivery", "Quality", "Responsiveness"])
        
        with performance_metrics[0]:
            fig1 = create_supplier_chart(latest_performance, filtered_suppliers, metric="OverallScore")
            st.plotly_chart(fig1, use_container_width=True)
        
        with performance_metrics[1]:
            fig2 = create_supplier_chart(latest_performance, filtered_suppliers, metric="DeliveryScore")
            st.plotly_chart(fig2, use_container_width=True)
        
        with performance_metrics[2]:
            fig3 = create_supplier_chart(latest_performance, filtered_suppliers, metric="QualityScore")
            st.plotly_chart(fig3, use_container_width=True)
        
        with performance_metrics[3]:
            fig4 = create_supplier_chart(latest_performance, filtered_suppliers, metric="ResponsivenessScore")
            st.plotly_chart(fig4, use_container_width=True)
        
        # Performance Trend Analysis
        st.subheader("Performance Trend Analysis")
        
        # Supplier selector for trend analysis
        selected_supplier_id = st.selectbox(
            "Select Supplier for Trend Analysis:",
            options=supplier_performance["SupplierID"].tolist(),
            format_func=lambda x: supplier_performance[supplier_performance["SupplierID"] == x]["SupplierName"].iloc[0]
        )
        
        # Get performance history for selected supplier
        supplier_history = performance_data[performance_data["SupplierID"] == selected_supplier_id]
        
        if len(supplier_history) > 0:
            # Create a long format dataframe for the line chart
            metrics = ["OverallScore", "DeliveryScore", "QualityScore", "ResponsivenessScore"]
            history_long = pd.melt(
                supplier_history,
                id_vars=["SupplierID", "Quarter"],
                value_vars=metrics,
                var_name="Metric",
                value_name="Score"
            )
            
            # Create a more readable label for the metrics
            history_long["Metric"] = history_long["Metric"].replace({
                "OverallScore": "Overall",
                "DeliveryScore": "Delivery",
                "QualityScore": "Quality",
                "ResponsivenessScore": "Responsiveness"
            })
            
            # Create the trend chart
            fig5 = px.line(
                history_long,
                x="Quarter",
                y="Score",
                color="Metric",
                title=f"Performance Trend for {supplier_performance[supplier_performance['SupplierID'] == selected_supplier_id]['SupplierName'].iloc[0]}",
                labels={"Score": "Performance Score (1-10)", "Quarter": "Quarter", "Metric": "Metric"},
                markers=True
            )
            
            fig5.update_layout(
                yaxis=dict(range=[0, 10.5]),
                hovermode="x unified"
            )
            
            st.plotly_chart(fig5, use_container_width=True)
            
            # Display latest comments for the selected supplier
            latest_comment = supplier_history[supplier_history["Quarter"] == latest_quarter]["Comments"].iloc[0]
            st.info(f"**Latest Performance Assessment:** {latest_comment}")
        else:
            st.warning("No performance history available for the selected supplier.")
        
        # Public Risk Indicators
        st.subheader("Public Risk Indicators (Simulated)")
        
        # Create simulated risk indicators
        supplier_performance["FinancialRisk"] = np.random.uniform(1, 10, len(supplier_performance))
        supplier_performance["ESGRisk"] = np.random.uniform(1, 10, len(supplier_performance))
        supplier_performance["ComplianceRisk"] = np.random.uniform(1, 10, len(supplier_performance))
        supplier_performance["GeopoliticalRisk"] = np.random.uniform(1, 10, len(supplier_performance))
        
        # Create a risk score (lower is better for risk scores)
        supplier_performance["RiskScore"] = (
            supplier_performance["FinancialRisk"] * 0.4 +
            supplier_performance["ESGRisk"] * 0.3 +
            supplier_performance["ComplianceRisk"] * 0.2 +
            supplier_performance["GeopoliticalRisk"] * 0.1
        )
        
        # Create two columns layout
        risk_col1, risk_col2 = st.columns(2)
        
        with risk_col1:
            # Create a scatter plot of performance vs risk
            fig6 = px.scatter(
                supplier_performance,
                x="RiskScore",
                y="OverallScore",
                color="Category",
                size="AnnualRevenue",
                hover_name="SupplierName",
                title="Supplier Performance vs. Risk Matrix",
                labels={
                    "RiskScore": "Risk Score (Lower is Better)",
                    "OverallScore": "Performance Score (Higher is Better)",
                    "Category": "Category"
                },
                custom_data=["SupplierID", "SupplierName"]
            )
            
            # Add quadrant lines
            fig6.add_hline(y=7.5, line_width=1, line_dash="dash", line_color="gray")
            fig6.add_vline(x=5, line_width=1, line_dash="dash", line_color="gray")
            
            # Add quadrant annotations
            fig6.add_annotation(x=2.5, y=8.75, text="Strategic Partners", showarrow=False, font=dict(size=12, color="green"))
            fig6.add_annotation(x=7.5, y=8.75, text="Performance Concerns", showarrow=False, font=dict(size=12, color="orange"))
            fig6.add_annotation(x=2.5, y=3.75, text="Reliable", showarrow=False, font=dict(size=12, color="blue"))
            fig6.add_annotation(x=7.5, y=3.75, text="High Risk", showarrow=False, font=dict(size=12, color="red"))
            
            st.plotly_chart(fig6, use_container_width=True)
        
        with risk_col2:
            # Top 10 suppliers by risk
            high_risk_suppliers = supplier_performance.sort_values("RiskScore", ascending=False).head(10)
            
            fig7 = px.bar(
                high_risk_suppliers,
                y="SupplierName",
                x="RiskScore",
                orientation="h",
                color="RiskScore",
                title="Top 10 Suppliers by Risk Score",
                labels={"SupplierName": "Supplier", "RiskScore": "Risk Score"},
                color_continuous_scale="Oranges_r"  # Reversed scale since higher risk is worse
            )
            
            fig7.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig7, use_container_width=True)
        
        # Detailed Risk Profile for a selected supplier
        st.subheader("Detailed Risk Profile")
        
        selected_supplier_id_risk = st.selectbox(
            "Select Supplier for Detailed Risk Analysis:",
            options=supplier_performance["SupplierID"].tolist(),
            format_func=lambda x: supplier_performance[supplier_performance["SupplierID"] == x]["SupplierName"].iloc[0],
            key="risk_supplier_selector"
        )
        
        # Get the selected supplier data
        selected_supplier = supplier_performance[supplier_performance["SupplierID"] == selected_supplier_id_risk].iloc[0]
        
        # Create columns for risk profile
        profile_col1, profile_col2 = st.columns(2)
        
        with profile_col1:
            # Create a radar chart for risk dimensions
            risk_dimensions = ["FinancialRisk", "ESGRisk", "ComplianceRisk", "GeopoliticalRisk"]
            risk_values = [selected_supplier[dim] for dim in risk_dimensions]
            
            fig8 = go.Figure()
            
            fig8.add_trace(go.Scatterpolar(
                r=risk_values,
                theta=["Financial", "ESG", "Compliance", "Geopolitical"],
                fill='toself',
                name='Risk Profile',
                line_color='orange'
            ))
            
            fig8.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                    )),
                showlegend=False,
                title=f"Risk Profile for {selected_supplier['SupplierName']}"
            )
            
            st.plotly_chart(fig8, use_container_width=True)
        
        with profile_col2:
            # Create a gauge chart for overall risk
            risk_score = selected_supplier["RiskScore"]
            
            fig9 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=risk_score,
                title={"text": "Overall Risk Score"},
                gauge={
                    'axis': {'range': [0, 10], 'tickwidth': 1},
                    'bar': {'color': "orange"},
                    'steps': [
                        {'range': [0, 3.33], 'color': "green"},
                        {'range': [3.33, 6.66], 'color': "yellow"},
                        {'range': [6.66, 10], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': risk_score
                    }
                }
            ))
            
            st.plotly_chart(fig9, use_container_width=True)
        
        # Risk alerts and recommendations
        st.subheader("Risk Alerts & Recommendations")
        
        # Simulated risk alerts based on the selected supplier
        alerts = []
        
        if selected_supplier["FinancialRisk"] > 7:
            alerts.append({
                "type": "Financial",
                "severity": "High",
                "description": f"Financial stability concerns detected for {selected_supplier['SupplierName']}.",
                "recommendation": "Consider requiring financial guarantees or adjusting payment terms."
            })
        
        if selected_supplier["ESGRisk"] > 7:
            alerts.append({
                "type": "ESG",
                "severity": "High",
                "description": f"Environmental or social compliance issues identified for {selected_supplier['SupplierName']}.",
                "recommendation": "Request ESG compliance documentation and schedule an audit."
            })
        
        if selected_supplier["DeliveryScore"] < 6:
            alerts.append({
                "type": "Performance",
                "severity": "Medium",
                "description": f"Consistent delivery issues with {selected_supplier['SupplierName']}.",
                "recommendation": "Implement a performance improvement plan with monthly reviews."
            })
        
        if len(alerts) == 0:
            st.success(f"No significant risk alerts for {selected_supplier['SupplierName']}.")
        else:
            for alert in alerts:
                severity_color = "red" if alert["severity"] == "High" else ("orange" if alert["severity"] == "Medium" else "blue")
                st.warning(
                    f"**{alert['type']} Risk - {alert['severity']} Severity**\n\n"
                    f"{alert['description']}\n\n"
                    f"**Recommendation:** {alert['recommendation']}"
                )
        
        # AI-Powered Supplier Risk Analysis
        st.subheader("AI-Powered Supplier Risk Analysis")
        
        # Check if LLM is configured
        llm_provider = st.session_state.get("llm_provider", "None")
        use_llm = llm_provider != "None"
        
        if not use_llm:
            st.info("Enable AI model configuration in the sidebar to get enhanced supplier risk analysis")
        else:
            with st.spinner("Generating advanced risk insights..."):
                # Get the supplier insights using LLM
                supplier_insights = generate_supplier_insights(
                    selected_supplier_id_risk, 
                    supplier_data, 
                    performance_data, 
                    spend_data, 
                    use_llm=True
                )
                
                # Display the AI-generated insights
                st.markdown(supplier_insights)
                
                # Ask user if they want to generate a risk mitigation plan
                if st.button("Generate Risk Mitigation Plan", key="gen_risk_plan"):
                    with st.spinner("Generating comprehensive risk mitigation plan..."):
                        # This would call an additional LLM function to generate a risk plan
                        st.success("Risk mitigation plan functionality will be implemented in the next update")
                        st.info("This feature would generate a detailed risk mitigation plan using AI analysis of the supplier's risk profile")
