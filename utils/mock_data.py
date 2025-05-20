import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def get_mock_spend_data():
    """Generate construction and MEP specific mock spend data for demonstration purposes"""
    # Define constants for mock data - Construction and MEP specific
    suppliers = [
        "Johnson Controls", "Schneider Electric", "Siemens Building Tech", 
        "Carrier HVAC", "Trane Technologies", "Daikin Industries",
        "Honeywell Building Solutions", "ABB Electrification", "Uponor Piping Systems",
        "Rheem Manufacturing", "Viega Plumbing", "Grundfos Pumps",
        "Eaton Electrical", "Victaulic Piping", "Mitsubishi Electric HVAC"
    ]
    
    categories = [
        "Mechanical", "Electrical", "Plumbing", "HVAC", 
        "Building Automation", "Fire Protection", "Structural Materials",
        "Finishing Materials", "Construction Equipment", "Safety Equipment"
    ]
    
    subcategories = {
        "Mechanical": ["Pumps", "Boilers", "Chillers", "Air Handlers", "Cooling Towers"],
        "Electrical": ["Distribution Panels", "Transformers", "Lighting", "Wiring", "Generators"],
        "Plumbing": ["Piping", "Fixtures", "Valves", "Water Heaters", "Drainage Systems"],
        "HVAC": ["Ductwork", "Heat Pumps", "Air Conditioning", "Ventilation Systems", "Controls"],
        "Building Automation": ["BMS Systems", "Controls", "Sensors", "Smart Building Tech", "Energy Management"],
        "Fire Protection": ["Sprinklers", "Alarms", "Extinguishers", "Smoke Detectors", "Fire Doors"],
        "Structural Materials": ["Steel", "Concrete", "Lumber", "Insulation", "Roofing"],
        "Finishing Materials": ["Drywall", "Flooring", "Paint", "Windows", "Doors"],
        "Construction Equipment": ["Scaffolding", "Lifts", "Power Tools", "Heavy Machinery", "Welding Equipment"],
        "Safety Equipment": ["PPE", "Safety Barriers", "Fall Protection", "First Aid", "Emergency Lighting"]
    }
    
    business_units = ["Commercial", "Healthcare", "Residential", "Industrial", "Government", "Education", "Data Centers"]
    
    # Generate dates for the last 2 years
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # ~2 years
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Generate 500 random transactions
    num_transactions = 500
    data = []
    
    for _ in range(num_transactions):
        supplier = random.choice(suppliers)
        category = random.choice(categories)
        subcategory = random.choice(subcategories[category])
        business_unit = random.choice(business_units)
        date = random.choice(date_range)
        
        # Generate amount based on category (construction/MEP specific spend patterns)
        base_amount = {
            "Mechanical": 15000,
            "Electrical": 12000,
            "Plumbing": 8000,
            "HVAC": 18000,
            "Building Automation": 25000,
            "Fire Protection": 9000,
            "Structural Materials": 22000,
            "Finishing Materials": 7500,
            "Construction Equipment": 14000,
            "Safety Equipment": 5000
        }
        
        amount = random.uniform(0.5, 1.5) * base_amount[category]
        
        # Add random invoice and PO numbers
        invoice_id = f"INV-{random.randint(10000, 99999)}"
        po_id = f"PO-{random.randint(10000, 99999)}"
        
        data.append({
            "Supplier": supplier,
            "Category": category,
            "SubCategory": subcategory,
            "BusinessUnit": business_unit,
            "Date": date,
            "Amount": round(amount, 2),
            "InvoiceID": invoice_id,
            "POID": po_id,
            "PaymentTerms": random.choice(["Net 30", "Net 45", "Net 60"]),
            "Currency": "USD"
        })
    
    return pd.DataFrame(data)

