import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

def show(session_state):
    """Display the Market Engagement tab content"""
    st.title("🌐 Market Engagement Facilitator")
    
    # Get data from session state
    spend_data = session_state.spend_data
    supplier_data = session_state.supplier_data
    
    # Filter controls
    st.subheader("Market Exploration Filters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Category filter
        categories = ["All Categories"] + sorted(spend_data["Category"].unique().tolist())
        selected_category = st.selectbox("Select Category:", categories, key="market_category")
    
    with col2:
        # Region filter - derived from supplier data
        regions = ["All Regions", "North America", "Europe", "Asia", "Other"]
        selected_region = st.selectbox("Select Region:", regions)
    
    with col3:
        # Market maturity filter (conceptual)
        market_maturity = st.selectbox(
            "Market Maturity:",
            ["All", "Emerging", "Growing", "Mature", "Declining"]
        )
    
    # New Supplier Discovery Section
    st.subheader("New Supplier Discovery")
    
    # Create a simulated supplier database for discovery
    potential_suppliers = generate_potential_suppliers(selected_category, selected_region)
    
    if len(potential_suppliers) > 0:
        # Display potential suppliers table
        st.dataframe(
            potential_suppliers,
            column_config={
                "SupplierName": "Supplier Name",
                "Category": "Category",
                "Region": "Region",
                "Country": "Country",
                "ESGRating": "ESG Rating",
                "MarketShare": "Market Share (%)",
                "YearsInBusiness": "Years in Business"
            },
            hide_index=True
        )
        
        # Supplier distribution map
        st.subheader("Geographical Distribution of Potential Suppliers")
        
        fig1 = px.scatter_geo(
            potential_suppliers,
            lat="Latitude",
            lon="Longitude",
            color="Category" if selected_category == "All Categories" else "ESGRating",
            hover_name="SupplierName",
            size="MarketShare",
            projection="natural earth",
            title="Potential Suppliers by Location",
            color_continuous_scale="Oranges" if selected_category != "All Categories" else None
        )
        
        fig1.update_layout(
            margin=dict(l=0, r=0, t=40, b=0),
            geo=dict(
                showland=True,
                landcolor='rgb(243, 243, 243)',
                countrycolor='rgb(204, 204, 204)',
            )
        )
        
        st.plotly_chart(fig1, use_container_width=True)
        
        # Market share and ESG rating comparison
        st.subheader("Supplier Market Share vs. ESG Rating")
        
        fig2 = px.scatter(
            potential_suppliers,
            x="MarketShare",
            y="ESGRating",
            color="Category" if selected_category == "All Categories" else "Region",
            size="YearsInBusiness",
            hover_name="SupplierName",
            title="Market Share vs. Sustainability",
            labels={
                "MarketShare": "Market Share (%)",
                "ESGRating": "ESG Rating (1-10)",
                "YearsInBusiness": "Years in Business"
            }
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No potential suppliers found matching your criteria. Try adjusting the filters.")
    
    # Internal Needs Analysis Section
    st.subheader("Internal Needs Analysis")
    
    # Filter spend data based on selected category
    if selected_category != "All Categories":
        category_spend = spend_data[spend_data["Category"] == selected_category]
    else:
        category_spend = spend_data
    
    # Create tabs for different analyses
    tab1, tab2, tab3 = st.tabs(["Spend Concentration", "Sourcing Opportunities", "Contract Coverage"])
    
    with tab1:
        # Analyze supplier concentration by category
        if len(category_spend) > 0:
            # Group by category and supplier
            category_supplier_spend = category_spend.groupby(["Category", "Supplier"])["Amount"].sum().reset_index()
            
            # Calculate total spend per category
            category_total = category_supplier_spend.groupby("Category")["Amount"].sum().reset_index()
            category_total.columns = ["Category", "TotalSpend"]
            
            # Merge to calculate percentage
            category_supplier_spend = category_supplier_spend.merge(category_total, on="Category")
            category_supplier_spend["SpendPercentage"] = (category_supplier_spend["Amount"] / category_supplier_spend["TotalSpend"]) * 100
            
            # Identify top supplier per category
            top_suppliers = category_supplier_spend.sort_values(["Category", "SpendPercentage"], ascending=[True, False])
            top_suppliers = top_suppliers.groupby("Category").head(3)
            
            # Create visualization
            fig3 = px.bar(
                top_suppliers,
                x="Category",
                y="SpendPercentage",
                color="Supplier",
                title="Supplier Concentration by Category (Top 3 Suppliers)",
                labels={
                    "SpendPercentage": "Spend Percentage (%)",
                    "Category": "Category",
                    "Supplier": "Supplier"
                },
                barmode="group"
            )
            
            st.plotly_chart(fig3, use_container_width=True)
            
            # Calculate concentration metrics
            concentrated_categories = []
            
            for category in top_suppliers["Category"].unique():
                cat_data = top_suppliers[top_suppliers["Category"] == category]
                top_supplier = cat_data.iloc[0]
                if top_supplier["SpendPercentage"] > 50:
                    concentrated_categories.append({
                        "Category": category,
                        "TopSupplier": top_supplier["Supplier"],
                        "SpendPercentage": top_supplier["SpendPercentage"]
                    })
            
            if concentrated_categories:
                st.warning("**High Concentration Risk Detected**")
                st.markdown("The following categories have high supplier concentration (>50% with a single supplier):")
                
                for item in concentrated_categories:
                    st.markdown(f"- **{item['Category']}**: {item['TopSupplier']} accounts for {item['SpendPercentage']:.1f}% of spend")
            else:
                st.success("No high supplier concentration risks detected.")
        else:
            st.info("No spend data available for the selected category.")
    
    with tab2:
        # Identify sourcing opportunities
        if len(category_spend) > 0:
            # Identify categories with few suppliers
            supplier_count = category_spend.groupby("Category")["Supplier"].nunique().reset_index()
            supplier_count.columns = ["Category", "SupplierCount"]
            
            # Group by Category to get total spend
            category_spend_total = category_spend.groupby("Category")["Amount"].sum().reset_index()
            category_spend_total.columns = ["Category", "TotalSpend"]
            
            # Merge the dataframes
            sourcing_opportunities = supplier_count.merge(category_spend_total, on="Category")
            
            # Calculate average transaction size
            transaction_count = category_spend.groupby("Category").size().reset_index()
            transaction_count.columns = ["Category", "TransactionCount"]
            sourcing_opportunities = sourcing_opportunities.merge(transaction_count, on="Category")
            sourcing_opportunities["AvgTransactionSize"] = sourcing_opportunities["TotalSpend"] / sourcing_opportunities["TransactionCount"]
            
            # Create opportunity score (higher score = better opportunity)
            # Logic: High spend + low supplier count = good opportunity
            sourcing_opportunities["OpportunityScore"] = (
                sourcing_opportunities["TotalSpend"] / sourcing_opportunities["TotalSpend"].max() * 5 +
                (10 - sourcing_opportunities["SupplierCount"]) / 10 * 5
            )
            
            # Sort by opportunity score
            sourcing_opportunities = sourcing_opportunities.sort_values("OpportunityScore", ascending=False)
            
            # Visualize opportunities
            fig4 = px.scatter(
                sourcing_opportunities,
                x="TotalSpend",
                y="SupplierCount",
                size="AvgTransactionSize",
                color="OpportunityScore",
                hover_name="Category",
                title="Sourcing Opportunity Analysis",
                labels={
                    "TotalSpend": "Total Spend ($)",
                    "SupplierCount": "Number of Suppliers",
                    "AvgTransactionSize": "Avg. Transaction Size ($)",
                    "OpportunityScore": "Opportunity Score"
                },
                color_continuous_scale="Oranges"
            )
            
            # Add annotations for high opportunity categories
            top_opportunities = sourcing_opportunities.head(3)
            annotations = []
            
            for _, opportunity in top_opportunities.iterrows():
                annotations.append(
                    dict(
                        x=opportunity["TotalSpend"],
                        y=opportunity["SupplierCount"],
                        text=opportunity["Category"],
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1,
                        arrowwidth=2,
                        arrowcolor="#636363",
                        ax=30,
                        ay=-30
                    )
                )
            
            fig4.update_layout(annotations=annotations)
            
            st.plotly_chart(fig4, use_container_width=True)
            
            # Display top opportunities
            st.subheader("Top Sourcing Opportunities")
            
            for i, (_, opportunity) in enumerate(top_opportunities.iterrows()):
                st.markdown(f"**{i+1}. {opportunity['Category']}**")
                st.markdown(f"Total Spend: ${opportunity['TotalSpend']:,.2f}")
                st.markdown(f"Current Suppliers: {opportunity['SupplierCount']}")
                st.markdown(f"Opportunity Score: {opportunity['OpportunityScore']:.1f}/10")
                
                if opportunity["SupplierCount"] <= 3 and opportunity["TotalSpend"] > 100000:
                    st.markdown("**Recommendation**: Expand supplier base to reduce concentration risk")
                elif opportunity["SupplierCount"] > 10:
                    st.markdown("**Recommendation**: Consider supplier consolidation to leverage volumes")
                else:
                    st.markdown("**Recommendation**: Review pricing and terms with current suppliers")
                
                st.markdown("---")
        else:
            st.info("No spend data available for the selected category.")
    
    with tab3:
        # Contract coverage analysis (simulated)
        st.info("This section would analyze contract coverage across categories using your contract data.")
        
        # Create simulated contract coverage data
        contract_coverage = {
            "Category": ["IT Hardware", "IT Software", "Office Supplies", "Professional Services", 
                        "Logistics", "Facilities", "Raw Materials", "Marketing", "Travel"],
            "TotalSpend": [250000, 450000, 120000, 380000, 220000, 190000, 320000, 150000, 90000],
            "ContractCoverage": [85, 92, 45, 78, 65, 70, 55, 60, 30],
            "ContractCount": [5, 8, 3, 12, 6, 4, 7, 5, 2]
        }
        
        contract_df = pd.DataFrame(contract_coverage)
        
        # Visualize contract coverage
        fig5 = px.bar(
            contract_df,
            x="Category",
            y="ContractCoverage",
            color="ContractCoverage",
            hover_data=["TotalSpend", "ContractCount"],
            title="Contract Coverage by Category (Simulated)",
            labels={
                "ContractCoverage": "Contract Coverage (%)",
                "Category": "Category",
                "TotalSpend": "Total Spend ($)",
                "ContractCount": "Number of Contracts"
            },
            color_continuous_scale="Oranges"
        )
        
        # Add threshold line for target coverage
        fig5.add_hline(
            y=80, 
            line_dash="dash", 
            line_color="red",
            annotation_text="Target Coverage (80%)",
            annotation_position="top right"
        )
        
        st.plotly_chart(fig5, use_container_width=True)
        
        # Identify categories with low contract coverage
        low_coverage = contract_df[contract_df["ContractCoverage"] < 70].sort_values("TotalSpend", ascending=False)
        
        if len(low_coverage) > 0:
            st.warning("**Contract Coverage Improvement Opportunities**")
            
            for _, row in low_coverage.iterrows():
                st.markdown(f"- **{row['Category']}**: {row['ContractCoverage']}% coverage, ${row['TotalSpend']:,.2f} annual spend")
            
            st.markdown("**Recommendation**: Consider establishing contracts for these categories to improve spend management and capture savings.")
    
    # Market Capability Overview Section
    st.subheader("Market Capability Overview")
    
    # Create market capability visualization for selected category
    if selected_category != "All Categories":
        display_category = selected_category
    else:
        display_category = st.selectbox("Select Category for Market Analysis:", 
                                        sorted(spend_data["Category"].unique().tolist()))
    
    # Create simulated market capability data
    market_capabilities = generate_market_capabilities(display_category)
    
    # Display market overview
    st.markdown(f"### {display_category} Market Overview")
    
    # Create metrics row
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric("Suppliers", market_capabilities["supplier_count"])
    
    with metric_col2:
        st.metric("Market Growth", f"{market_capabilities['market_growth']}%")
    
    with metric_col3:
        st.metric("Innovation Index", f"{market_capabilities['innovation_index']}/10")
    
    with metric_col4:
        st.metric("Average ESG Score", f"{market_capabilities['avg_esg_score']}/10")
    
    # Display radar chart of market capabilities
    radar_data = {
        'Metric': ['Supply Base', 'Innovation', 'Price Competitiveness', 'Quality Standards', 'Sustainability'],
        'Score': [
            market_capabilities['dimensions']['supply_base'],
            market_capabilities['dimensions']['innovation'],
            market_capabilities['dimensions']['price_competitiveness'],
            market_capabilities['dimensions']['quality_standards'],
            market_capabilities['dimensions']['sustainability']
        ]
    }
    
    radar_df = pd.DataFrame(radar_data)
    
    fig6 = go.Figure()
    
    fig6.add_trace(go.Scatterpolar(
        r=radar_df['Score'],
        theta=radar_df['Metric'],
        fill='toself',
        name='Market Capabilities',
        line_color='orange'
    ))
    
    fig6.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=False,
        title=f"Market Capability Assessment: {display_category}"
    )
    
    st.plotly_chart(fig6, use_container_width=True)
    
    # Trend analysis
    st.subheader("Price Trend Analysis")
    
    # Generate simulated price trend data
    price_trend_data = generate_price_trends(display_category)
    
    fig7 = px.line(
        price_trend_data,
        x="Quarter",
        y="PriceIndex",
        color="Region",
        title=f"Price Index Trends: {display_category}",
        labels={"PriceIndex": "Price Index (100 = Base)", "Quarter": "Quarter"},
        markers=True
    )
    
    st.plotly_chart(fig7, use_container_width=True)
    
    # Key market insights
    st.subheader("Key Market Insights")
    
    insights = market_capabilities["insights"]
    
    for insight in insights:
        st.markdown(f"- **{insight['title']}**: {insight['description']}")
    
    # Market engagement recommendations
    st.subheader("Engagement Recommendations")
    
    st.markdown(f"""
    Based on the {display_category} market analysis, consider the following approach:
    
    1. **Engagement Strategy**: {market_capabilities['recommendations']['strategy']}
    
    2. **Supplier Approach**: {market_capabilities['recommendations']['supplier_approach']}
    
    3. **Negotiation Leverage**: {market_capabilities['recommendations']['negotiation_leverage']}
    
    4. **Innovation Opportunities**: {market_capabilities['recommendations']['innovation']}
    """)

def generate_potential_suppliers(category="All Categories", region="All Regions"):
    """Generate simulated potential supplier data based on filters"""
    # Base set of potential suppliers
    all_suppliers = [
        {"name": "NextGen Tech", "category": "IT Hardware", "country": "USA", "region": "North America", "lat": 37.7749, "lon": -122.4194},
        {"name": "EuroSoft Solutions", "category": "IT Software", "country": "Germany", "region": "Europe", "lat": 52.5200, "lon": 13.4050},
        {"name": "Global Office Supplies", "category": "Office Supplies", "country": "Canada", "region": "North America", "lat": 43.6532, "lon": -79.3832},
        {"name": "Asian Electronics Ltd", "category": "IT Hardware", "country": "Japan", "region": "Asia", "lat": 35.6762, "lon": 139.6503},
        {"name": "Eco Materials Inc", "category": "Raw Materials", "country": "USA", "region": "North America", "lat": 40.7128, "lon": -74.0060},
        {"name": "Professional Services Group", "category": "Professional Services", "country": "UK", "region": "Europe", "lat": 51.5074, "lon": -0.1278},
        {"name": "Sustainable Office Co", "category": "Office Supplies", "country": "Netherlands", "region": "Europe", "lat": 52.3676, "lon": 4.9041},
        {"name": "Pacific Logistics Partners", "category": "Logistics", "country": "Singapore", "region": "Asia", "lat": 1.3521, "lon": 103.8198},
        {"name": "Smart Facility Management", "category": "Facilities", "country": "France", "region": "Europe", "lat": 48.8566, "lon": 2.3522},
        {"name": "Industrial Raw Materials", "category": "Raw Materials", "country": "China", "region": "Asia", "lat": 39.9042, "lon": 116.4074},
        {"name": "Creative Marketing Agency", "category": "Marketing", "country": "Australia", "region": "Other", "lat": -33.8688, "lon": 151.2093},
        {"name": "Travel Management Solutions", "category": "Travel", "country": "Spain", "region": "Europe", "lat": 40.4168, "lon": -3.7038},
        {"name": "Quality IT Consultants", "category": "Professional Services", "country": "India", "region": "Asia", "lat": 28.6139, "lon": 77.2090},
        {"name": "Nordic Office Systems", "category": "Office Supplies", "country": "Sweden", "region": "Europe", "lat": 59.3293, "lon": 18.0686},
        {"name": "American Logistics Corp", "category": "Logistics", "country": "USA", "region": "North America", "lat": 33.7490, "lon": -84.3880},
        {"name": "Innovative Software Labs", "category": "IT Software", "country": "Israel", "region": "Other", "lat": 32.0853, "lon": 34.7818},
        {"name": "European Raw Materials", "category": "Raw Materials", "country": "Poland", "region": "Europe", "lat": 52.2297, "lon": 21.0122},
        {"name": "Global Facilities Services", "category": "Facilities", "country": "Brazil", "region": "Other", "lat": -23.5505, "lon": -46.6333},
        {"name": "Digital Marketing Experts", "category": "Marketing", "country": "Canada", "region": "North America", "lat": 45.5017, "lon": -73.5673},
        {"name": "Corporate Travel Solutions", "category": "Travel", "country": "Hong Kong", "region": "Asia", "lat": 22.3193, "lon": 114.1694},
    ]
    
    # Filter by category
    if category != "All Categories":
        all_suppliers = [s for s in all_suppliers if s["category"] == category]
    
    # Filter by region
    if region != "All Regions":
        all_suppliers = [s for s in all_suppliers if s["region"] == region]
    
    # If no suppliers match the filters, return empty list
    if len(all_suppliers) == 0:
        return []
    
    # Create pandas DataFrame from the filtered list
    np.random.seed(42)  # For reproducibility
    
    potential_suppliers = []
    
    for supplier in all_suppliers:
        # Generate random metrics for each supplier
        esg_rating = round(np.random.uniform(4, 10), 1)
        market_share = round(np.random.uniform(0.5, 15), 1)
        years_in_business = np.random.randint(2, 50)
        certifications = np.random.choice(
            ["ISO 9001", "ISO 14001", "ISO 27001", "None"],
            size=np.random.randint(0, 4),
            replace=False
        )
        
        potential_suppliers.append({
            "SupplierName": supplier["name"],
            "Category": supplier["category"],
            "Region": supplier["region"],
            "Country": supplier["country"],
            "ESGRating": esg_rating,
            "MarketShare": market_share,
            "YearsInBusiness": years_in_business,
            "Certifications": ", ".join(certifications) if len(certifications) > 0 else "None",
            "Latitude": supplier["lat"],
            "Longitude": supplier["lon"]
        })
    
    return pd.DataFrame(potential_suppliers)

def generate_market_capabilities(category):
    """Generate simulated market capability data for a given category"""
    # Set random seed for reproducibility
    np.random.seed(hash(category) % 2**32)
    
    # Generate category-specific capabilities
    capabilities = {
        "IT Hardware": {
            "supplier_count": np.random.randint(50, 200),
            "market_growth": round(np.random.uniform(2.0, 8.0), 1),
            "innovation_index": round(np.random.uniform(7.0, 9.5), 1),
            "avg_esg_score": round(np.random.uniform(5.0, 8.0), 1),
            "dimensions": {
                "supply_base": round(np.random.uniform(7.0, 9.0), 1),
                "innovation": round(np.random.uniform(8.0, 10.0), 1),
                "price_competitiveness": round(np.random.uniform(6.0, 8.0), 1),
                "quality_standards": round(np.random.uniform(7.0, 9.0), 1),
                "sustainability": round(np.random.uniform(5.0, 7.0), 1)
            },
            "insights": [
                {
                    "title": "Supply Chain Challenges",
                    "description": "Global chip shortages continue to impact hardware availability, though improving from 2022 levels."
                },
                {
                    "title": "Sustainability Focus",
                    "description": "Increasing emphasis on energy-efficient hardware and sustainable manufacturing practices."
                },
                {
                    "title": "Pricing Trends",
                    "description": "Prices stabilizing after post-pandemic increases, with competitive pressure in commodity segments."
                }
            ],
            "recommendations": {
                "strategy": "Consider strategic partnerships with key manufacturers to secure supply and preferential terms.",
                "supplier_approach": "Engage with tier-1 suppliers directly while exploring emerging players for specialized needs.",
                "negotiation_leverage": "Bundle purchases across hardware categories and emphasize total cost of ownership in negotiations.",
                "innovation": "Explore Hardware-as-a-Service models to reduce capital expenditure and improve lifecycle management."
            }
        },
        "IT Software": {
            "supplier_count": np.random.randint(200, 500),
            "market_growth": round(np.random.uniform(7.0, 12.0), 1),
            "innovation_index": round(np.random.uniform(8.0, 10.0), 1),
            "avg_esg_score": round(np.random.uniform(6.0, 8.5), 1),
            "dimensions": {
                "supply_base": round(np.random.uniform(8.0, 10.0), 1),
                "innovation": round(np.random.uniform(8.5, 10.0), 1),
                "price_competitiveness": round(np.random.uniform(5.0, 7.0), 1),
                "quality_standards": round(np.random.uniform(7.0, 9.0), 1),
                "sustainability": round(np.random.uniform(7.0, 9.0), 1)
            },
            "insights": [
                {
                    "title": "SaaS Dominance",
                    "description": "Subscription-based models now represent over 70% of enterprise software spending."
                },
                {
                    "title": "AI Integration",
                    "description": "Rapid integration of AI capabilities across all software categories, creating differentiation."
                },
                {
                    "title": "Vendor Consolidation",
                    "description": "Major platform providers expanding capabilities through acquisition, reducing point solution viability."
                }
            ],
            "recommendations": {
                "strategy": "Develop a platform-first approach with strategic enterprise agreements for core platforms.",
                "supplier_approach": "Consolidate spend with major platforms while maintaining selective best-of-breed solutions.",
                "negotiation_leverage": "Multi-year commitments with flexible scaling options to secure optimal pricing.",
                "innovation": "Partner with vendors offering integrated AI capabilities to enhance business processes."
            }
        },
        "Office Supplies": {
            "supplier_count": np.random.randint(100, 300),
            "market_growth": round(np.random.uniform(-1.0, 3.0), 1),
            "innovation_index": round(np.random.uniform(3.0, 6.0), 1),
            "avg_esg_score": round(np.random.uniform(5.0, 7.0), 1),
            "dimensions": {
                "supply_base": round(np.random.uniform(8.0, 10.0), 1),
                "innovation": round(np.random.uniform(3.0, 6.0), 1),
                "price_competitiveness": round(np.random.uniform(7.0, 9.0), 1),
                "quality_standards": round(np.random.uniform(6.0, 8.0), 1),
                "sustainability": round(np.random.uniform(5.0, 8.0), 1)
            },
            "insights": [
                {
                    "title": "Hybrid Work Impact",
                    "description": "Shifting demand patterns due to hybrid work models, with decreased overall volume but more diverse needs."
                },
                {
                    "title": "Sustainable Products",
                    "description": "Growing market share for eco-friendly and recycled office products, with price premiums decreasing."
                },
                {
                    "title": "Consolidation Trend",
                    "description": "Distributor consolidation accelerating, with integrated service providers gaining market share."
                }
            ],
            "recommendations": {
                "strategy": "Consolidate spend through a primary supplier with strong e-procurement capabilities.",
                "supplier_approach": "Focus on suppliers offering flexible delivery models supporting hybrid work environments.",
                "negotiation_leverage": "Leverage market competition for aggressive pricing while emphasizing sustainability requirements.",
                "innovation": "Explore vendors offering consumption-based models and inventory management solutions."
            }
        },
        "Professional Services": {
            "supplier_count": np.random.randint(300, 1000),
            "market_growth": round(np.random.uniform(4.0, 8.0), 1),
            "innovation_index": round(np.random.uniform(6.0, 8.0), 1),
            "avg_esg_score": round(np.random.uniform(6.0, 8.0), 1),
            "dimensions": {
                "supply_base": round(np.random.uniform(8.0, 10.0), 1),
                "innovation": round(np.random.uniform(6.0, 8.0), 1),
                "price_competitiveness": round(np.random.uniform(5.0, 7.0), 1),
                "quality_standards": round(np.random.uniform(7.0, 9.0), 1),
                "sustainability": round(np.random.uniform(6.0, 8.0), 1)
            },
            "insights": [
                {
                    "title": "Specialized Expertise",
                    "description": "Growing demand for specialized expertise, particularly in technology transformation and sustainability."
                },
                {
                    "title": "Delivery Models",
                    "description": "Increasing adoption of outcome-based contracts and hybrid onshore/offshore delivery models."
                },
                {
                    "title": "Talent Constraints",
                    "description": "Ongoing talent constraints in key areas driving rate increases and extended delivery timelines."
                }
            ],
            "recommendations": {
                "strategy": "Develop a tiered panel of preferred providers with clear category specializations.",
                "supplier_approach": "Balance established firms with specialized boutiques for optimal expertise access.",
                "negotiation_leverage": "Structure outcomes-based contracts with clear deliverables and performance incentives.",
                "innovation": "Explore alternative delivery models combining technology platforms with advisory services."
            }
        },
        "Logistics": {
            "supplier_count": np.random.randint(100, 400),
            "market_growth": round(np.random.uniform(2.0, 6.0), 1),
            "innovation_index": round(np.random.uniform(5.0, 8.0), 1),
            "avg_esg_score": round(np.random.uniform(4.0, 7.0), 1),
            "dimensions": {
                "supply_base": round(np.random.uniform(7.0, 9.0), 1),
                "innovation": round(np.random.uniform(5.0, 8.0), 1),
                "price_competitiveness": round(np.random.uniform(6.0, 8.0), 1),
                "quality_standards": round(np.random.uniform(6.0, 8.0), 1),
                "sustainability": round(np.random.uniform(4.0, 7.0), 1)
            },
            "insights": [
                {
                    "title": "Rate Volatility",
                    "description": "Freight rates stabilizing after extreme volatility, but remain above pre-pandemic levels."
                },
                {
                    "title": "Green Logistics",
                    "description": "Increased focus on sustainability with carbon tracking and alternative fuel options expanding."
                },
                {
                    "title": "Technology Integration",
                    "description": "Advanced visibility platforms becoming standard offering from major logistics providers."
                }
            ],
            "recommendations": {
                "strategy": "Implement a dual-supplier strategy with primary and backup providers for key lanes.",
                "supplier_approach": "Focus on providers with strong technology platforms and sustainability commitments.",
                "negotiation_leverage": "Use multi-year volume commitments with flexibility clauses to secure competitive rates.",
                "innovation": "Explore providers offering integrated logistics management platforms with real-time visibility."
            }
        },
        "Facilities": {
            "supplier_count": np.random.randint(100, 300),
            "market_growth": round(np.random.uniform(1.0, 5.0), 1),
            "innovation_index": round(np.random.uniform(4.0, 7.0), 1),
            "avg_esg_score": round(np.random.uniform(5.0, 8.0), 1),
            "dimensions": {
                "supply_base": round(np.random.uniform(7.0, 9.0), 1),
                "innovation": round(np.random.uniform(4.0, 7.0), 1),
                "price_competitiveness": round(np.random.uniform(6.0, 8.0), 1),
                "quality_standards": round(np.random.uniform(6.0, 8.0), 1),
                "sustainability": round(np.random.uniform(6.0, 8.0), 1)
            },
            "insights": [
                {
                    "title": "Integrated Services",
                    "description": "Growing preference for integrated facility management over individual service contracts."
                },
                {
                    "title": "Sustainability Focus",
                    "description": "Increased emphasis on energy efficiency and sustainable building maintenance practices."
                },
                {
                    "title": "Labor Challenges",
                    "description": "Persistent labor shortages impacting service availability and driving wage inflation."
                }
            ],
            "recommendations": {
                "strategy": "Consider integrated facility management approach for core locations with specialized providers for critical services.",
                "supplier_approach": "Balance regional providers with national/global capabilities based on facility distribution.",
                "negotiation_leverage": "Develop performance-based contracts with clear KPIs and quality standards.",
                "innovation": "Explore providers offering smart building technologies and predictive maintenance capabilities."
            }
        },
        "Raw Materials": {
            "supplier_count": np.random.randint(50, 200),
            "market_growth": round(np.random.uniform(0.0, 4.0), 1),
            "innovation_index": round(np.random.uniform(3.0, 6.0), 1),
            "avg_esg_score": round(np.random.uniform(4.0, 7.0), 1),
            "dimensions": {
                "supply_base": round(np.random.uniform(6.0, 8.0), 1),
                "innovation": round(np.random.uniform(3.0, 6.0), 1),
                "price_competitiveness": round(np.random.uniform(5.0, 7.0), 1),
                "quality_standards": round(np.random.uniform(7.0, 9.0), 1),
                "sustainability": round(np.random.uniform(4.0, 7.0), 1)
            },
            "insights": [
                {
                    "title": "Price Volatility",
                    "description": "Commodity prices showing increased volatility due to geopolitical factors and supply constraints."
                },
                {
                    "title": "Supply Security",
                    "description": "Growing focus on supply security and regional sourcing to mitigate geopolitical risks."
                },
                {
                    "title": "Regulatory Compliance",
                    "description": "Increasing regulatory requirements for material sourcing transparency and environmental impact."
                }
            ],
            "recommendations": {
                "strategy": "Develop a mix of spot purchases and long-term contracts to balance price opportunities with security.",
                "supplier_approach": "Diversify supplier base geographically while developing strategic partnerships with key providers.",
                "negotiation_leverage": "Consider index-based pricing mechanisms with caps and floors to manage volatility.",
                "innovation": "Explore circular economy initiatives and recycled material options to reduce environmental impact."
            }
        },
        "Marketing": {
            "supplier_count": np.random.randint(200, 800),
            "market_growth": round(np.random.uniform(3.0, 8.0), 1),
            "innovation_index": round(np.random.uniform(7.0, 9.0), 1),
            "avg_esg_score": round(np.random.uniform(5.0, 8.0), 1),
            "dimensions": {
                "supply_base": round(np.random.uniform(8.0, 10.0), 1),
                "innovation": round(np.random.uniform(7.0, 9.0), 1),
                "price_competitiveness": round(np.random.uniform(6.0, 8.0), 1),
                "quality_standards": round(np.random.uniform(7.0, 9.0), 1),
                "sustainability": round(np.random.uniform(5.0, 8.0), 1)
            },
            "insights": [
                {
                    "title": "Digital Transformation",
                    "description": "Accelerating shift to digital channels, with over 70% of marketing budgets now allocated to digital."
                },
                {
                    "title": "Data Privacy Impact",
                    "description": "Evolving privacy regulations reshaping targeting capabilities and measurement approaches."
                },
                {
                    "title": "AI-Driven Content",
                    "description": "Rapid adoption of AI tools for content creation and campaign optimization."
                }
            ],
            "recommendations": {
                "strategy": "Develop a hybrid agency model with specialized providers for creative, media, and digital execution.",
                "supplier_approach": "Balance established agencies with specialized digital-native providers for optimal capabilities.",
                "negotiation_leverage": "Structure performance-based compensation models tied to measurable business outcomes.",
                "innovation": "Explore providers with AI-driven campaign optimization and content creation capabilities."
            }
        },
        "Travel": {
            "supplier_count": np.random.randint(100, 400),
            "market_growth": round(np.random.uniform(-3.0, 5.0), 1),
            "innovation_index": round(np.random.uniform(5.0, 8.0), 1),
            "avg_esg_score": round(np.random.uniform(5.0, 7.0), 1),
            "dimensions": {
                "supply_base": round(np.random.uniform(7.0, 9.0), 1),
                "innovation": round(np.random.uniform(6.0, 8.0), 1),
                "price_competitiveness": round(np.random.uniform(5.0, 7.0), 1),
                "quality_standards": round(np.random.uniform(6.0, 8.0), 1),
                "sustainability": round(np.random.uniform(5.0, 7.0), 1)
            },
            "insights": [
                {
                    "title": "Business Travel Evolution",
                    "description": "Permanent shift in business travel patterns, with selective in-person engagement replacing routine travel."
                },
                {
                    "title": "Sustainability Focus",
                    "description": "Growing emphasis on carbon footprint reduction and sustainable travel options."
                },
                {
                    "title": "Technology Integration",
                    "description": "Advanced booking platforms with integrated expense management becoming industry standard."
                }
            ],
            "recommendations": {
                "strategy": "Implement a managed travel program with strong policy controls and sustainability tracking.",
                "supplier_approach": "Focus on TMCs with strong technology platforms and supplier network influence.",
                "negotiation_leverage": "Develop a preferred supplier network with volume commitments for optimal pricing.",
                "innovation": "Explore providers offering integrated travel and expense management with sustainability analytics."
            }
        }
    }
    
    # Default values for categories not explicitly defined
    default_capabilities = {
        "supplier_count": np.random.randint(50, 300),
        "market_growth": round(np.random.uniform(1.0, 6.0), 1),
        "innovation_index": round(np.random.uniform(5.0, 8.0), 1),
        "avg_esg_score": round(np.random.uniform(5.0, 7.0), 1),
        "dimensions": {
            "supply_base": round(np.random.uniform(6.0, 8.0), 1),
            "innovation": round(np.random.uniform(5.0, 7.0), 1),
            "price_competitiveness": round(np.random.uniform(6.0, 8.0), 1),
            "quality_standards": round(np.random.uniform(6.0, 8.0), 1),
            "sustainability": round(np.random.uniform(5.0, 7.0), 1)
        },
        "insights": [
            {
                "title": "Market Dynamics",
                "description": "Moderate competition with steady growth projections for the coming year."
            },
            {
                "title": "Supplier Landscape",
                "description": "Mix of established providers and emerging specialists creating a balanced market."
            },
            {
                "title": "Technology Adoption",
                "description": "Gradual technology adoption improving service delivery and efficiency."
            }
        ],
        "recommendations": {
            "strategy": "Develop a balanced approach with multiple suppliers to ensure competition.",
            "supplier_approach": "Regular market assessments to identify new capabilities and competitive offerings.",
            "negotiation_leverage": "Use competitive bidding to drive optimal pricing and terms.",
            "innovation": "Evaluate emerging suppliers for specialized capabilities and innovative approaches."
        }
    }
    
    # Return category-specific capabilities or default if not found
    return capabilities.get(category, default_capabilities)

def generate_price_trends(category):
    """Generate simulated price trend data for a given category"""
    # Set random seed for reproducibility
    np.random.seed(hash(category) % 2**32)
    
    # Create quarterly dates for the past 2 years
    quarters = [
        "2022-Q1", "2022-Q2", "2022-Q3", "2022-Q4",
        "2023-Q1", "2023-Q2", "2023-Q3", "2023-Q4"
    ]
    
    regions = ["Global", "North America", "Europe", "Asia"]
    
    # Generate price trends with some correlation between quarters
    trend_data = []
    
    # Category-specific trend patterns
    if category in ["IT Hardware", "Electronics"]:
        # More volatile with recent decreases
        base_trend = [102, 105, 110, 108, 106, 104, 100, 98]
    elif category in ["IT Software", "Professional Services"]:
        # Steady increases
        base_trend = [100, 102, 104, 106, 108, 110, 112, 114]
    elif category in ["Raw Materials", "Logistics"]:
        # Highly volatile
        base_trend = [100, 110, 105, 115, 105, 95, 100, 105]
    elif category in ["Office Supplies", "Facilities"]:
        # Moderate increases
        base_trend = [100, 101, 102, 104, 105, 106, 107, 108]
    elif category == "Travel":
        # Pandemic recovery pattern
        base_trend = [85, 90, 95, 100, 105, 110, 115, 118]
    else:
        # Default moderate trend
        base_trend = [100, 102, 103, 104, 105, 106, 107, 108]
    
    # Generate data for each region with variations from the base trend
    for region in regions:
        # Add some region-specific variation
        if region == "Global":
            variation = 0  # Global follows the base trend
        elif region == "North America":
            variation = 2  # Slightly higher
        elif region == "Europe":
            variation = -1  # Slightly lower
        else:  # Asia
            variation = 1  # In between
        
        # Add some random noise to each point
        for i, quarter in enumerate(quarters):
            price_index = base_trend[i] + variation + np.random.uniform(-2, 2)
            trend_data.append({
                "Quarter": quarter,
                "Region": region,
                "PriceIndex": round(price_index, 1)
            })
    
    return pd.DataFrame(trend_data)
