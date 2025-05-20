import streamlit as st
import pandas as pd
import hashlib
import json
from utils.llm_integration import analyze_text_with_llm

def generate_category_insights(category, spend_data, use_llm=False):
    """
    Generate insights for a specific procurement category
    
    Parameters:
    category: The category to analyze
    spend_data: DataFrame containing spend data
    use_llm: Whether to use LLM for enhanced insights
    
    Returns:
    str: Generated insights
    """
    if category == "All Categories":
        filtered_data = spend_data
    else:
        filtered_data = spend_data[spend_data["Category"] == category]
    
    if len(filtered_data) == 0:
        return "No data available for the selected category."
    
    # Basic statistical insights
    total_spend = filtered_data["Amount"].sum()
    avg_transaction = filtered_data["Amount"].mean()
    transaction_count = len(filtered_data)
    supplier_count = filtered_data["Supplier"].nunique()
    
    # Top suppliers for this category
    top_suppliers = filtered_data.groupby("Supplier")["Amount"].sum().sort_values(ascending=False).head(3)
    top_supplier_names = top_suppliers.index.tolist()
    top_supplier_amounts = top_suppliers.values.tolist()
    
    # Spend over time
    filtered_data["Month"] = pd.to_datetime(filtered_data["Date"]).dt.strftime('%Y-%m')
    spend_trend = filtered_data.groupby("Month")["Amount"].sum().reset_index()
    
    # Generate basic insights without LLM
    basic_insights = f"""
    ### {category} Summary
    
    **Total Spend**: ${total_spend:,.2f}
    **Suppliers**: {supplier_count}
    **Transactions**: {transaction_count}
    **Average Transaction**: ${avg_transaction:,.2f}
    
    **Top Suppliers**:
    """
    
    for i, (supplier, amount) in enumerate(zip(top_supplier_names, top_supplier_amounts)):
        basic_insights += f"- {supplier}: ${amount:,.2f}\n"
    
    # Check for spend trend patterns
    if len(spend_trend) > 1:
        first_month = spend_trend.iloc[0]["Amount"]
        last_month = spend_trend.iloc[-1]["Amount"]
        
        if last_month > first_month:
            change_pct = (last_month - first_month) / first_month * 100
            basic_insights += f"\n**Spend Trend**: Increasing by approximately {change_pct:.1f}% from first to last period\n"
        else:
            change_pct = (first_month - last_month) / first_month * 100
            basic_insights += f"\n**Spend Trend**: Decreasing by approximately {change_pct:.1f}% from first to last period\n"
    
    # If LLM is not enabled, return basic insights
    if not use_llm:
        return basic_insights
    
    # Use LLM for enhanced insights if available
    # Prepare data summary for LLM
    data_summary = {
        "category": category,
        "total_spend": total_spend,
        "avg_transaction": avg_transaction,
        "transaction_count": transaction_count,
        "supplier_count": supplier_count,
        "top_suppliers": [{"name": name, "amount": amount} for name, amount in zip(top_supplier_names, top_supplier_amounts)],
        "spend_trend": [{"month": row["Month"], "amount": row["Amount"]} for _, row in spend_trend.iterrows()]
    }
    
    # Generate cache key based on data
    cache_key = hashlib.md5(json.dumps(data_summary, default=str).encode()).hexdigest()
    
    # LLM prompt template
    prompt_template = """
    As a procurement analytics expert, analyze the following category data and provide strategic insights:
    
    Category: {text}
    
    Please provide:
    1. Key observations about spending patterns
    2. Potential cost-saving opportunities
    3. Supplier consolidation recommendations
    4. Market trend implications
    5. Strategic procurement recommendations
    
    Keep your analysis concise (maximum 300 words) and focus on actionable insights.
    """
    
    # Call LLM for analysis
    llm_insights = analyze_text_with_llm(json.dumps(data_summary), prompt_template, cache_key)
    
    # Combine basic insights with LLM analysis
    combined_insights = basic_insights + "\n\n### AI-Powered Strategic Analysis\n\n" + llm_insights
    return combined_insights

