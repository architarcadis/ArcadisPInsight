import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.visualizations import create_spend_chart, create_risk_heatmap
from utils.llm_analysis import generate_category_insights, generate_market_insights

def show(session_state):
    """Display the Category Intelligence tab content"""
    st.title("📊 Category Intelligence")
    
    # Get data from session state
    spend_data = session_state.spend_data
    
    # Filters section
    st.subheader("Filters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Category filter
        categories = ["All Categories"] + sorted(spend_data["Category"].unique().tolist())
        selected_category = st.selectbox("Select Category:", categories)
    
    with col2:
        # Business Unit filter
        business_units = ["All Business Units"] + sorted(spend_data["BusinessUnit"].unique().tolist())
        selected_bu = st.selectbox("Select Business Unit:", business_units)
    
    with col3:
        # Date range filter
        dates = pd.to_datetime(spend_data["Date"])
        min_date = dates.min().date()
        max_date = dates.max().date()
        date_range = st.date_input(
            "Select Date Range:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    
    # Apply filters to data
    filtered_data = spend_data.copy()
    
    if selected_category != "All Categories":
        filtered_data = filtered_data[filtered_data["Category"] == selected_category]
    
    if selected_bu != "All Business Units":
        filtered_data = filtered_data[filtered_data["BusinessUnit"] == selected_bu]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_data = filtered_data[
            (pd.to_datetime(filtered_data["Date"]).dt.date >= start_date) &
            (pd.to_datetime(filtered_data["Date"]).dt.date <= end_date)
        ]
    
    # Main content area
    if len(filtered_data) == 0:
        st.warning("No data available with the selected filters.")
    else:
        st.subheader("Spending Pattern & Opportunities")
        
        # Calculate key metrics
        total_spend = filtered_data["Amount"].sum()
        avg_transaction = filtered_data["Amount"].mean()
        transaction_count = len(filtered_data)
        supplier_count = filtered_data["Supplier"].nunique()
        
        # Add insight to metrics
        st.markdown(f"""
        *Understanding your spending profile provides the foundation for strategic sourcing decisions.*
        """)
        
        # Display metrics in columns
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        # Format metrics for better readability
        def format_currency(value):
            if value >= 1000000:
                return f"${value/1000000:.1f}M"
            elif value >= 1000:
                return f"${value/1000:.1f}K"
            else:
                return f"${value:.0f}"
                
        with metric_col1:
            st.metric("Total Spend", format_currency(total_spend))
            st.markdown(f"<div style='font-size:0.8em; color:#999'>Full amount: ${total_spend:,.2f}</div>", unsafe_allow_html=True)
        
        with metric_col2:
            st.metric("Suppliers", f"{supplier_count}")
            
        with metric_col3:
            st.metric("Transactions", f"{transaction_count:,}")
        
        with metric_col4:
            st.metric("Avg. Transaction", format_currency(avg_transaction))
            st.markdown(f"<div style='font-size:0.8em; color:#999'>Full amount: ${avg_transaction:,.2f}</div>", unsafe_allow_html=True)
            
        # Add opportunity insight based on metrics
        if supplier_count > 0 and transaction_count > 0:
            transactions_per_supplier = transaction_count / supplier_count
            if transactions_per_supplier < 5:
                st.info(f"⚠️ **Opportunity Alert**: Low transaction volume per supplier ({transactions_per_supplier:.1f}) suggests potential for supplier consolidation to improve efficiency and leverage.")
            elif supplier_count < 3 and total_spend > 500000:
                st.info(f"⚠️ **Risk Alert**: High spend concentration with only {supplier_count} suppliers may represent a supply risk. Consider supplier diversification strategy.")
            elif avg_transaction < 1000 and transaction_count > 100:
                st.info(f"⚠️ **Efficiency Alert**: High volume of small transactions (avg ${avg_transaction:.2f}) indicates opportunity to implement catalog purchasing or consolidate orders.")
        
        # Create charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Category spend chart with more insightful title
            if selected_category == "All Categories":
                dimension = "Category"
                title = "Where Your Money Goes: Spend Distribution by Category"
                subtitle = "Identify your highest-spend categories for strategic sourcing focus"
            else:
                dimension = "SubCategory"
                title = f"Breaking Down {selected_category}: Sub-Category Spend Distribution"
                subtitle = f"Identify key focus areas within {selected_category} for targeted savings initiatives"
            
            fig1 = create_spend_chart(filtered_data, dimension=dimension)
            fig1.update_layout(
                title={
                    'text': title,
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                }
            )
            st.plotly_chart(fig1, use_container_width=True)
            st.caption(subtitle)
        
        with chart_col2:
            # Top suppliers chart with added context and insight
            suppliers_df = filtered_data.groupby("Supplier")["Amount"].sum().reset_index()
            suppliers_df = suppliers_df.sort_values("Amount", ascending=False).head(10)
            
            # Calculate concentration metrics for insight
            total_category_spend = filtered_data["Amount"].sum()
            top3_spend = suppliers_df.head(3)["Amount"].sum() if len(suppliers_df) >= 3 else suppliers_df["Amount"].sum()
            top3_concentration = (top3_spend / total_category_spend * 100) if total_category_spend > 0 else 0
            
            supplier_title = "Supplier Concentration: Who Controls Your Spend"
            supplier_subtitle = f"Your top 3 suppliers represent {top3_concentration:.1f}% of total spend"
            
            fig2 = px.bar(
                suppliers_df,
                y="Supplier",
                x="Amount",
                orientation="h",
                title=supplier_title,
                labels={"Amount": "Spend Amount ($)", "Supplier": "Supplier"},
                color="Amount",
                color_continuous_scale="Oranges"
            )
            
            fig2.update_layout(
                yaxis={'categoryorder':'total ascending'},
                title={
                    'text': supplier_title,
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                }
            )
            st.plotly_chart(fig2, use_container_width=True)
            st.caption(supplier_subtitle)
            
            # Add actionable insight based on concentration
            if top3_concentration > 75:
                st.info("⚠️ **High supplier concentration detected.** While this offers potential leverage for negotiations, it also creates dependency risk. Consider developing alternative suppliers to mitigate supply chain risk.")
            elif top3_concentration < 30 and len(suppliers_df) > 7:
                st.info("💡 **Fragmented supplier base detected.** Your spending is dispersed across many suppliers, which may be increasing administrative costs and reducing buying power. Consider a supplier consolidation initiative.")
            elif 50 <= top3_concentration <= 75:
                st.success("✅ **Balanced supplier concentration.** Your current supplier mix provides good negotiating leverage while maintaining reasonable risk diversification.")
        
        # Spend over time analysis with enhanced storytelling
        st.subheader("Spending Patterns & Trends")
        st.markdown("*Identify seasonality, growth patterns, and spending anomalies to inform your procurement strategy*")
        
        # Convert dates to month periods for trend analysis
        filtered_data["Month"] = pd.to_datetime(filtered_data["Date"]).dt.strftime('%Y-%m')
        
        # Group by month and appropriate dimension
        group_dimension = "Supplier" if selected_category != "All Categories" else "Category"
        time_df = filtered_data.groupby(["Month", group_dimension])["Amount"].sum().reset_index()
        
        # Calculate trend statistics
        monthly_totals = filtered_data.groupby("Month")["Amount"].sum().reset_index()
        
        if len(monthly_totals) >= 3:
            first_month = monthly_totals.iloc[0]["Amount"] 
            last_month = monthly_totals.iloc[-1]["Amount"]
            change_pct = ((last_month - first_month) / first_month * 100) if first_month > 0 else 0
            
            # Create trend insight box
            if abs(change_pct) < 5:
                trend_color = "info"
                trend_message = f"📊 **Stable Spending Pattern**: Your spending has remained steady (±{abs(change_pct):.1f}%) over this period, suggesting consistent procurement activity."
            elif change_pct > 20:
                trend_color = "warning"
                trend_message = f"📈 **Significant Spending Growth**: Your spending has increased by {change_pct:.1f}% from first to last period. Investigate whether this reflects business growth or potential cost control issues."
            elif change_pct > 0:
                trend_color = "info"
                trend_message = f"📈 **Moderate Spending Growth**: Your spending has increased by {change_pct:.1f}% from first to last period, tracking slightly above inflation."
            elif change_pct < -20:
                trend_color = "success"
                trend_message = f"📉 **Major Spending Reduction**: Your spending has decreased by {abs(change_pct):.1f}% from first to last period. This significant reduction may reflect successful cost-saving initiatives."
            else:
                trend_color = "success"
                trend_message = f"📉 **Spending Reduction**: Your spending has decreased by {abs(change_pct):.1f}% from first to last period, which may indicate effective cost control measures."
            
            if trend_color == "info":
                st.info(trend_message)
            elif trend_color == "warning":
                st.warning(trend_message)
            else:
                st.success(trend_message)
        
        # Create the time series chart with enhanced title
        trend_title = f"Spending Evolution: How Your {selected_category if selected_category != 'All Categories' else 'Categories'} Spend Has Changed"
        
        fig3 = px.line(
            time_df,
            x="Month",
            y="Amount",
            color=group_dimension,
            title=trend_title,
            labels={"Amount": "Spend Amount ($)", "Month": "Month", group_dimension: group_dimension},
            markers=True
        )
        
        fig3.update_layout(
            title={
                'text': trend_title,
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )
        
        st.plotly_chart(fig3, use_container_width=True)
        
        # Add actionable context based on the data
        if len(time_df[group_dimension].unique()) > 5:
            st.caption("**Pro Tip**: Focus on the top 3-5 spending items for clearer trend analysis. Too many lines can obscure important patterns.")
        
        # Spend distribution heatmap with enhanced storytelling
        st.subheader("Spend Distribution Matrix")
        st.markdown("*Identify spending hotspots and blind spots across your organization*")
        
        # Determine dimensions for heatmap based on filters
        x_dimension = "Category" if selected_category == "All Categories" else "SubCategory"
        y_dimension = "BusinessUnit" if selected_bu == "All Business Units" else "Supplier"
        
        heatmap_title = ""
        if selected_category == "All Categories" and selected_bu == "All Business Units":
            heatmap_title = "Organizational Spending Heat Map: Which Categories and Business Units Drive Your Spend?"
            heatmap_subtitle = "Identify high-spend combinations that offer consolidation and strategic sourcing opportunities"
        elif selected_category != "All Categories" and selected_bu == "All Business Units":
            heatmap_title = f"{selected_category} Spending Across Business Units: Where Are Your Biggest Opportunities?"
            heatmap_subtitle = "Identify which business units have the highest spend in each sub-category"
        elif selected_category == "All Categories" and selected_bu != "All Business Units":
            heatmap_title = f"{selected_bu} Category Profile: Understanding Departmental Spending Patterns"
            heatmap_subtitle = "Identify which categories drive spending in this business unit"
        else:
            heatmap_title = f"{selected_category} Supplier Distribution for {selected_bu}: Who Gets Your Business?"
            heatmap_subtitle = "Identify supplier concentration within this category and business unit"
        
        # Create heatmap for the appropriate dimensions
        fig4 = create_risk_heatmap(
            filtered_data, 
            x_dim=x_dimension, 
            y_dim=y_dimension, 
            value="Amount"
        )
        
        # Update layout with better title
        fig4.update_layout(
            title={
                'text': heatmap_title,
                'y':0.97,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )
        
        st.plotly_chart(fig4, use_container_width=True, key="heatmap_chart")
        st.caption(heatmap_subtitle)
        
        # Add insight based on the heatmap data
        # Get the top combinations
        if len(filtered_data) > 0:
            combo_data = filtered_data.groupby([x_dimension, y_dimension])["Amount"].sum().reset_index()
            combo_data = combo_data.sort_values("Amount", ascending=False)
            
            if len(combo_data) > 0:
                top_combo = combo_data.iloc[0]
                top_combo_pct = (top_combo["Amount"] / filtered_data["Amount"].sum() * 100)
                
                if top_combo_pct > 25:
                    st.info(f"🔍 **Strategic Focus Opportunity**: The combination of {top_combo[x_dimension]} and {top_combo[y_dimension]} represents {top_combo_pct:.1f}% of your total filtered spend. This concentration suggests a high-impact opportunity for strategic sourcing and optimization.")
        
        # AI-Powered Insights Section
        st.subheader("AI-Powered Insights")
        
        # Check if LLM is configured
        llm_provider = st.session_state.get("llm_provider", "None")
        use_llm = llm_provider != "None"
        
        # Create columns for the insights
        insight_col1, insight_col2 = st.columns(2)
        
        with insight_col1:
            st.subheader("Category Insights")
            if not use_llm:
                st.info("Enable AI model configuration in the sidebar to get enhanced insights")
                st.markdown(generate_category_insights(selected_category, filtered_data, use_llm=False))
            else:
                with st.spinner("Generating category insights..."):
                    insights = generate_category_insights(selected_category, filtered_data, use_llm=True)
                    st.markdown(insights)
        
        with insight_col2:
            st.subheader("Market Intelligence")
            if not use_llm:
                st.info("Enable AI model configuration in the sidebar to get enhanced market intelligence")
                st.markdown(generate_market_insights(selected_category, use_llm=False))
            else:
                with st.spinner("Generating market intelligence..."):
                    market_insights = generate_market_insights(selected_category, use_llm=True)
                    st.markdown(market_insights)
        
        # Market Trend Analysis (simulated)
        st.subheader("Market Trend Analysis")
        
        tab1, tab2, tab3 = st.tabs(["Commodity Price Trends", "Market Size Indicators", "News Sentiment"])
        
        with tab1:
            st.info("This section would display real commodity price trends from external data sources.")
            
            # Simulated commodity price trend data
            import numpy as np
            
            dates = pd.date_range(start=min_date, end=max_date, freq='MS')
            commodities = ["Steel", "Aluminum", "Plastic", "Paper", "Electronics"]
            
            commodity_data = []
            
            for commodity in commodities:
                # Create a base price with some randomness
                if commodity == "Steel":
                    base_price = 800
                    volatility = 50
                elif commodity == "Aluminum":
                    base_price = 600
                    volatility = 40
                elif commodity == "Plastic":
                    base_price = 400
                    volatility = 30
                elif commodity == "Paper":
                    base_price = 200
                    volatility = 20
                else:  # Electronics
                    base_price = 1000
                    volatility = 70
                
                # Generate prices with a slight upward trend
                np.random.seed(42)  # For reproducibility
                prices = [base_price]
                for i in range(1, len(dates)):
                    change = np.random.normal(5, volatility)  # Slight upward trend
                    new_price = max(50, prices[-1] + change)  # Ensure price doesn't go too low
                    prices.append(int(new_price))
                
                for i, date in enumerate(dates):
                    commodity_data.append({
                        "Date": date,
                        "Commodity": commodity,
                        "Price": float(prices[i])
                    })
            
            commodity_df = pd.DataFrame(commodity_data)
            
            fig5 = px.line(
                commodity_df,
                x="Date",
                y="Price",
                color="Commodity",
                title="Simulated Commodity Price Trends ($/Metric Ton)",
                labels={"Price": "Price ($/Metric Ton)", "Date": "Month", "Commodity": "Commodity"},
                markers=True
            )
            
            st.plotly_chart(fig5, use_container_width=True)
        
        with tab2:
            st.info("This section would display market size indicators from external data sources.")
            
            # Simulated market size data
            market_size_data = {
                "Category": ["IT Hardware", "IT Software", "Office Supplies", "Professional Services", 
                            "Logistics", "Facilities", "Raw Materials", "Marketing", "Travel"],
                "MarketSize": [120, 200, 80, 150, 110, 90, 130, 100, 70],
                "GrowthRate": [3.2, 8.5, 1.5, 5.2, 2.8, 1.2, 3.8, 4.5, -2.1]
            }
            
            market_df = pd.DataFrame(market_size_data)
            
            fig6 = px.scatter(
                market_df,
                x="MarketSize",
                y="GrowthRate",
                color="GrowthRate",
                size="MarketSize",
                text="Category",
                title="Simulated Market Size and Growth by Category",
                labels={"MarketSize": "Market Size ($ Billions)", "GrowthRate": "Annual Growth Rate (%)", "Category": "Category"},
                color_continuous_scale="Oranges"
            )
            
            fig6.update_traces(textposition='top center')
            fig6.add_hline(y=0, line_width=1, line_dash="dash", line_color="gray")
            fig6.update_layout(height=600)
            
            st.plotly_chart(fig6, use_container_width=True)
        
        with tab3:
            st.info("This section would display news sentiment analysis from external data sources.")
            
            # Simulated news sentiment data
            news_data = {
                "Category": ["IT Hardware", "IT Software", "Office Supplies", "Professional Services", 
                            "Logistics", "Facilities", "Raw Materials", "Marketing", "Travel"],
                "Sentiment": [65, 78, 45, 60, 40, 52, 35, 72, 48],
                "NewsCount": [120, 200, 50, 100, 80, 60, 90, 110, 70]
            }
            
            news_df = pd.DataFrame(news_data)
            
            fig7 = px.bar(
                news_df,
                x="Category",
                y="Sentiment",
                color="Sentiment",
                title="Simulated News Sentiment by Category (Higher is More Positive)",
                labels={"Sentiment": "Sentiment Score (0-100)", "Category": "Category", "NewsCount": "Number of News Articles"},
                color_continuous_scale="Oranges"
            )
            
            st.plotly_chart(fig7, use_container_width=True)
            
            # Simulated news headlines
            st.subheader("Recent Industry News (Simulated)")
            
            news_items = [
                {"headline": "Global chip shortage eases as manufacturers increase production", 
                 "source": "Tech Daily", "date": "2023-05-15", "sentiment": "Positive"},
                {"headline": "New regulations impact logistics costs across Europe", 
                 "source": "Supply Chain Weekly", "date": "2023-05-10", "sentiment": "Negative"},
                {"headline": "Office supplies market faces disruption from remote work trends", 
                 "source": "Business Insights", "date": "2023-05-07", "sentiment": "Neutral"},
                {"headline": "Sustainable materials seeing increased adoption in manufacturing", 
                 "source": "Industry Today", "date": "2023-05-02", "sentiment": "Positive"},
                {"headline": "Software as a Service spending continues strong growth in enterprise sector", 
                 "source": "IT Review", "date": "2023-04-28", "sentiment": "Positive"}
            ]
            
            for item in news_items:
                sentiment_color = "green" if item["sentiment"] == "Positive" else ("red" if item["sentiment"] == "Negative" else "gray")
                st.markdown(f"**{item['headline']}** - {item['source']} ({item['date']}) "
                            f"[{item['sentiment']}]({sentiment_color})")
