from flask import Flask, request, jsonify
import pyodbc
from datetime import datetime
from openai import AzureOpenAI
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for , jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash
import uuid


#genrated response

import pandas as pd
from openai import AzureOpenAI
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load scheme data and FAQ data (as provided in your code)
schemes = pd.DataFrame({
    'SchemeName': ['Small Business Loan', 'Education Loan', 'Green Energy Loan', 'Women Entrepreneur Loan', 
                   'Farmers Loan', 'Retired Military Personnel Loan', 'First Time Home Buyer Loan', 
                   'Startup Loan', 'Student Loan', 'Renewable Energy Loan', 
                   'Rural Development Loan', 'Healthcare Loan', 'Solar Energy Loan', 
                   'Fisherman Loan', 'Elderly Care Loan'],
    'SchemeInfo': ['Empower your small business with our flexible loan options designed for growth and sustainability', 
                   'Support your education journey with our specialized loans for students.', 
                   'Invest in a greener future with our loans for renewable energy projects', 
                   'Boost your business with our loans tailored for ambitious women entrepreneurs', 
                   'Enhance your agricultural potential with our financial support for farmers.', 
                   'Enjoy financial assistance tailored for retired military personnel to support your post-service life', 
                   'Make your dream home a reality with our first-time homebuyer loans', 
                   'Kickstart your entrepreneurial journey with our funding options for new startups.', 
                   'Ease your educational expenses with our comprehensive student loan solutions.', 
                   'Accelerate your renewable energy initiatives with our specialized loan offerings.', 
                   'Transform rural communities with our development loans designed for infrastructure and growth', 
                   'Access funding for healthcare improvements and medical expenses with our tailored loans', 
                   'Power up your solar energy projects with our dedicated financing options.', 
                   'Support your fishing business and equipment needs with our customized loans', 
                   'Provide quality care for the elderly with our financial solutions designed for care services'],
    'Link': ['https://www.bankofbaroda.in/personal-banking/loans/small-business-loan', 
             'https://www.bankofbaroda.in/personal-banking/loans/education-loan',
             'https://www.bankofbaroda.in/personal-banking/loans/green-energy-loan', 
             'https://www.bankofbaroda.in/personal-banking/loans/women-entrepreneur-loan', 
             'https://www.bankofbaroda.in/personal-banking/loans/farmers-loan', 
             'https://www.bankofbaroda.in/personal-banking/loans/retired-military-personnel-loan', 
             'https://www.bankofbaroda.in/personal-banking/loans/first-time-home-buyer-loan', 
             'https://www.bankofbaroda.in/personal-banking/loans/startup-loan', 
             'https://www.bankofbaroda.in/personal-banking/loans/student-loan', 
             'https://www.bankofbaroda.in/personal-banking/loans/renewable-energy-loan', 
             'https://www.bankofbaroda.in/personal-banking/loans/rural-development-loan', 
             'https://www.bankofbaroda.in/personal-banking/loans/healthcare-loan', 
             'https://www.bankofbaroda.in/personal-banking/loans/solar-energy-loan', 
             'https://www.bankofbaroda.in/personal-banking/loans/fisherman-loan', 
             'https://www.bankofbaroda.in/personal-banking/loans/elderly-care-loan']
})

faqs = pd.DataFrame({
    'Question': [
        'How do I open a savings account?',
        'What are the types of loans offered by Bank of Baroda?',
        'How can I apply for a debit card?',
        'What is the process for online fund transfer?',
        'How do I update my KYC details?',
        'What are the interest rates for fixed deposits?',
        'How can I register for internet banking?',
        'What is the minimum balance required for a savings account?',
        'How do I report a lost or stolen card?',
        'What are the working hours of Bank of Baroda branches?'
    ],
    'Answer': [
        'To open a savings account, visit your nearest Bank of Baroda branch with valid ID proof, address proof, and passport-size photographs. You can also initiate the process online through our website.',
        'Bank of Baroda offers various types of loans including home loans, personal loans, car loans, education loans, and business loans. Check our website for specific loan products.',
        'Existing account holders can apply for a debit card through internet banking, mobile banking, or by visiting the nearest branch. New account holders usually receive a debit card with their account opening kit.',
        'You can transfer funds online using our internet banking or mobile banking services. Log in, select the transfer option, enter the beneficiary details and amount, and authorize the transaction using your secure password or OTP.',
        'To update your KYC details, visit your home branch with the latest KYC documents. Some updates can also be done through internet banking or our mobile app.',
        'Fixed deposit interest rates vary based on the deposit amount and tenure. Please check our website or contact your nearest branch for the latest rates.',
        'You can register for internet banking by visiting our website and clicking on the "Register" option under internet banking. Youll need your account details and registered mobile number to complete the process.',
        'The minimum balance requirement varies based on the type of savings account and your location (urban, semi-urban, or rural). Please check with your local branch or our website for specific details.',
        'If your card is lost or stolen, immediately call our 24/7 customer care number to block the card. You can also block the card through internet banking or mobile banking.',
        'Most Bank of Baroda branches operate from Monday to Friday, 10:00 AM to 4:00 PM, and on Saturdays from 10:00 AM to 1:00 PM. Timings may vary for specific branches or on holidays.'
    ]
})

