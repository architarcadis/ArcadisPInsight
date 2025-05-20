import pandas as pd
import numpy as np
from io import BytesIO

def load_data(file, file_type=None):
    """
    Load data from uploaded file
    
    Parameters:
    file: The uploaded file object
    file_type: The type of file (csv or excel)
    
    Returns:
    pd.DataFrame: The loaded data
    """
    if file_type is None:
        # Try to infer file type from name
        if file.name.endswith('.csv'):
            file_type = 'csv'
        elif file.name.endswith('.xlsx'):
            file_type = 'excel'
        else:
            raise ValueError("Unsupported file type. Please upload a CSV or Excel file.")
    
    if file_type == 'csv':
        return pd.read_csv(file)
    elif file_type == 'excel':
        return pd.read_excel(file)
    else:
        raise ValueError("Unsupported file type. Please upload a CSV or Excel file.")

def validate_data(file, data_type):
    """
    Validate uploaded data based on expected structure for data type
    
    Parameters:
    file: The uploaded file object
    data_type: The type of data being uploaded (Spend Data, Supplier Master, etc.)
    
    Returns:
    tuple: (is_valid, message, data)
    """
    try:
        # Determine file type from extension
        file_type = None
        if file.name.endswith('.csv'):
            file_type = 'csv'
        elif file.name.endswith('.xlsx'):
            file_type = 'excel'
        else:
            return False, "Unsupported file type. Please upload a CSV or Excel file.", None
        
        # Load the data
        data = load_data(file, file_type)
        
        # Validate based on data type
        if data_type == "Spend Data":
            required_columns = ['Supplier', 'Category', 'SubCategory', 'BusinessUnit', 'Date', 'Amount']
            missing_columns = [col for col in required_columns if col not in data.columns]
            
            if missing_columns:
                return False, f"Missing required columns: {', '.join(missing_columns)}", None
            
            # Check data types
            if not pd.api.types.is_numeric_dtype(data['Amount']):
                return False, "Amount column must contain numeric values", None
            
            # Check for null values in critical columns
            null_suppliers = data['Supplier'].isnull().sum()
            if null_suppliers > 0:
                return False, f"Found {null_suppliers} rows with missing supplier information", None
        
        elif data_type == "Supplier Master Data":
            required_columns = ['SupplierID', 'SupplierName', 'Category', 'Country', 'City', 'ContactEmail']
            missing_columns = [col for col in required_columns if col not in data.columns]
            
            if missing_columns:
                return False, f"Missing required columns: {', '.join(missing_columns)}", None
        
        elif data_type == "Contract Data":
            required_columns = ['ContractID', 'SupplierID', 'StartDate', 'EndDate', 'Value', 'Category']
            missing_columns = [col for col in required_columns if col not in data.columns]
            
            if missing_columns:
                return False, f"Missing required columns: {', '.join(missing_columns)}", None
        
        elif data_type == "Performance Data":
            required_columns = ['SupplierID', 'Quarter', 'DeliveryScore', 'QualityScore', 'ResponsivenessScore', 'OverallScore']
            missing_columns = [col for col in required_columns if col not in data.columns]
            
            if missing_columns:
                return False, f"Missing required columns: {', '.join(missing_columns)}", None
        
        # If we reach here, validation passed
        return True, "Data validated successfully", data
    
    except Exception as e:
        return False, f"Error during validation: {str(e)}", None