def generate_supplier_insights(supplier_id, supplier_data, performance_data, spend_data, use_llm=False):
    """
    Generate insights for a specific supplier
    
    Parameters:
    supplier_id: The ID of the supplier to analyze
    supplier_data: DataFrame containing supplier master data
    performance_data: DataFrame containing supplier performance data
    spend_data: DataFrame containing spend data
    use_llm: Whether to use LLM for enhanced insights
    
    Returns:
    str: Generated insights
    """
    # Get supplier details
    supplier_info = supplier_data[supplier_data["SupplierID"] == supplier_id].iloc[0]
    supplier_name = supplier_info["SupplierName"]
    
    # Get performance data
    supplier_perf = performance_data[performance_data["SupplierID"] == supplier_id]
    
    # Get spend data for this supplier
    supplier_spend = spend_data[spend_data["Supplier"] == supplier_name]
    
    # Basic insights without LLM
    basic_insights = f"""
    ### {supplier_name} Summary
    
    **Location**: {supplier_info['City']}, {supplier_info['Country']}
    **Category**: {supplier_info['Category']}
    **Relationship Started**: {supplier_info['RelationshipStartDate']}
    """
    
    # Add performance metrics if available
    latest_quarter = None
    latest_perf = None
    
    if len(supplier_perf) > 0:
        basic_insights += "\n**Performance Metrics (Latest)**:\n"
        latest_quarter = supplier_perf["Quarter"].max()
        latest_perf = supplier_perf[supplier_perf["Quarter"] == latest_quarter].iloc[0]
        
        basic_insights += f"""
        - Overall Score: {latest_perf['OverallScore']}/10
        - Delivery Score: {latest_perf['DeliveryScore']}/10
        - Quality Score: {latest_perf['QualityScore']}/10
        - Responsiveness Score: {latest_perf['ResponsivenessScore']}/10
        """
    else:
        basic_insights += "\n**Performance Metrics**: No performance data available.\n"
    
    # Add spend analysis if available
    if len(supplier_spend) > 0:
        total_spend = supplier_spend["Amount"].sum()
        transaction_count = len(supplier_spend)
        avg_transaction = total_spend / transaction_count if transaction_count > 0 else 0
        
        basic_insights += f"""
        **Spend Analysis**:
        - Total Spend: ${total_spend:,.2f}
        - Transactions: {transaction_count}
        - Average Transaction: ${avg_transaction:,.2f}
        """
    else:
        basic_insights += "\n**Spend Analysis**: No spend data available.\n"
    
    # If LLM is not enabled, return basic insights
    if not use_llm:
        return basic_insights
    
    # Use LLM for enhanced supplier insights
    # Prepare data summary for LLM
    data_summary = {
        "supplier": {
            "name": supplier_name,
            "location": f"{supplier_info['City']}, {supplier_info['Country']}",
            "category": supplier_info['Category'],
            "relationshipStarted": supplier_info['RelationshipStartDate']
        },
        "performance": {}
    }
    
    if len(supplier_perf) > 0:
        # Safely handle performance data
        try:
            history_data = [
                {
                    "quarter": str(row["Quarter"]),
                    "overallScore": float(row["OverallScore"])
                } for _, row in supplier_perf.sort_values("Quarter").iterrows()
            ]
            
            data_summary["performance"] = {
                "history": history_data
            }
            
            if latest_quarter is not None and latest_perf is not None:
                latest_data = {
                    "quarter": str(latest_quarter),
                    "overallScore": float(latest_perf['OverallScore']),
                    "deliveryScore": float(latest_perf['DeliveryScore']),
                    "qualityScore": float(latest_perf['QualityScore']),
                    "responsivenessScore": float(latest_perf['ResponsivenessScore'])
                }
                data_summary["performance"]["latest"] = latest_data
        except Exception as e:
            data_summary["performance"] = {"error": str(e)}
            pass
    
    if len(supplier_spend) > 0:
        supplier_spend["Month"] = pd.to_datetime(supplier_spend["Date"]).dt.strftime('%Y-%m')
        spend_by_month = supplier_spend.groupby("Month")["Amount"].sum().reset_index()
        
        total_spend_val = supplier_spend["Amount"].sum()
        transactions_count = len(supplier_spend)
        avg_transaction = total_spend_val / transactions_count if transactions_count > 0 else 0
        
        data_summary["spend"] = {
            "total": total_spend_val,
            "transactions": transactions_count,
            "average": avg_transaction,
            "trend": [
                {
                    "month": row["Month"],
                    "amount": row["Amount"]
                } for _, row in spend_by_month.iterrows()
            ]
        }
    
    # Generate cache key based on data
    cache_key = hashlib.md5(json.dumps(data_summary, default=str).encode()).hexdigest()
    
    # LLM prompt template
    prompt_template = """
    As a supplier relationship management expert, analyze the following supplier data and provide strategic insights:
    
    Supplier Data: {text}
    
    Please provide:
    1. Relationship health assessment
    2. Potential risk factors
    3. Optimization opportunities
    4. Recommended engagement strategy
    5. Action items for relationship improvement
    
    Keep your analysis concise (maximum 300 words) and focus on actionable recommendations.
    """
    
    # Call LLM for analysis
    llm_insights = analyze_text_with_llm(json.dumps(data_summary), prompt_template, cache_key)
    
    # Combine basic insights with LLM analysis
    combined_insights = basic_insights + "\n\n### AI-Powered Relationship Analysis\n\n" + llm_insights
    return combined_insights

def generate_market_insights(category, use_llm=False):
    """
    Generate market insights for a specific category
    
    Parameters:
    category: The category to analyze
    use_llm: Whether to use LLM for enhanced insights
    
    Returns:
    str: Generated insights
    """
    # Basic insights without LLM
    basic_insights = f"""
    ### {category} Market Insights
    
    **Note**: This section contains simulated market data for demonstration purposes.
    """
    
    # If LLM is not enabled, return basic insights
    if not use_llm:
        return basic_insights + "\n\nEnable AI analysis in the sidebar to get enhanced market insights."
    
    # Use LLM for market insights
    # Generate cache key based on category
    cache_key = hashlib.md5(f"market_insights_{category}".encode()).hexdigest()
    
    # LLM prompt template
    prompt_template = """
    As a procurement market intelligence expert, provide market insights for the following category:
    
    Category: {text}
    
    Please provide:
    1. Current market trends and conditions
    2. Supplier landscape overview
    3. Pricing trends and forecasts
    4. Supply chain risks and considerations
    5. Innovation and sustainability developments
    
    Keep your analysis realistic and fact-based, focusing on the current procurement market conditions. 
    Keep your insights concise (maximum 400 words) and focus on actionable intelligence.
    """
    
    # Call LLM for analysis
    llm_insights = analyze_text_with_llm(category, prompt_template, cache_key)
    
    # Combine basic insights with LLM analysis
    combined_insights = basic_insights + "\n\n### AI-Powered Market Intelligence\n\n" + llm_insights
    return combined_insights