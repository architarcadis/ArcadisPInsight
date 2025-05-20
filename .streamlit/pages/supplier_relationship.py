import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def show(session_state):
    """Display the Supplier Relationship Management tab content"""
    st.title("🤝 Supplier Relationship Management")
    
    # Get data from session state
    supplier_data = session_state.supplier_data
    performance_data = session_state.performance_data
    spend_data = session_state.spend_data
    contract_data = session_state.contract_data
    
    # Supplier selector
    st.subheader("Supplier 360° View")
    
    # Dropdown to select supplier
    selected_supplier_id = st.selectbox(
        "Select Supplier:",
        options=supplier_data["SupplierID"].tolist(),
        format_func=lambda x: supplier_data[supplier_data["SupplierID"] == x]["SupplierName"].iloc[0]
    )
    
    # Get supplier details
    supplier_details = supplier_data[supplier_data["SupplierID"] == selected_supplier_id].iloc[0]
    
    # Create columns for supplier details and metrics
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"### {supplier_details['SupplierName']}")
        st.markdown(f"**Category:** {supplier_details['Category']}")
        st.markdown(f"**Location:** {supplier_details['City']}, {supplier_details['Country']}")
        st.markdown(f"**Contact:** {supplier_details['ContactName']}")
        st.markdown(f"**Email:** {supplier_details['ContactEmail']}")
        st.markdown(f"**Phone:** {supplier_details['ContactPhone']}")
        st.markdown(f"**Relationship Since:** {supplier_details['RelationshipStartDate']}")
    
    with col2:
        # Calculate supplier metrics
        
        # 1. Performance metrics
        latest_quarter = performance_data["Quarter"].max()
        latest_performance = performance_data[
            (performance_data["SupplierID"] == selected_supplier_id) & 
            (performance_data["Quarter"] == latest_quarter)
        ]
        
        if len(latest_performance) > 0:
            overall_score = latest_performance["OverallScore"].iloc[0]
            delivery_score = latest_performance["DeliveryScore"].iloc[0]
            quality_score = latest_performance["QualityScore"].iloc[0]
            responsiveness_score = latest_performance["ResponsivenessScore"].iloc[0]
        else:
            overall_score = delivery_score = quality_score = responsiveness_score = "N/A"
        
        # 2. Spend metrics
        supplier_spend = spend_data[spend_data["Supplier"] == supplier_details["SupplierName"]]
        total_spend = supplier_spend["Amount"].sum() if len(supplier_spend) > 0 else 0
        
        # 3. Contract metrics
        supplier_contracts = contract_data[contract_data["SupplierID"] == selected_supplier_id]
        active_contracts = len(supplier_contracts[supplier_contracts["Status"] == "Active"])
        
        # Create metric columns
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            st.metric("Overall Score", 
                      f"{overall_score}/10" if isinstance(overall_score, (int, float)) else overall_score)
        
        with metric_col2:
            # Format with appropriate width to prevent truncation
            st.metric("Total Spend", f"${total_spend:,.2f}", help=f"Total spend with this supplier: ${total_spend:,.2f}")
        
        with metric_col3:
            st.metric("Active Contracts", active_contracts)
        
        with metric_col4:
            # Determine if this is a key supplier based on spend percentile
            if len(supplier_spend) > 0:
                spend_percentile = (spend_data.groupby("Supplier")["Amount"].sum() <= total_spend).mean() * 100
                tier = "Strategic" if spend_percentile >= 80 else ("Key" if spend_percentile >= 50 else "Standard")
            else:
                tier = "Unknown"
            
            st.metric("Supplier Tier", tier)
    
    # Performance scores chart
    if isinstance(overall_score, (int, float)):
        # Create a bullet chart for performance metrics
        fig1 = go.Figure()
        
        # Add performance metrics as bullet charts
        metrics = [
            {"name": "Overall", "score": overall_score},
            {"name": "Delivery", "score": delivery_score},
            {"name": "Quality", "score": quality_score},
            {"name": "Responsiveness", "score": responsiveness_score}
        ]
        
        for i, metric in enumerate(metrics):
            fig1.add_trace(go.Indicator(
                mode="number+gauge",
                value=metric["score"],
                domain={'x': [0, 1], 'y': [i/len(metrics), (i+0.8)/len(metrics)]},
                title={'text': metric["name"]},
                gauge={
                    'shape': "bullet",
                    'axis': {'range': [0, 10]},
                    'threshold': {
                        'line': {'color': "red", 'width': 2},
                        'thickness': 0.75,
                        'value': 7
                    },
                    'steps': [
                        {'range': [0, 5], 'color': "lightgray"},
                        {'range': [5, 7], 'color': "gray"}
                    ],
                    'bar': {'color': "orange"}
                }
            ))
        
        fig1.update_layout(
            height=250,
            margin=dict(l=100, r=10, t=10, b=10)
        )
        
        st.plotly_chart(fig1, use_container_width=True, key="performance_score_chart")
    
    # Create tabs for detailed information
    tab1, tab2, tab3, tab4 = st.tabs(["Performance Trend", "Spend Analysis", "Contracts", "Relationship Notes"])
    
    # Performance Trend Tab
    with tab1:
        # Get performance history for the selected supplier
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
            fig2 = px.line(
                history_long,
                x="Quarter",
                y="Score",
                color="Metric",
                title=f"Performance Trend for {supplier_details['SupplierName']}",
                labels={"Score": "Performance Score (1-10)", "Quarter": "Quarter", "Metric": "Metric"},
                markers=True
            )
            
            fig2.update_layout(
                yaxis=dict(range=[0, 10.5]),
                hovermode="x unified"
            )
            
            st.plotly_chart(fig2, use_container_width=True, key="perf_trend_chart")
            
            # Display comments in a timeline
            st.subheader("Performance Assessment Timeline")
            
            supplier_history_sorted = supplier_history.sort_values("Quarter", ascending=False)
            for _, row in supplier_history_sorted.iterrows():
                st.markdown(f"**{row['Quarter']}:** {row['Comments']} (Score: {row['OverallScore']}/10)")
        else:
            st.warning("No performance history available for this supplier.")
    
    # Spend Analysis Tab
    with tab2:
        # Filter spend data for the selected supplier
        supplier_spend = spend_data[spend_data["Supplier"] == supplier_details["SupplierName"]]
        
        if len(supplier_spend) > 0:
            # Calculate total spend
            total_spend = supplier_spend["Amount"].sum()
            
            # Create columns for metrics
            spend_col1, spend_col2 = st.columns(2)
            
            with spend_col1:
                # Spend by category
                spend_by_category = supplier_spend.groupby("Category")["Amount"].sum().reset_index()
                spend_by_category = spend_by_category.sort_values("Amount", ascending=False)
                
                fig3 = px.pie(
                    spend_by_category,
                    values="Amount",
                    names="Category",
                    title=f"Spend by Category with {supplier_details['SupplierName']}",
                    color_discrete_sequence=px.colors.sequential.Oranges
                )
                
                st.plotly_chart(fig3, use_container_width=True, key="spend_category_chart")
            
            with spend_col2:
                # Spend trend over time
                supplier_spend["Month"] = pd.to_datetime(supplier_spend["Date"]).dt.strftime('%Y-%m')
                spend_by_month = supplier_spend.groupby("Month")["Amount"].sum().reset_index()
                
                fig4 = px.line(
                    spend_by_month,
                    x="Month",
                    y="Amount",
                    title=f"Spend Trend with {supplier_details['SupplierName']}",
                    labels={"Amount": "Spend Amount ($)", "Month": "Month"},
                    markers=True
                )
                
                st.plotly_chart(fig4, use_container_width=True, key="spend_trend_chart")
            
            # Spend by business unit
            spend_by_bu = supplier_spend.groupby("BusinessUnit")["Amount"].sum().reset_index()
            spend_by_bu = spend_by_bu.sort_values("Amount", ascending=False)
            
            fig5 = px.bar(
                spend_by_bu,
                x="BusinessUnit",
                y="Amount",
                title=f"Spend by Business Unit with {supplier_details['SupplierName']}",
                labels={"Amount": "Spend Amount ($)", "BusinessUnit": "Business Unit"},
                color="Amount",
                color_continuous_scale="Oranges"
            )
            
            st.plotly_chart(fig5, use_container_width=True, key="spend_by_bu_chart")
            
            # Invoice table
            st.subheader("Recent Transactions")
            
            recent_transactions = supplier_spend.sort_values("Date", ascending=False).head(10)
            st.dataframe(
                recent_transactions[["Date", "InvoiceID", "POID", "Category", "Amount", "BusinessUnit"]],
                hide_index=True
            )
        else:
            st.warning("No spend data available for this supplier.")
    
    # Contracts Tab
    with tab3:
        # Filter contract data for the selected supplier
        supplier_contracts = contract_data[contract_data["SupplierID"] == selected_supplier_id]
        
        if len(supplier_contracts) > 0:
            # Contract metrics
            active_contracts = supplier_contracts[supplier_contracts["Status"] == "Active"]
            expiring_soon = []
            renewal_alert = []
            
            current_date = datetime.now()
            
            for _, contract in active_contracts.iterrows():
                end_date = datetime.strptime(contract["EndDate"], "%Y-%m-%d")
                days_until_expiry = (end_date - current_date).days
                
                if days_until_expiry <= 90:  # Within 90 days
                    expiring_soon.append({
                        "ContractID": contract["ContractID"],
                        "Type": contract["ContractType"],
                        "EndDate": contract["EndDate"],
                        "DaysRemaining": days_until_expiry,
                        "Value": contract["Value"]
                    })
                
                if contract["AutoRenewal"] and days_until_expiry <= contract["NoticePeriodDays"]:
                    renewal_alert.append({
                        "ContractID": contract["ContractID"],
                        "Type": contract["ContractType"],
                        "NoticePeriodDays": contract["NoticePeriodDays"],
                        "DaysRemaining": days_until_expiry,
                        "EndDate": contract["EndDate"]
                    })
            
            # Display contract alerts
            if len(expiring_soon) > 0 or len(renewal_alert) > 0:
                st.subheader("Contract Alerts")
                
                alert_col1, alert_col2 = st.columns(2)
                
                with alert_col1:
                    if len(expiring_soon) > 0:
                        st.warning(
                            f"**{len(expiring_soon)} contract(s) expiring soon**\n\n" +
                            "\n".join([f"Contract {c['ContractID']} ({c['Type']}) - {c['DaysRemaining']} days remaining (${c['Value']:,.2f})" 
                                      for c in expiring_soon])
                        )
                
                with alert_col2:
                    if len(renewal_alert) > 0:
                        st.error(
                            f"**{len(renewal_alert)} contract(s) approaching auto-renewal**\n\n" +
                            "\n".join([f"Contract {c['ContractID']} - Notice period ({c['NoticePeriodDays']} days) starts now" 
                                      for c in renewal_alert])
                        )
            
            # Contract timeline
            st.subheader("Contract Timeline")
            
            # Convert date strings to datetime
            timeline_data = []
            
            for _, contract in supplier_contracts.iterrows():
                start_date = datetime.strptime(contract["StartDate"], "%Y-%m-%d")
                end_date = datetime.strptime(contract["EndDate"], "%Y-%m-%d")
                
                timeline_data.append({
                    "ContractID": contract["ContractID"],
                    "Task": contract["ContractType"],
                    "Start": start_date,
                    "Finish": end_date,
                    "Status": contract["Status"],
                    "Value": contract["Value"]
                })
            
            timeline_df = pd.DataFrame(timeline_data)
            
            # Create a Gantt chart
            fig6 = px.timeline(
                timeline_df,
                x_start="Start",
                x_end="Finish",
                y="ContractID",
                color="Status",
                hover_data=["Task", "Value"],
                labels={"ContractID": "Contract", "Task": "Type"},
                title="Contract Timeline",
                color_discrete_map={"Active": "green", "Expired": "gray", "Future": "blue"}
            )
            
            # Add current date line
            # Instead of using vline, let's add a shape for the current date line
            fig6.update_layout(
                shapes=[
                    dict(
                        type='line',
                        yref='paper',
                        x0=current_date.strftime('%Y-%m-%d'),
                        y0=0,
                        x1=current_date.strftime('%Y-%m-%d'),
                        y1=1,
                        line=dict(color='red', width=2, dash='dash')
                    )
                ],
                annotations=[
                    dict(
                        x=current_date.strftime('%Y-%m-%d'),
                        y=1.05,
                        xref='x',
                        yref='paper',
                        text='Today',
                        showarrow=False,
                        font=dict(color='red')
                    )
                ]
            )
            
            fig6.update_yaxes(autorange="reversed")
            
            st.plotly_chart(fig6, use_container_width=True, key="contract_timeline_chart")
            
            # Contract details table
            st.subheader("Contract Details")
            
            # Sort contracts by status and end date
            sorted_contracts = supplier_contracts.sort_values(
                ["Status", "EndDate"],
                ascending=[True, True]
            )
            
            contract_display = sorted_contracts[[
                "ContractID", "ContractType", "StartDate", "EndDate", 
                "Value", "Status", "AutoRenewal", "NoticePeriodDays"
            ]]
            
            st.dataframe(contract_display, hide_index=True)
        else:
            st.warning("No contract data available for this supplier.")
    
    # Relationship Notes Tab (Simulated)
    with tab4:
        st.subheader("Relationship Notes & Activities")
        
        # Simulated relationship notes
        notes = [
            {
                "date": "2023-05-01",
                "type": "Meeting",
                "title": "Quarterly Business Review",
                "content": "Met with supplier's account team to review Q1 performance. Discussed delivery issues with Project XYZ and agreed on corrective actions.",
                "author": "John Smith"
            },
            {
                "date": "2023-03-15",
                "type": "Contract",
                "title": "Contract Amendment Signed",
                "content": "Amendment to add new services to existing MSA. Increased contract value by $50,000.",
                "author": "Jane Doe"
            },
            {
                "date": "2023-02-10",
                "type": "Issue",
                "title": "Delivery Delay",
                "content": "Supplier notified of 2-week delay for Project XYZ deliverables. Impact analysis conducted.",
                "author": "Robert Johnson"
            },
            {
                "date": "2023-01-05",
                "type": "Meeting",
                "title": "Annual Strategic Planning",
                "content": "Annual planning meeting to discuss 2023 roadmap and strategic initiatives. Identified opportunities for cost savings.",
                "author": "John Smith"
            }
        ]
        
        # Display notes in a timeline
        for note in notes:
            with st.expander(f"{note['date']} | {note['type']}: {note['title']}"):
                st.markdown(f"**{note['title']}**")
                st.markdown(note['content'])
                st.markdown(f"*Author: {note['author']}*")
        
        # Add new note form
        st.subheader("Add New Note")
        
        note_col1, note_col2 = st.columns(2)
        
        with note_col1:
            note_type = st.selectbox("Note Type:", ["Meeting", "Contract", "Issue", "Other"])
        
        with note_col2:
            note_title = st.text_input("Title:")
        
        note_content = st.text_area("Content:")
        
        if st.button("Save Note"):
            st.success("Note saved successfully! (This is a simulation)")
    
    # Supplier Segmentation Overview
    st.subheader("Supplier Segmentation Overview")
    
    # Get all supplier data with performance and spend information
    latest_quarter = performance_data["Quarter"].max()
    latest_performance = performance_data[performance_data["Quarter"] == latest_quarter]
    
    # Prepare data for segmentation
    segmentation_data = []
    
    for _, supplier in supplier_data.iterrows():
        # Get performance data
        perf = latest_performance[latest_performance["SupplierID"] == supplier["SupplierID"]]
        performance_score = perf["OverallScore"].iloc[0] if len(perf) > 0 else 5.0  # Default if no data
        
        # Get spend data
        supplier_name = supplier["SupplierName"]
        spend = spend_data[spend_data["Supplier"] == supplier_name]
        total_spend = spend["Amount"].sum() if len(spend) > 0 else 0
        
        # Calculate spend percentile (higher percentile = higher relative spend)
        all_suppliers_spend = spend_data.groupby("Supplier")["Amount"].sum()
        spend_percentile = (all_suppliers_spend <= total_spend).mean() * 100 if total_spend > 0 else 0
        
        # Add to segmentation data
        segmentation_data.append({
            "SupplierID": supplier["SupplierID"],
            "SupplierName": supplier_name,
            "Category": supplier["Category"],
            "PerformanceScore": performance_score,
            "TotalSpend": total_spend,
            "SpendPercentile": spend_percentile,
            "IsSelected": supplier["SupplierID"] == selected_supplier_id
        })
    
    segmentation_df = pd.DataFrame(segmentation_data)
    
    # Create segmentation quadrant chart
    fig7 = px.scatter(
        segmentation_df,
        x="SpendPercentile",
        y="PerformanceScore",
        color="Category",
        size="TotalSpend",
        hover_name="SupplierName",
        title="Supplier Segmentation Matrix",
        labels={
            "SpendPercentile": "Spend (Percentile)",
            "PerformanceScore": "Performance Score (1-10)"
        },
        size_max=25,
        opacity=0.7
    )
    
    # Highlight the selected supplier
    selected_supplier_data = segmentation_df[segmentation_df["IsSelected"]]
    
    if len(selected_supplier_data) > 0:
        x = selected_supplier_data["SpendPercentile"].iloc[0]
        y = selected_supplier_data["PerformanceScore"].iloc[0]
        
        fig7.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode="markers",
            marker=dict(
                size=16,
                color="rgba(0,0,0,0)",
                line=dict(
                    color="black",
                    width=2
                )
            ),
            showlegend=False,
            hoverinfo="skip"
        ))
    
    # Add quadrant lines
    fig7.add_hline(y=7.5, line_width=1, line_dash="dash", line_color="gray")
    fig7.add_vline(x=60, line_width=1, line_dash="dash", line_color="gray")
    
    # Add quadrant annotations
    fig7.add_annotation(x=80, y=8.75, text="Strategic", showarrow=False, font=dict(size=12, color="green"))
    fig7.add_annotation(x=30, y=8.75, text="Potential", showarrow=False, font=dict(size=12, color="blue"))
    fig7.add_annotation(x=80, y=3.75, text="Problematic", showarrow=False, font=dict(size=12, color="red"))
    fig7.add_annotation(x=30, y=3.75, text="Transactional", showarrow=False, font=dict(size=12, color="gray"))
    
    st.plotly_chart(fig7, use_container_width=True)