def get_mock_supplier_data():
    """Generate construction and MEP specific mock supplier data for demonstration purposes"""
    # Define constants for construction and MEP suppliers
    suppliers = [
        {"name": "Johnson Controls", "category": "Building Automation", "country": "USA", "city": "Milwaukee", "lat": 43.0389, "lon": -87.9065},
        {"name": "Schneider Electric", "category": "Electrical", "country": "France", "city": "Paris", "lat": 48.8566, "lon": 2.3522},
        {"name": "Siemens Building Tech", "category": "Building Automation", "country": "Germany", "city": "Munich", "lat": 48.1351, "lon": 11.5820},
        {"name": "Carrier HVAC", "category": "HVAC", "country": "USA", "city": "Palm Beach", "lat": 26.7056, "lon": -80.0364},
        {"name": "Trane Technologies", "category": "HVAC", "country": "USA", "city": "Davidson", "lat": 35.4993, "lon": -80.8528},
        {"name": "Daikin Industries", "category": "HVAC", "country": "Japan", "city": "Osaka", "lat": 34.6937, "lon": 135.5023},
        {"name": "Honeywell Building Solutions", "category": "Building Automation", "country": "USA", "city": "Charlotte", "lat": 35.2271, "lon": -80.8431},
        {"name": "ABB Electrification", "category": "Electrical", "country": "Switzerland", "city": "Zurich", "lat": 47.3769, "lon": 8.5417},
        {"name": "Uponor Piping Systems", "category": "Plumbing", "country": "Finland", "city": "Helsinki", "lat": 60.1699, "lon": 24.9384},
        {"name": "Rheem Manufacturing", "category": "Plumbing", "country": "USA", "city": "Atlanta", "lat": 33.7490, "lon": -84.3880},
        {"name": "Viega Plumbing", "category": "Plumbing", "country": "Germany", "city": "Attendorn", "lat": 51.1266, "lon": 7.9222},
        {"name": "Grundfos Pumps", "category": "Mechanical", "country": "Denmark", "city": "Bjerringbro", "lat": 56.3705, "lon": 9.6568},
        {"name": "Eaton Electrical", "category": "Electrical", "country": "Ireland", "city": "Dublin", "lat": 53.3498, "lon": -6.2603},
        {"name": "Victaulic Piping", "category": "Fire Protection", "country": "USA", "city": "Easton", "lat": 40.6881, "lon": -75.2201},
        {"name": "Mitsubishi Electric HVAC", "category": "HVAC", "country": "Japan", "city": "Tokyo", "lat": 35.6762, "lon": 139.6503},
    ]
    
    data = []
    
    for i, supplier in enumerate(suppliers):
        # Generate a supplier ID
        supplier_id = f"S{str(i+1).zfill(4)}"
        
        # Generate contact information
        contact_name = f"{random.choice(['John', 'Jane', 'Robert', 'Mary', 'David', 'Sarah'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Miller'])}"
        contact_email = f"{contact_name.lower().replace(' ', '.')}@{supplier['name'].lower().replace(' ', '')}.com"
        contact_phone = f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        
        # Generate financial details
        annual_revenue = random.randint(1, 50) * 1000000
        
        # Generate performance metrics
        payment_terms = random.choice(["Net 30", "Net 45", "Net 60"])
        
        data.append({
            "SupplierID": supplier_id,
            "SupplierName": supplier["name"],
            "Category": supplier["category"],
            "Country": supplier["country"],
            "City": supplier["city"],
            "Latitude": supplier["lat"],
            "Longitude": supplier["lon"],
            "ContactName": contact_name,
            "ContactEmail": contact_email,
            "ContactPhone": contact_phone,
            "AnnualRevenue": annual_revenue,
            "PaymentTerms": payment_terms,
            "Active": True,
            "RelationshipStartDate": f"{random.randint(2010, 2021)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
        })
    
    return pd.DataFrame(data)

def get_mock_contract_data():
    """Generate mock contract data for demonstration purposes"""
    # Base the contracts on the supplier data
    supplier_data = get_mock_supplier_data()
    
    data = []
    
    # Current date for reference
    current_date = datetime.now()
    
    # Create 2-3 contracts per supplier
    for _, supplier in supplier_data.iterrows():
        num_contracts = random.randint(1, 3)
        
        for j in range(num_contracts):
            # Generate contract ID
            contract_id = f"C{supplier['SupplierID'][1:]}{j+1}"
            
            # Contract type based on construction industry needs
            contract_type = random.choice(["Equipment", "Service & Maintenance", "Installation", "System Integration", "Parts & Materials", "Design Services"])
            
            # Generate start and end dates
            years_ago = random.randint(0, 3)
            months_ago = random.randint(0, 11)
            start_date = current_date - timedelta(days=365*years_ago + 30*months_ago)
            
            duration_years = random.randint(1, 5)
            end_date = start_date + timedelta(days=365*duration_years)
            
            # Format dates as strings
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
            # Generate contract value
            base_value = random.randint(10000, 1000000)
            value = round(base_value, -3)  # Round to nearest thousand
            
            # Status based on end date
            if end_date < current_date:
                status = "Expired"
            elif start_date > current_date:
                status = "Future"
            else:
                status = "Active"
            
            # Auto-renewal
            auto_renewal = random.choice([True, False])
            
            # Notice period
            notice_period_days = random.choice([30, 60, 90])
            
            data.append({
                "ContractID": contract_id,
                "SupplierID": supplier["SupplierID"],
                "SupplierName": supplier["SupplierName"],
                "Category": supplier["Category"],
                "ContractType": contract_type,
                "StartDate": start_date_str,
                "EndDate": end_date_str,
                "Value": value,
                "Currency": "USD",
                "Status": status,
                "AutoRenewal": auto_renewal,
                "NoticePeriodDays": notice_period_days
            })
    
    return pd.DataFrame(data)

