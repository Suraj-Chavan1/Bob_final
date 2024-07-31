import urllib.request
import json
import os
import ssl
import pyodbc
import uuid
from flask import Flask, request, jsonify, Blueprint
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import FormRecognizerClient
import logging


ploan = Blueprint('personalloan', __name__, url_prefix='/personalloan')

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Load credentials
API_KEY01 = '6e5535613cc84907b74b2a18da9db57c'
ENDPOINT01 = 'https://cyberwardensserver.cognitiveservices.azure.com/'

# Initialize the Form Recognizer client
form_recognizer_client = FormRecognizerClient(ENDPOINT01, AzureKeyCredential(API_KEY01))

def convert_to_numeric(value):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value

def parse_line(line):
    if ':' in line:
        key, value = line.split(':', 1)
        return key.strip(), value.strip()
    return None, None

def parse_table_cells(cells):
    key_value_pairs = {}
    row_data = []
    for cell in cells:
        row_data.append(cell.text.strip())
        if len(row_data) == 2:
            key_value_pairs[row_data[0]] = row_data[1]
            row_data = []
    return key_value_pairs

def form_ocr(link):
    if not link:
        return {"error": "No link provided"}, 400
    
    try:
        poller = form_recognizer_client.begin_recognize_content_from_url(link)
        form_result = poller.result()
        
        key_value_pairs = {}
        current_key = None
        
        for page in form_result:
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

            for table in page.tables:
                cells = []
                for cell in table.cells:
                    cells.append(cell)
                table_data = parse_table_cells(cells)
                key_value_pairs.update(table_data)

        return key_value_pairs

    except Exception as e:
        logging.error(f'Error: {e}')
        return {"error": str(e)}, 500

def allowSelfSignedHttps(allowed):
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True)

def make_api_request(data):
    body = str.encode(json.dumps(data))
    url = 'http://18bbb702-6e45-4800-a7b4-288c0ead5eed.australiaeast.azurecontainer.io/score'
    headers = {'Content-Type': 'application/json'}
    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)
        result = response.read()
        return json.loads(result)
    except urllib.error.HTTPError as error:
        logging.error(f"The request failed with status code: {error.code}")
        logging.error(error.info())
        logging.error(error.read().decode("utf8", 'ignore'))
        return None



server = 'cbnewbase.database.windows.net'
database = 'bobdb'
username = 'suraj'
password = 'cyberwardens123@'
connection_string = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};Trusted_Connection=no;'

def connect_to_db():
    server = 'cbnewbase.database.windows.net'
    database = 'bobdb'
    username = 'suraj'
    password = 'cyberwardens123@'
    connection_string = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};Trusted_Connection=no;'

    try:
        conn = pyodbc.connect(connection_string)
        logging.info("Connection established successfully!")
        return conn
    except Exception as e:
        logging.error(f"Failed to connect to database: {e}")
        return None

