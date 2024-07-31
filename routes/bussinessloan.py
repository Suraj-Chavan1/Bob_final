import functools
import json
import os
import ssl
import pyodbc
import uuid
import logging
import requests

from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import FormRecognizerClient


# Load credentials
API_KEY01 = '6e5535613cc84907b74b2a18da9db57c'
ENDPOINT01 = 'https://cyberwardensserver.cognitiveservices.azure.com/'



server = 'cbnewbase.database.windows.net'
database = 'bobdb'
username = 'suraj'
password = 'cyberwardens123@'
connection_string = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};Trusted_Connection=no;'

# Establish the database connection
conn = pyodbc.connect(connection_string)

# Initialize the Form Recognizer client
form_recognizer_client = FormRecognizerClient(ENDPOINT01, AzureKeyCredential(API_KEY01))

def convert_to_numeric(value):
    """
    Converts a string to a numeric value (int or float) if possible.
    Returns the original value if conversion is not possible.
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value

def parse_line(line):
    """ Parses a line of text into a key-value pair. """
    if ':' in line:
        key, value = line.split(':', 1)
        return key.strip(), value.strip()
    return None, None

def parse_table_cells(cells):
    """ Parses table cells into key-value pairs assuming alternating cells for keys and values. """
    key_value_pairs = {}
    row_data = []
    for cell in cells:
        row_data.append(cell.text.strip())
        if len(row_data) == 2:
            key_value_pairs[row_data[0]] = row_data[1]
            row_data = []
    return key_value_pairs

def form_ocr(link):
    """ Performs OCR on the form image at the given link and extracts key-value pairs. """
    if not link:
        return {"error": "No link provided"}, 400
    
    try:
        poller = form_recognizer_client.begin_recognize_content_from_url(link)
        form_result = poller.result()
        
        key_value_pairs = {}
        current_key = None
        
        for page in form_result:
            # Extract lines of text
            for line in page.lines:
                text = line.text.strip()
                if text:
                    if current_key is None:
                        if ':' in text:
                            key, value = parse_line(text)
                            if key and value:
                                key_value_pairs[key] = value
                            else:
                                current_key = text
                        else:
                            current_key = text
                    else:
                        key_value_pairs[current_key] = text
                        current_key = None

            # Extract table data
            for table in page.tables:
                cells = [cell for cell in table.cells]
                table_data = parse_table_cells(cells)
                key_value_pairs.update(table_data)

        return key_value_pairs

    except Exception as e:
        logging.error(f'Error: {e}')
        return {"error": str(e)}, 500

def allow_self_signed_https(allowed):
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allow_self_signed_https(True)

def calculate_loan_ratios(data):
    ratios = {
        "Current Ratio": data["current_assets"] / data["current_liabilities"],
        "Quick Ratio": (data["current_assets"] - data["inventory"]) / data["current_liabilities"],
        "Debt-to-Equity Ratio": data["total_debt"] / data["total_equity"],
        "Debt Ratio": data["total_debt"] / data["total_assets"],
        "Net Profit Margin": data["net_income"] / data["net_sales"],
        "Return on Assets (ROA)": data["net_income"] / data["total_assets"],
        "Return on Equity (ROE)": data["net_income"] / data["total_equity"],
        "Interest Coverage Ratio": data["ebit"] / data["interest_expense"],
        "Operating Cash Flow to Total Debt Ratio": data["operating_cash_flow"] / data["total_debt"],
        "Free Cash Flow to Firm (FCFF)": data["operating_cash_flow"] - data["capital_expenditures"]
    }
    return ratios

def insert_into_db(data, ratios, result_data, user_id):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        create_table_sql = '''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='BusinessLoanApplication' and xtype='U')
        CREATE TABLE BusinessLoanApplication (
            application_id INT IDENTITY(1,1) PRIMARY KEY,
            company_name NVARCHAR(100),
            auditing_company_name NVARCHAR(100),
            current_assets FLOAT,
            current_liabilities FLOAT,
            inventory FLOAT,
            total_debt FLOAT,
            total_equity FLOAT,
            total_assets FLOAT,
            net_income FLOAT,
            net_sales FLOAT,
            ebit FLOAT,
            interest_expense FLOAT,
            operating_cash_flow FLOAT,
            capital_expenditures FLOAT,
            Current_Ratio FLOAT,
            Quick_Ratio FLOAT,
            Debt_to_Equity_Ratio FLOAT,
            Debt_Ratio FLOAT,
            Net_Profit_Margin FLOAT,
            Return_on_Assets FLOAT,
            Return_on_Equity FLOAT,
            Interest_Coverage_Ratio FLOAT,
            Operating_Cash_Flow_to_Total_Debt_Ratio FLOAT,
            Free_Cash_Flow_to_Firm FLOAT,
            User_id VARCHAR(50),
            Status NVARCHAR(50) DEFAULT 'Processing',
            result INT,
            created_at DATETIME DEFAULT (GETDATE() AT TIME ZONE 'UTC' AT TIME ZONE 'India Standard Time')
        )
        '''
        cursor.execute(create_table_sql)

        insert_values_sql = '''
        INSERT INTO BusinessLoanApplication (
            company_name, auditing_company_name, current_assets, current_liabilities, inventory, total_debt,
            total_equity, total_assets, net_income, net_sales, ebit, interest_expense, operating_cash_flow, capital_expenditures,
            Current_Ratio, Quick_Ratio, Debt_to_Equity_Ratio, Debt_Ratio, Net_Profit_Margin, Return_on_Assets, Return_on_Equity,
            Interest_Coverage_Ratio, Operating_Cash_Flow_to_Total_Debt_Ratio, Free_Cash_Flow_to_Firm, result, User_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(insert_values_sql, data["company_name"], data["auditing_company_name"], data["current_assets"],
                       data["current_liabilities"], data["inventory"], data["total_debt"], data["total_equity"], data["total_assets"],
                       data["net_income"], data["net_sales"], data["ebit"], data["interest_expense"], data["operating_cash_flow"],
                       data["capital_expenditures"], ratios["Current Ratio"], ratios["Quick Ratio"], ratios["Debt-to-Equity Ratio"],
                       ratios["Debt Ratio"], ratios["Net Profit Margin"], ratios["Return on Assets (ROA)"], ratios["Return on Equity (ROE)"],
                       ratios["Interest Coverage Ratio"], ratios["Operating Cash Flow to Total Debt Ratio"], ratios["Free Cash Flow to Firm (FCFF)"],
                       data.get("result", result_data), user_id)

        conn.commit()
    except pyodbc.Error as ex:
        sqlstate = ex.args[1]
        logging.error(f"Error connecting to database: {sqlstate}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

bl = Blueprint('bussinessloan', __name__, url_prefix='/bussinessloan')

@bl.route('/calculate_and_send', methods=['POST'])
def calculate_and_send():
    data = request.json
    user_id = data.get('user_id')
    link = data.get("link")
    result_data = form_ocr(link)
    if "error" in result_data:
        return jsonify(result_data), 400

    mapped_data = {
        "company_name": result_data.get('Customer Name:', ''),
        "auditing_company_name": result_data.get('Auditing Company Name:', ''),
        "current_assets": convert_to_numeric(result_data.get('Current Assets', '0')),
        "current_liabilities": convert_to_numeric(result_data.get('Current Liabilities', '0')),
        "inventory": convert_to_numeric(result_data.get('Inventory:', '0')),
        "total_debt": convert_to_numeric(result_data.get('Total Debt:', '0')),
        "total_equity": convert_to_numeric(result_data.get('Total Equity:', '0')),
        "total_assets": convert_to_numeric(result_data.get('Total Assets:', '0')),
        "net_income": convert_to_numeric(result_data.get('Net Income:', '0')),
        "net_sales": convert_to_numeric(result_data.get('Net Sales:', '0')),
        "ebit": convert_to_numeric(result_data.get('EBIT:', '0')),
        "interest_expense": convert_to_numeric(result_data.get('Interest Expense:', '0')),
        "operating_cash_flow": convert_to_numeric(result_data.get('Operating Cash Flow:', '0')),
        "capital_expenditures": convert_to_numeric(result_data.get('Capital Expenditure:', '0'))
    }

    # Calculate the ratios
    ratios = calculate_loan_ratios(mapped_data)
    
    # Generate a unique application ID
    application_id = str(uuid.uuid4())
    
    # Prepare data for Azure endpoint
    azure_data = {
        "input_data": {
            "columns": [
                "Customer_id", "Company_name", "Auditing_Company_Name", "Current_Ratio", "Quick_Ratio", 
                "Debt_to_Equity_Ratio", "Debt_Ratio", "Net_Profit_Margin", "Return_on_Assets (ROA)",
                "Return_on_Equity (ROE)", "Interest_Coverage_Ratio", "Operating_Cash_Flow_to_Total_Debt_Ratio",
                "Free_Cash_Flow_to_Firm (FCFF)"
            ],
            "index": [1],
            "data": [
                [1, mapped_data["company_name"], mapped_data["auditing_company_name"], ratios["Current Ratio"], 
                ratios["Quick Ratio"], ratios["Debt-to-Equity Ratio"], ratios["Debt Ratio"], 
                ratios["Net Profit Margin"], ratios["Return on Assets (ROA)"], ratios["Return on Equity (ROE)"], 
                ratios["Interest Coverage Ratio"], ratios["Operating Cash Flow to Total Debt Ratio"], 
                ratios["Free Cash Flow to Firm (FCFF)"]]
            ]
        }
    }

    try:
        response = requests.post(
            'https://bld9502.australiaeast.inference.ml.azure.com/score',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer w5bMDNR5OMFhRWEf3p8KCdNCk5WUGMWi',
                'azureml-model-deployment': 'bld9502'
            },
            json=azure_data
        )
        response.raise_for_status()
        result = response.json()
        print(result[0])
        insert_into_db( mapped_data, ratios, result[0], user_id)
        return jsonify({"application_id": application_id, "UserID": user_id, "ratios": ratios, "azure_response": result}), 200
    except requests.exceptions.RequestException as error:
        logging.error(f'Error sending request to Azure: {error}')
        return jsonify({"error": str(error)}), 500

@bl.route('/user_to_data', methods=['GET'])
def get_loan_application():
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    try:
        # Establish the database connection
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT application_id, company_name, auditing_company_name , Status
            FROM BusinessLoanApplication
            WHERE User_id = ?
        """, user_id)
        
        rows = cursor.fetchall()
        if rows:
            columns = [column[0] for column in cursor.description]
            result = [dict(zip(columns, row)) for row in rows]
            return jsonify(result)
        else:
            return jsonify({'message': 'No data found for the provided User ID'}), 404

    except Exception as e:
        # Log the exception to the console for debugging
        logging.error(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals() and conn:
            conn.close()

@bl.route('/all_loans', methods=['GET'])
def all_loans():
    try:
        # Establish the database connection
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM BusinessLoanApplication
        """)
        
        rows = cursor.fetchall()
        if rows:
            columns = [column[0] for column in cursor.description]
            result = [dict(zip(columns, row)) for row in rows]
            return jsonify(result)
        else:
            return jsonify({'message': 'No data found'}), 404

    except Exception as e:
        # Log the exception to the console for debugging
        logging.error(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        if 'conn' in locals() and conn:
            conn.close()

@bl.route('/get_data_from_applicationid/<application_id>', methods=['GET'])
def get_data_from_applicationid(application_id):
    try:
        # Establish the database connection
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Use the application_id to fetch the specific loan application
        cursor.execute("""
            SELECT * FROM BusinessLoanApplication WHERE application_id = ?
        """, application_id)
        
        row = cursor.fetchone()
        if row:
            columns = [column[0] for column in cursor.description]
            result = dict(zip(columns, row))
            return jsonify(result)
        else:
            return jsonify({'message': 'No data found'}), 404

    except Exception as e:
        # Log the exception to the console for debugging
        logging.error(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        if 'conn' in locals() and conn:
            conn.close()
@bl.route('/set_to_rejected/<application_id>', methods=['POST'])  # Use POST method for updates
def set_to_rejected(application_id):
    try:
        # Establish the database connection
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Update the status to 'rejected' for the specified application_id
        cursor.execute("""
            UPDATE BusinessLoanApplication
            SET Status = 'rejected'
            WHERE application_id = ?
        """, application_id)
        
        # Commit the transaction
        conn.commit()
        
        # Check if any row was updated
        if cursor.rowcount > 0:
            return jsonify({'message': 'Application status updated to rejected'}), 200
        else:
            return jsonify({'message': 'No data found'}), 404

    except Exception as e:
        # Log the exception to the console for debugging
        logging.error(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        if 'conn' in locals() and conn:
            conn.close()

@bl.route('/set_to_accepted/<application_id>', methods=['POST'])
def set_to_accepted(application_id):
    try:
        # Establish the database connection
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Update the status to 'accepted' for the specified application_id
        cursor.execute("""
            UPDATE BusinessLoanApplication
            SET Status = 'accepted'
            WHERE application_id = ?
        """, application_id)
        
        # Commit the transaction
        conn.commit()
        
        # Check if any row was updated
        if cursor.rowcount > 0:
            return jsonify({'message': 'Application status updated to accepted'}), 200
        else:
            return jsonify({'message': 'No data found for the provided application ID'}), 404

    except Exception as e:
        # Log the exception to the console for debugging
        logging.error(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        if 'conn' in locals() and conn:
            conn.close()