def get_scheme_details(scheme_name):
    if scheme_name not in schemes['SchemeName'].values:
        return None, None
    scheme = schemes[schemes['SchemeName'] == scheme_name].iloc[0]
    return scheme['SchemeInfo'], scheme['Link']

def generate_response(email_content):
    client = AzureOpenAI(
        azure_endpoint="https://bobopenai1.openai.azure.com/",
        api_version="2024-02-15-preview",
        api_key="8af8440fb3e34b99b5abe914d8548709"
    )

    # Check if the query matches any FAQ
    matched_faq = faqs[faqs['Question'].str.lower().str.contains(email_content.lower())]
    
    if not matched_faq.empty:
        return matched_faq.iloc[0]['Answer']

    prompt = f"""
    Generate a response to the following email:
    {email_content}

  

    If the query is related to a specific loan scheme, include relevant details from our available schemes:
    {schemes[['SchemeName', 'SchemeInfo']].to_string(index=False)}

    Please provide a professional and helpful response that addresses the specific concerns or queries in the email.
    """

    response = client.chat.completions.create(
        model="gpt23133",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.7
    )

    return response.choices[0].message.content.strip()

def regenerate_response(email_content, context):
    client = AzureOpenAI(
        azure_endpoint="https://bobopenai1.openai.azure.com/",
        api_version="2024-02-15-preview",
        api_key="8af8440fb3e34b99b5abe914d8548709"
    )

    # Check if the query matches any FAQ
    matched_faq = faqs[faqs['Question'].str.lower().str.contains(email_content.lower())]
    
    if not matched_faq.empty:
        return matched_faq.iloc[0]['Answer']

    prompt = f"""
    Generate a response to the following email:
    {email_content}

    Context provided by the user:
    {context}

    If the query is related to a specific loan scheme, include relevant details from our available schemes:
    {schemes[['SchemeName', 'SchemeInfo']].to_string(index=False)}

    Please provide a professional and helpful response that addresses the specific concerns or queries in the email.
    """

    response = client.chat.completions.create(
        model="gpt23133",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.7
    )

    return response.choices[0].message.content.strip()



def send_email(subject, body, recipient_email):
    sender_email = "cyberwardensbankofbaroda@gmail.com"
    sender_password = "bkcBKC123"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)
#genrated response end here
server = 'cbnewbase.database.windows.net'
database = 'bobdb'
username = 'suraj'
password = 'cyberwardens123@'
connection_string = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};Trusted_Connection=no;'

# Azure OpenAI configuration
endpoint = "https://bobopenai1.openai.azure.com/"
key = "8af8440fb3e34b99b5abe914d8548709"
model_name = "gpt23133"

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_version="2024-02-15-preview",
    api_key=key
)

def classify_email(email_content):
    prompt = f"""
    Classify the following email into one of the four categories:
    - Loans and Mortgages: Inquiries about loans, mortgage applications, interest rates, or repayment issues.
    - Deposits and Withdrawals: Questions about account deposits, withdrawals, transfers, or balance inquiries.
    - Fraud and Security: Reports of suspicious activity, unauthorized transactions, or security concerns.
    - Customer Service: General inquiries, complaints, or issues not fitting the above categories.


    Only respond with the category name.

    Email: {email_content}

    The category is:
    """

    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_tokens=50,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
    )

    category = completion.choices[0].message.content.strip()
    if category not in ["Loans and Mortgages", "Deposits and Withdrawals", "Fraud and Security", "Customer Service"]:
        category = "Customer Service"

    return category