def create_table(conn):
    cursor = conn.cursor()
    create_table_sql = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='PersonalApplication' AND xtype='U')
    CREATE TABLE PersonalApplication (
        Application_id INT IDENTITY(1,1) PRIMARY KEY,
        Customer_ID INT,
        Name NVARCHAR(100),
        Age INT,
        Occupation NVARCHAR(50),
        Annual_Income FLOAT,
        Monthly_Inhand_Salary FLOAT,
        Num_Bank_Accounts INT,
        Num_Credit_Card INT,
        Interest_Rate INT,
        Num_of_Loan INT,
        Delay_from_due_date INT,
        Num_of_Delayed_Payment INT,
        Changed_Credit_Limit FLOAT,
        Num_Credit_Inquiries INT,
        Outstanding_Debt FLOAT,
        Credit_Utilization_Ratio FLOAT,
        Credit_History_Age INT,
        Total_EMI_per_month FLOAT,
        Amount_invested_monthly FLOAT,
        Monthly_Balance FLOAT,
        Applied_date_time DATETIME DEFAULT (GETDATE() AT TIME ZONE 'UTC' AT TIME ZONE 'India Standard Time'),
        Status NVARCHAR(50),
        Result VARCHAR(100),
        Message_to_User NVARCHAR(MAX),
        Type_of_Loan NVARCHAR(50)
    
    )
    """
    cursor.execute(create_table_sql)
    conn.commit()
    logging.info("Table created successfully!")

def insert_data(conn, customer_data, status, result, message_to_user,Type_of_Loan="Personal Loan"):
    cursor = conn.cursor()
    insert_sql = """
    INSERT INTO PersonalApplication (
        Customer_ID, Name, Age, Occupation, Annual_Income, Monthly_Inhand_Salary,
        Num_Bank_Accounts, Num_Credit_Card, Interest_Rate, Num_of_Loan, Delay_from_due_date,
        Num_of_Delayed_Payment, Changed_Credit_Limit, Num_Credit_Inquiries, Outstanding_Debt,
        Credit_Utilization_Ratio, Credit_History_Age, Total_EMI_per_month, Amount_invested_monthly,
        Monthly_Balance, Status, Result, Message_to_User, Type_of_Loan
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(insert_sql, (
        customer_data["Customer_ID"], customer_data["Name"], customer_data["Age"],
        customer_data["Occupation"], customer_data["Annual_Income"], customer_data["Monthly_Inhand_Salary"],
        customer_data["Num_Bank_Accounts"], customer_data["Num_Credit_Card"], customer_data["Interest_Rate"],
        customer_data["Num_of_Loan"], customer_data["Delay_from_due_date"], customer_data["Num_of_Delayed_Payment"],
        customer_data["Changed_Credit_Limit"], customer_data["Num_Credit_Inquiries"], customer_data["Outstanding_Debt"],
        customer_data["Credit_Utilization_Ratio"], customer_data["Credit_History_Age"], customer_data["Total_EMI_per_month"],
        customer_data["Amount_invested_monthly"], customer_data["Monthly_Balance"], status, result, message_to_user, Type_of_Loan
    ))
    conn.commit()
    logging.info("Data inserted successfully!")

@ploan.route('/ploan', methods=['POST'])
def submit():
    data = request.json
    application_idjson = None
    type_of_loan = data.get('type_of_loan')
    link = data.get('link')
    result = form_ocr(link)
    print(result)
    
    if 'error' in result:
        return jsonify(result), 400

    try:
        request_data = {
            "customer_data": {
                "Customer_ID": int(result['Customer ID:']),
                "Name": result['Customer Name:'],
                "Age": int(result['Customer Age:']),
                "Occupation": result['Occupation:'],
                "Annual_Income": float(result['Annual Income:']),
                "Monthly_Inhand_Salary": float(result['Monthly In-hand Salary:']),
                "Num_Bank_Accounts": int(result['Number of Bank Accounts:']),
                "Num_Credit_Card": int(result['Number of Credit Cards:']),
                "Interest_Rate": float(result['Interest Rate:']),
                "Num_of_Loan": int(result['Number of Loans:']),
                "Delay_from_due_date": int(result['Delay from Due Date:']),
                "Num_of_Delayed_Payment": int(result['Number of Delayed Payments:']),
                "Changed_Credit_Limit": float(result['Changed Credit Limit:']),
                "Num_Credit_Inquiries": int(result['Number of Credit Inquiries:']),
                "Outstanding_Debt": float(result['Outstanding Debt:']),
                "Credit_Utilization_Ratio": float(result['Credit Utilization Ratio:']),
                "Credit_History_Age": int(result['Credit History Age:']),
                "Total_EMI_per_month": float(result['Total EMI per month:']),
                "Amount_invested_monthly": float(result['Amount Invested Monthly:']),
                "Monthly_Balance": float(result['Monthly Balance:'])
            }
        }
    except KeyError as e:
        logging.error(f'Missing key in OCR result: {e}')
        return jsonify({"error": f"Missing required field in OCR result: {e}"}), 400

    if not all([ request_data['customer_data']]):
        return jsonify({"error": "Missing required fields"}), 400

    request_data_payload = {
        "Inputs": {
            "data": [request_data['customer_data']]
        },
        "GlobalParameters": {
            "method": "predict"
        }
    }

    response_data = make_api_request(request_data_payload)

    if response_data:
        status = "Success"
        result = json.dumps(response_data)
        message_to_user = "Request processed successfully."
    else:
        status = "Failure"
        result = ""
        message_to_user = "Failed to process request."

    conn = connect_to_db()
    data_result_form_json = json.loads(result)


    if conn:
        create_table(conn)
        try:
            insert_data(conn , request_data['customer_data'], status, data_result_form_json["Results"][0], message_to_user,type_of_loan)
        except Exception as e:
            logging.error(f'Failed to insert data: {e}')
            return jsonify({"error": "Failed to insert data"}), 500
        finally:
            conn.close()
        return jsonify({"application_id": application_idjson, "result": response_data["Results"][0], "coloumn_data": request_data['customer_data'], "Type_of_loan": type_of_loan}), 200
    else:
        return jsonify({"error": "Failed to connect to database"}), 500
    
    
    
@ploan.route('/get_customer_info', methods=['GET'])
def get_customer_info():
    customer_id = request.args.get('Customer_ID')
    
    if not customer_id:
        return jsonify({'error': 'Customer_ID is required'}), 400

    try:
        # Establish the database connection
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Application_id, Name, Occupation, Status ,Type_of_Loan
            FROM PersonalApplication
            WHERE Customer_ID = ?
        """, customer_id)
        
        rows = cursor.fetchall()
        if rows:
            columns = [column[0] for column in cursor.description]
            result = [dict(zip(columns, row)) for row in rows]
            return jsonify(result)
        else:
            return jsonify({'message': 'No data found for the provided Customer_ID'}), 404

    except Exception as e:
        # Log the exception to the console for debugging
        logging.error(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals() and conn:
            conn.close()


@ploan.route('/all_loans', methods=['GET'])
def all_loans():
    try:
        # Establish the database connection
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM PersonalApplication
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





@ploan.route('/get_data_from_applicationid/<application_id>', methods=['GET'])
def get_data_from_applicationid(application_id):
    conn = None
    try:
        # Establish the database connection
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Use the application_id to fetch the specific loan application
        cursor.execute("""
            SELECT * FROM PersonalApplication WHERE Application_id = ?
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
        if conn:
            conn.close()
            
            
@ploan.route('/set_to_rejected/<application_id>', methods=['POST'])
def set_to_rejected(application_id):
    conn = None
    try:
        # Establish the database connection
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Update the status to 'rejected' for the specified application_id
        cursor.execute("""
            UPDATE PersonalApplication
            SET Status = 'rejected'
            WHERE Application_id = ?
        """, application_id)
        
        # Commit the transaction
        conn.commit()
        
        # Check if any row was updated
        if cursor.rowcount > 0:
            return jsonify({'message': 'Application status updated to rejected'}), 200
        else:
            return jsonify({'message': 'No data found for the provided application ID'}), 404

    except Exception as e:
        # Log the exception to the console for debugging
        logging.error(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        if conn:
            conn.close()

@ploan.route('/set_to_accepted/<application_id>', methods=['POST'])
def set_to_accepted(application_id):
    conn = None
    try:
        # Establish the database connection
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Update the status to 'accepted' for the specified application_id
        cursor.execute("""
            UPDATE PersonalApplication
            SET Status = 'accepted'
            WHERE Application_id = ?
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
        if conn:
            conn.close()