def get_mock_performance_data():
    """Generate mock supplier performance data for demonstration purposes"""
    # Base the performance data on the supplier data
    supplier_data = get_mock_supplier_data()
    
    data = []
    
    # Generate performance data for the last 8 quarters
    quarters = ["2022-Q1", "2022-Q2", "2022-Q3", "2022-Q4", 
                "2023-Q1", "2023-Q2", "2023-Q3", "2023-Q4"]
    
    for _, supplier in supplier_data.iterrows():
        for quarter in quarters:
            # Generate random scores with some correlation between quarters
            if quarter == quarters[0]:
                # First quarter scores are completely random
                delivery_score = round(random.uniform(5.0, 10.0), 1)
                quality_score = round(random.uniform(5.0, 10.0), 1)
                responsiveness_score = round(random.uniform(5.0, 10.0), 1)
            else:
                # Subsequent quarters are somewhat correlated with the previous
                prev_data = [d for d in data if d["SupplierID"] == supplier["SupplierID"] and d["Quarter"] == quarters[quarters.index(quarter)-1]]
                if prev_data:
                    prev = prev_data[0]
                    # Score fluctuates by up to ±1.5 points
                    delivery_score = round(max(1, min(10, prev["DeliveryScore"] + random.uniform(-1.5, 1.5))), 1)
                    quality_score = round(max(1, min(10, prev["QualityScore"] + random.uniform(-1.5, 1.5))), 1)
                    responsiveness_score = round(max(1, min(10, prev["ResponsivenessScore"] + random.uniform(-1.5, 1.5))), 1)
                else:
                    # Fallback if previous quarter data is missing
                    delivery_score = round(random.uniform(5.0, 10.0), 1)
                    quality_score = round(random.uniform(5.0, 10.0), 1)
                    responsiveness_score = round(random.uniform(5.0, 10.0), 1)
            
            # Calculate overall score as weighted average
            overall_score = round((delivery_score * 0.4 + quality_score * 0.4 + responsiveness_score * 0.2), 1)
            
            data.append({
                "SupplierID": supplier["SupplierID"],
                "Quarter": quarter,
                "DeliveryScore": delivery_score,
                "QualityScore": quality_score,
                "ResponsivenessScore": responsiveness_score,
                "OverallScore": overall_score,
                "Comments": generate_performance_comment(overall_score)
            })
    
    return pd.DataFrame(data)

def generate_performance_comment(score):
    """Generate a construction and MEP specific performance comment based on the overall score"""
    if score >= 9.0:
        return random.choice([
            "Exceptional MEP installation quality and project delivery.",
            "Outstanding compliance with specifications and building codes.",
            "Excellent coordination with other trades and project teams.",
            "Superior technical expertise and system commissioning.",
            "Exceptional safety record and quality control procedures."
        ])
    elif score >= 8.0:
        return random.choice([
            "Very good system performance with minor commissioning adjustments needed.",
            "Strong technical documentation and as-built drawings provided.",
            "Consistently good coordination with project schedule requirements.",
            "Reliable equipment quality with good warranty support.",
            "Effective project management with good communication."
        ])
    elif score >= 7.0:
        return random.choice([
            "Good installation quality with some minor rework required.",
            "Satisfactory adherence to specifications with occasional clarifications needed.",
            "Meets expectations for system performance with some optimization potential.",
            "Generally reliable on schedule with occasional delays.",
            "Acceptable safety procedures with room for improvement."
        ])
    elif score >= 5.0:
        return random.choice([
            "Average installation quality with several deficiencies requiring correction.",
            "Some technical issues with equipment and system integration.",
            "Performance below target on project schedule adherence.",
            "Multiple RFIs and change orders requiring attention.",
            "Quality inconsistencies between different installation areas."
        ])
    else:
        return random.choice([
            "Significant system performance issues requiring remediation.",
            "Multiple code compliance and specification deviation issues.",
            "Substantial delays impacting overall project schedule.",
            "Poor coordination with other trades causing conflicts.",
            "Serious quality control and safety procedure concerns."
        ])