def analyze_sentiment(email_content):
    prompt = f"""
    Analyze the sentiment of the following email content. The possible sentiments are "positive", "neutral", or "negative". 
    Consider the overall tone, language used, and any expressions of satisfaction or dissatisfaction.
    Only respond with one word: the sentiment.

    Email: {email_content}

    The sentiment is:
    """

    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_tokens=50,
        temperature=0.3,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
    )

    sentiment = completion.choices[0].message.content.strip().lower()
    if sentiment not in ["positive", "neutral", "negative"]:
        sentiment = "neutral"

    return sentiment


def detect_urgency(email_content):
    # Keywords for detecting urgency
    urgency_keywords = ["immediately", "asap", "urgent", "deadline", "soon", "quickly", "today", "tomorrow", "fast"]
    if any(keyword in email_content.lower() for keyword in urgency_keywords):
        return "urgent"
    return "non-urgent"


def summarize_email(email_content):
    prompt = f"""
    Provide a one-line summary of the following email content. The summary should be concise and highlight key details.

    Email: {email_content}

    Summary:
    """

    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_tokens=50,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
    )

    summary = completion.choices[0].message.content.strip()
    return summary

def calculate_priority(email_content):
    category = classify_email(email_content)
    sentiment = analyze_sentiment(email_content)
    urgency = detect_urgency(email_content)
    summary = summarize_email(email_content)
    
    if urgency == "urgent":
        if sentiment == "negative":
            priority = 1
        elif sentiment == "neutral":
            priority = 2
        else:  # positive
            priority = 3
    else:
        if sentiment == "negative":
            priority = 3
        elif sentiment == "neutral":
            priority = 4
        else:  # positive
            priority = 5

    return {
        "category": category,
        "sentiment": sentiment,
        "urgency": urgency,
        "priority": priority,
        "summary": summary
    }


email = Blueprint('emailclassify', __name__, url_prefix='/emailclassify')

