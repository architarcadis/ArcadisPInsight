import pandas as pd
import streamlit as st
from io import BytesIO
import base64

def get_template_download_button(template_type):
    """
    Create and display a download button for the selected template type
    
    Parameters:
    template_type: The type of template to generate
    """
    template_file = create_template(template_type)
    
    file_extension = "xlsx"
    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    file_name = template_type.replace(" ", "_").lower() + f".{file_extension}"
    
    b64 = base64.b64encode(template_file.getvalue()).decode()
    href = f'<a href="data:{mime_type};base64,{b64}" download="{file_name}">Download {template_type}</a>'
    
    st.sidebar.markdown(href, unsafe_allow_html=True)
    st.sidebar.info("👆 Click above to download the template file")

def create_template(template_type):
    """
    Create an Excel template file based on the specified type
    
    Parameters:
    template_type: The type of template to create
    
    Returns:
    BytesIO: An in-memory Excel file
    """
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Create instructions sheet
        instructions_df = create_instructions_sheet(template_type)
        instructions_df.to_excel(writer, sheet_name='Instructions', index=False)
        
        # Create data entry sheet with example data
        example_df = create_example_data(template_type)
        example_df.to_excel(writer, sheet_name='Data_Entry_Sheet', index=False)
    
    output.seek(0)
    return output

def create_instructions_sheet(template_type):
    """
    Create the instructions dataframe for the template
    
    Parameters:
    template_type: The type of template to create instructions for
    
    Returns:
    pd.DataFrame: A dataframe with instructions
    """
    if template_type == "Spend Data Template":
        instructions = [
            ["Purpose", "Use this template to upload your organization's spend data for analysis in the Arcadis Procure Insights platform."],
            ["", ""],
            ["Column Definitions", ""],
            ["Supplier", "Text - Full legal name of the supplier. E.g., 'Acme Corp'", "Required"],
            ["Category", "Text - Primary procurement category. E.g., 'IT Hardware', 'Office Supplies'", "Required"],
            ["SubCategory", "Text - More specific category. E.g., 'Laptops', 'Desktops'", "Required"],
            ["BusinessUnit", "Text - Internal business unit or department. E.g., 'Finance', 'Marketing'", "Required"],
            ["Date", "Date (YYYY-MM-DD) - Transaction date", "Required"],
            ["Amount", "Numeric - Transaction amount without currency symbol", "Required"],
            ["InvoiceID", "Text - Unique invoice identifier", "Optional"],
            ["POID", "Text - Purchase order identifier", "Optional"],
            ["PaymentTerms", "Text - Payment terms. E.g., 'Net 30', 'Net 45'", "Optional"],
            ["Currency", "Text - 3-letter currency code. E.g., 'USD', 'EUR'", "Optional"],
            ["", ""],
            ["Formatting Notes", "Ensure dates are in YYYY-MM-DD format. Currency should be in decimal format without symbols."],
            ["Data Quality Tips", "Ensure no blank required fields. Check for consistent supplier naming."]
        ]
    
    elif template_type == "Invoice Data Template":
        instructions = [
            ["Purpose", "Use this template to upload your organization's invoice data for analysis in the Arcadis Procure Insights platform."],
            ["", ""],
            ["Column Definitions", ""],
            ["InvoiceID", "Text - Unique invoice identifier", "Required"],
            ["Supplier", "Text - Full legal name of the supplier", "Required"],
            ["InvoiceDate", "Date (YYYY-MM-DD) - Date invoice was issued", "Required"],
            ["DueDate", "Date (YYYY-MM-DD) - Date payment is due", "Required"],
            ["Amount", "Numeric - Invoice amount without currency symbol", "Required"],
            ["Currency", "Text - 3-letter currency code. E.g., 'USD', 'EUR'", "Required"],
            ["POID", "Text - Associated purchase order identifier", "Optional"],
            ["Status", "Text - Invoice status. E.g., 'Paid', 'Pending', 'Overdue'", "Optional"],
            ["PaymentDate", "Date (YYYY-MM-DD) - Date invoice was paid (if applicable)", "Optional"],
            ["Category", "Text - Procurement category", "Optional"],
            ["BusinessUnit", "Text - Internal business unit or department", "Optional"],
            ["", ""],
            ["Formatting Notes", "Ensure dates are in YYYY-MM-DD format. Currency should be in decimal format without symbols."],
            ["Data Quality Tips", "Ensure InvoiceID is unique. Check for consistent supplier naming."]
        ]
    
    elif template_type == "Supplier Master Data Template":
        instructions = [
            ["Purpose", "Use this template to upload your organization's supplier master data for analysis in the Arcadis Procure Insights platform."],
            ["", ""],
            ["Column Definitions", ""],
            ["SupplierID", "Text - Unique supplier identifier", "Required"],
            ["SupplierName", "Text - Full legal name of the supplier", "Required"],
            ["Category", "Text - Primary procurement category", "Required"],
            ["Country", "Text - Country where supplier is based", "Required"],
            ["City", "Text - City where supplier is based", "Required"],
            ["ContactName", "Text - Primary contact person", "Optional"],
            ["ContactEmail", "Text - Email address for primary contact", "Optional"],
            ["ContactPhone", "Text - Phone number for primary contact", "Optional"],
            ["AnnualRevenue", "Numeric - Supplier's annual revenue (if known)", "Optional"],
            ["PaymentTerms", "Text - Standard payment terms. E.g., 'Net 30'", "Optional"],
            ["Active", "Boolean (TRUE/FALSE) - Whether supplier is currently active", "Optional"],
            ["RelationshipStartDate", "Date (YYYY-MM-DD) - When relationship began", "Optional"],
            ["", ""],
            ["Formatting Notes", "Ensure dates are in YYYY-MM-DD format. Boolean values should be TRUE or FALSE."],
            ["Data Quality Tips", "Ensure SupplierID is unique. Check for consistent category naming."]
        ]
    
    elif template_type == "Contract Data Template":
        instructions = [
            ["Purpose", "Use this template to upload your organization's contract data for analysis in the Arcadis Procure Insights platform."],
            ["", ""],
            ["Column Definitions", ""],
            ["ContractID", "Text - Unique contract identifier", "Required"],
            ["SupplierID", "Text - Supplier identifier (should match Supplier Master Data)", "Required"],
            ["SupplierName", "Text - Full legal name of the supplier", "Required"],
            ["Category", "Text - Procurement category", "Required"],
            ["ContractType", "Text - Type of contract. E.g., 'Product', 'Service'", "Required"],
            ["StartDate", "Date (YYYY-MM-DD) - Contract start date", "Required"],
            ["EndDate", "Date (YYYY-MM-DD) - Contract end date", "Required"],
            ["Value", "Numeric - Total contract value without currency symbol", "Required"],
            ["Currency", "Text - 3-letter currency code. E.g., 'USD', 'EUR'", "Required"],
            ["Status", "Text - Contract status. E.g., 'Active', 'Expired', 'Future'", "Optional"],
            ["AutoRenewal", "Boolean (TRUE/FALSE) - Whether contract auto-renews", "Optional"],
            ["NoticePeriodDays", "Numeric - Days required for termination notice", "Optional"],
            ["", ""],
            ["Formatting Notes", "Ensure dates are in YYYY-MM-DD format. Boolean values should be TRUE or FALSE."],
            ["Data Quality Tips", "Ensure ContractID is unique. EndDate should be after StartDate."]
        ]
    
    elif template_type == "Supplier Performance Data Template":
        instructions = [
            ["Purpose", "Use this template to upload your organization's supplier performance data for analysis in the Arcadis Procure Insights platform."],
            ["", ""],
            ["Column Definitions", ""],
            ["SupplierID", "Text - Supplier identifier (should match Supplier Master Data)", "Required"],
            ["Quarter", "Text - Evaluation period in YYYY-QX format. E.g., '2023-Q1'", "Required"],
            ["DeliveryScore", "Numeric (1-10) - Score for on-time delivery performance", "Required"],
            ["QualityScore", "Numeric (1-10) - Score for quality of products/services", "Required"],
            ["ResponsivenessScore", "Numeric (1-10) - Score for responsiveness to inquiries", "Required"],
            ["OverallScore", "Numeric (1-10) - Overall performance score", "Required"],
            ["Comments", "Text - Additional notes on performance", "Optional"],
            ["", ""],
            ["Scoring Guide", "1-3: Poor, 4-6: Average, 7-8: Good, 9-10: Excellent"],
            ["Formatting Notes", "Scores should be between 1 and 10, with up to one decimal place precision."],
            ["Data Quality Tips", "Ensure SupplierID exists in your Supplier Master Data. Quarter should follow YYYY-QX format."]
        ]
    
    # Create dataframe with instructions
    return pd.DataFrame(instructions)