@email.route('/classify_email_to_user', methods=['POST'])
def classify_and_save_email():
    data = request.json
    email_id = data.get('email_id')
    email_content = data.get('email_content')
    user_id = data.get('user_id')
    
    if not email_id or not email_content or not user_id:
        return jsonify({"error": "email_id, email_content, and user_id are required"}), 400

    category = classify_email(email_content)
    summary = summarize_email(email_content)
    urgency = detect_urgency(email_content)
    priority = calculate_priority(email_content)['priority']
    sentiment = analyze_sentiment(email_content)

    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Prepare and execute the insert statement
        current_datetime = datetime.now()
        cursor.execute("""
            INSERT INTO EmailClassificationsNew (email_id, email_content, category, status, reply_message, classification_date, user_id, summary, urgency, priority, sentiment ,ai_generated_response )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
        """, (email_id, email_content, category, 'Processed', 'Null', current_datetime, user_id, summarize_email(email_content), urgency, priority, sentiment,generate_response(email_content)))

        conn.commit()
        conn.close()

        return jsonify({
            "email_id": email_id,
            "email_content": email_content,
            "category": category,
            "status": "Processed",
            "reply_message": f"Classified as {category}",
            "classification_date": current_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": user_id
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

server = 'cbnewbase.database.windows.net'
database = 'bobdb'
username = 'suraj'
password = 'cyberwardens123@'
connection_string = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};Trusted_Connection=no;'

@email.route('/get_loans_and_mortgages', methods=['GET'])
def get_loans_and_mortgages():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM EmailClassificationsNew
            WHERE category = 'Loans and Mortgages'
        """)
        
        rows = cursor.fetchall()
        if rows:
            columns = [column[0] for column in cursor.description]
            result = [dict(zip(columns, row)) for row in rows]
            return jsonify(result)
        else:
            return jsonify({'message': 'No data found for the category "Loans and Mortgages"'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if 'conn' in locals() and conn:
            conn.close()


@email.route('/get_deposits_and_withdrawals', methods=['GET'])
def get_deposits_and_withdrawals():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM EmailClassificationsNew
            WHERE category = 'Deposits and Withdrawals'
        """)
        
        rows = cursor.fetchall()
        if rows:
            columns = [column[0] for column in cursor.description]
            result = [dict(zip(columns, row)) for row in rows]
            return jsonify(result)
        else:
            return jsonify({'message': 'No data found for the category "Deposits and Withdrawals"'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if 'conn' in locals() and conn:
            conn.close()

@email.route('/get_fraud_and_security', methods=['GET'])
def get_fraud_and_security():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM EmailClassificationsNew
            WHERE category = 'Fraud and Security'
        """)
        
        rows = cursor.fetchall()
        if rows:
            columns = [column[0] for column in cursor.description]
            result = [dict(zip(columns, row)) for row in rows]
            return jsonify(result)
        else:
            return jsonify({'message': 'No data found for the category "Fraud and Security"'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if 'conn' in locals() and conn:
            conn.close()

@email.route('/get_customer_service', methods=['GET'])
def get_customer_service():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM EmailClassificationsNew
            WHERE category = 'Customer Service'
        """)
        
        rows = cursor.fetchall()
        if rows:
            columns = [column[0] for column in cursor.description]
            result = [dict(zip(columns, row)) for row in rows]
            return jsonify(result)
        else:
            return jsonify({'message': 'No data found for the category "Customer Service"'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if 'conn' in locals() and conn:
            conn.close()

@email.route('/email_by_userid', methods=['GET'])
def email_by_userid():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM EmailClassificationsNew
            
            WHERE user_id = 1
        """)
        
        rows = cursor.fetchall()
        if rows:
            columns = [column[0] for column in cursor.description]
            result = [dict(zip(columns, row)) for row in rows]
            return jsonify(result)
        else:
            return jsonify({'message': 'No data found for the category "Fraud and Security"'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if 'conn' in locals() and conn:
            conn.close()
            
            
@email.route('/get_all_emails', methods=['GET'])
def get_all_emails():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM EmailClassificationsNew
        """)
        
        rows = cursor.fetchall()
        if rows:
            columns = [column[0] for column in cursor.description]
            result = [dict(zip(columns, row)) for row in rows]
            return jsonify(result)
        else:
            return jsonify({'message': 'Error No email Found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if 'conn' in locals() and conn:
            conn.close()

@email.route('/email_by_applicationid', methods=['GET'])
def email_by_applicationid():
    try:
        # Get the application_id from the request query parameters
        application_id = request.args.get('application_id')
        
        if not application_id:
            return jsonify({'error': 'Application ID is required'}), 400

        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Use the application_id in the SQL query
        cursor.execute("""
            SELECT *
            FROM EmailClassificationsNew
            WHERE application_id = ?
        """, application_id)
        
        rows = cursor.fetchall()
        if rows:
            columns = [column[0] for column in cursor.description]
            result = [dict(zip(columns, row)) for row in rows]
            return jsonify(result)
        else:
            return jsonify({'message': f'No data found for application_id {application_id}'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if 'conn' in locals() and conn:
            conn.close()


@email.route('/regenerate-response', methods=['POST'])
def regenerate_response_for_email():
    # Get JSON data from the request
    data=request.json
    

    # Check if 'email_content' and 'context' are provided
    if 'email_content' not in data or 'context' not in data:
        return jsonify({'error': 'Missing required fields: email_content and context'}), 400

    email_content = data['email_content']
    context = data['context']

    # Call the regenerate_response function
    try:
        response = regenerate_response(email_content, context)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@email.route('/process-email', methods=['POST'])
def process_email():
    data = request.json
    email_content = data.get('email_content')
    recipient_email=data.get('recipient_email')
    subject = "Respond Mail From Bank Of Baroda"

    response = data.get('response')

    send_email(subject, response, recipient_email)

    return jsonify({'message': 'Email processed and sent successfully','response':response}), 200


@email.route('/replymessage_by_applicationid', methods=['POST'])
def replymessage_by_applicationid():
    try:
        # Get the application_id and reply_message from the request JSON body
        data = request.get_json()
        application_id = data.get('application_id')
        reply_message = data.get('reply_message')
        
        if not application_id:
            return jsonify({'error': 'Application ID is required'}), 400

        if not reply_message:
            return jsonify({'error': 'Reply message is required'}), 400

        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Update the reply_message in the EmailClassificationsNew table
        cursor.execute("""
            UPDATE EmailClassificationsNew
            SET reply_message = ?
            WHERE application_id = ?
        """, reply_message, application_id)
        
        conn.commit()

        # Fetch the updated record to confirm the update
        cursor.execute("""
            SELECT *
            FROM EmailClassificationsNew
            WHERE application_id = ?
        """, application_id)
        
        rows = cursor.fetchall()
        if rows:
            columns = [column[0] for column in cursor.description]
            result = [dict(zip(columns, row)) for row in rows]
            return jsonify(result)
        else:
            return jsonify({'message': f'No data found for application_id {application_id}'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if 'conn' in locals() and conn:
            conn.close()