def create_example_data(template_type):
    """
    Create example data for the template
    
    Parameters:
    template_type: The type of template to create example data for
    
    Returns:
    pd.DataFrame: A dataframe with example data
    """
    if template_type == "Spend Data Template":
        data = {
            "Supplier": ["Acme Supplies", "GlobalTech Solutions", "Midwest Materials"],
            "Category": ["Office Supplies", "IT Software", "Raw Materials"],
            "SubCategory": ["Paper Products", "CRM Software", "Metals"],
            "BusinessUnit": ["Marketing", "IT", "Operations"],
            "Date": ["2023-01-15", "2023-02-10", "2023-03-22"],
            "Amount": [1250.00, 15000.00, 7500.00],
            "InvoiceID": ["INV-12345", "INV-23456", "INV-34567"],
            "POID": ["PO-45678", "PO-56789", "PO-67890"],
            "PaymentTerms": ["Net 30", "Net 45", "Net 60"],
            "Currency": ["USD", "USD", "USD"]
        }
    
    elif template_type == "Invoice Data Template":
        data = {
            "InvoiceID": ["INV-12345", "INV-23456", "INV-34567"],
            "Supplier": ["Acme Supplies", "GlobalTech Solutions", "Midwest Materials"],
            "InvoiceDate": ["2023-01-15", "2023-02-10", "2023-03-22"],
            "DueDate": ["2023-02-14", "2023-03-27", "2023-05-21"],
            "Amount": [1250.00, 15000.00, 7500.00],
            "Currency": ["USD", "USD", "USD"],
            "POID": ["PO-45678", "PO-56789", "PO-67890"],
            "Status": ["Paid", "Pending", "Overdue"],
            "PaymentDate": ["2023-02-10", "", ""],
            "Category": ["Office Supplies", "IT Software", "Raw Materials"],
            "BusinessUnit": ["Marketing", "IT", "Operations"]
        }
    
    elif template_type == "Supplier Master Data Template":
        data = {
            "SupplierID": ["S0001", "S0002", "S0003"],
            "SupplierName": ["Acme Supplies", "GlobalTech Solutions", "Midwest Materials"],
            "Category": ["Office Supplies", "IT Software", "Raw Materials"],
            "Country": ["USA", "USA", "USA"],
            "City": ["Chicago", "San Francisco", "Detroit"],
            "ContactName": ["John Smith", "Jane Johnson", "Robert Williams"],
            "ContactEmail": ["john.smith@acmesupplies.com", "jane.johnson@globaltechsolutions.com", "robert.williams@midwestmaterials.com"],
            "ContactPhone": ["+1-312-555-1234", "+1-415-555-6789", "+1-313-555-4321"],
            "AnnualRevenue": [5000000, 25000000, 12000000],
            "PaymentTerms": ["Net 30", "Net 45", "Net 60"],
            "Active": [True, True, True],
            "RelationshipStartDate": ["2018-06-15", "2020-02-10", "2017-11-22"]
        }
    
    elif template_type == "Contract Data Template":
        data = {
            "ContractID": ["C0001", "C0002", "C0003"],
            "SupplierID": ["S0001", "S0002", "S0003"],
            "SupplierName": ["Acme Supplies", "GlobalTech Solutions", "Midwest Materials"],
            "Category": ["Office Supplies", "IT Software", "Raw Materials"],
            "ContractType": ["Product", "Service", "Product"],
            "StartDate": ["2022-01-01", "2023-01-01", "2022-06-01"],
            "EndDate": ["2024-12-31", "2025-12-31", "2025-05-31"],
            "Value": [120000, 500000, 300000],
            "Currency": ["USD", "USD", "USD"],
            "Status": ["Active", "Active", "Active"],
            "AutoRenewal": [False, True, False],
            "NoticePeriodDays": [60, 90, 30]
        }
    
    elif template_type == "Supplier Performance Data Template":
        data = {
            "SupplierID": ["S0001", "S0002", "S0003"],
            "Quarter": ["2023-Q1", "2023-Q1", "2023-Q1"],
            "DeliveryScore": [8.5, 9.0, 7.2],
            "QualityScore": [9.0, 8.5, 7.5],
            "ResponsivenessScore": [8.0, 9.5, 8.0],
            "OverallScore": [8.6, 8.9, 7.5],
            "Comments": ["Consistent high quality delivery", "Excellent service and responsiveness", "Some delivery delays, quality adequate"]
        }
    
    return pd.DataFrame(data)
