from flask import Flask, request, jsonify, render_template
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from openai import AzureOpenAI
from flask import Blueprint



ads = Blueprint('ads', __name__, url_prefix='/ads')

schemes = pd.DataFrame({
    'SchemeName': ['Small Business Loan', 'Education Loan', 'Green Energy Loan', 'Women Entrepreneur Loan', 
                   'Farmers Loan', 'Retired Military Personnel Loan', 'First Time Home Buyer Loan', 
                   'Startup Loan', 'Student Loan', 'Renewable Energy Loan', 
                   'Rural Development Loan', 'Healthcare Loan', 'Solar Energy Loan', 
                   'Fisherman Loan', 'Elderly Care Loan'],
    'MinIncome(INR)': [5000, 2500, 8000, 6000, 5000, 3000, 4500, 5500, 3500, 9000, 4000, 
                       5000, 8500, 4500, 3500],
    'MinCreditScore': [680, 650, 750, 700, 650, 600, 650, 700, 600, 600, 600, 700, 750, 650, 600],
    'InterestRate(%)': [8.5, 7.5, 6.5, 8, 7, 8.5, 6, 9.5, 9, 6, 7.5, 8.5, 6.5, 7, 8.5],
    'MaxLoanAmount(INR)': [8000000, 4000000, 12000000, 10000000, 6000000, 3500000, 4000000, 
                           15000000, 5000000, 15000000, 5000000, 7000000, 14000000, 5500000, 3000000],
    'Tenure(years)': [12, 15, 20, 15, 10, 15, 30, 10, 20, 25, 12, 15, 20, 10, 15],
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
    'Occupation': [None, 'Student', 'Engineer', 'Business Owner', 'Farmer', 'Retired Military', 
                   None, 'Entrepreneur', 'Student', 'Engineer', None, 'Doctor', 'Engineer', 'Fisherman', None],
    'Gender': [None, None, None, 'Female', None, None, None, None, None, None, None, None, None, None, None],
    'MinAge': [None, None, None, None, None, None, None, None, None, None, None, None, None, None, 60],
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

customers = pd.DataFrame({
    'CustomerID': [86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98],
    'Name': ['Aisha Ahmed', 'Kevin Nguyen', 'Sofia Rodriguez', 'Mohammed Ali', 'Grace Kim', 
             'Daniel Lee', 'Emily Chen', 'James Patel', 'Sophia Garcia', 'Michael Johnson',
             'Aaliyah Williams', 'Kevin Nguyen', 'Sofia Rodriguez'],
    'Income (INR)': [50000, 75000, 40000, 60000, 55000, 80000, 35000, 65000, 45000, 70000, 52000, 78000, 42000],
    'CreditScore': [650, 700, 620, 680, 670, 710, 600, 690, 630, 720, 660, 730, 610],
    'Email': ['aisha.ahmed@example.com', 'kevin.nguyen@example.com', 'sofia.rodriguez@example.com', 
              'mohammed.ali@example.com', 'grace.kim@example.com', 'daniel.lee@example.com', 
              'emily.chen@example.com', 'james.patel@example.com', 'sophia.garcia@example.com',
              'michael.johnson@example.com', 'aaliyah.williams@example.com', 
              'kevin.nguyen@example.com', 'sofia.rodriguez@example.com'],
    'ExistingSchemes': ['Home Loan', 'Car Loan', 'Education Loan', 'Personal Loan', 'Home Loan', 
                        'Car Loan', 'Education Loan', 'Personal Loan', 'Home Loan', 
                        'Car Loan', 'Education Loan', 'Personal Loan', 'Home Loan'],
    'Age': [32, 41, 28, 36, 39, 45, 25, 34, 31, 42, 37, 46, 29],
    'Gender': ['Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female', 
               'Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
    'Occupation': ['Teacher', 'Business Owner', 'Student', 'Farmer', 'Business Owner', 'Engineer', 'Student',
                   'Engineer', 'Teacher', 'Business Owner', 'Doctor', 'Business Owner', 'Student']
})

def get_scheme_details(scheme_name):
    if scheme_name not in schemes['SchemeName'].values:
        return {"error": f"Scheme '{scheme_name}' not found!"}
    
    scheme_details = schemes[schemes['SchemeName'] == scheme_name].iloc[0]
    scheme_info = scheme_details['SchemeInfo']
    scheme_link = scheme_details['Link']
    
    return {"scheme_info": scheme_info, "scheme_link": scheme_link}

def get_eligible_customers(scheme_name):
    if scheme_name not in schemes['SchemeName'].values:
        return pd.DataFrame()  # Return an empty DataFrame if scheme not found

    scheme_details = schemes[schemes['SchemeName'] == scheme_name].iloc[0]
    
    eligible_customers = customers[
        (customers['Income (INR)'] >= scheme_details['MinIncome(INR)']) &
        (customers['CreditScore'] >= scheme_details['MinCreditScore'])
    ]
    
    return eligible_customers[['CustomerID', 'Name', 'Email']]

def generate_email(customer, scheme_name):
    scheme_details = schemes[schemes['SchemeName'] == scheme_name].iloc[0]
    scheme_info = scheme_details['SchemeInfo']
    scheme_link = scheme_details['Link']
    
    email_content = f"Dear {customer['Name']},\n\n"
    email_content += f"We are excited to inform you about our {scheme_name}. {scheme_info}\n\n"
    email_content += f"To know more about this scheme, please visit: {scheme_link}\n\n"
    email_content += "Best regards,\nThe Bank Team"
    
    return email_content

def send_email(to_email, subject, body):
    sender_email = "your-email@example.com"
    sender_password = "your-password"
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))
    
    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

# Updated routes with POST requests
@ads.route('/scheme', methods=['POST'])
def get_scheme():
    data = request.json
    scheme_name = data.get('scheme_name')
    scheme_details = get_scheme_details(scheme_name)
    return jsonify(scheme_details)

@ads.route('/eligible_customers', methods=['POST'])
def eligible_customers():
    data = request.json
    scheme_name = data.get('scheme_name')
    customers_df = get_eligible_customers(scheme_name)
    return jsonify(customers_df.to_dict(orient='records'))

@ads.route('/send_emails', methods=['POST'])
def send_emails():
    data = request.json
    scheme_name = data.get('scheme_name')
    eligible_customers_df = get_eligible_customers(scheme_name)
    if eligible_customers_df.empty:
        return jsonify({"error": "No eligible customers found for this scheme"}), 404
    
    for _, customer in eligible_customers_df.iterrows():
        email_body = generate_email(customer, scheme_name)
        send_email(customer['Email'], f"Exciting Scheme: {scheme_name}", email_body)
    
    return jsonify({"message": "Emails sent successfully!"})

@ads.route('/edit_email', methods=['POST'])
def edit_email():
    data = request.json
    customer_id = data.get('CustomerID')
    new_email = data.get('NewEmail')

    if customer_id not in customers['CustomerID'].values:
        return jsonify({"error": "Customer not found!"}), 404
    
    customers.loc[customers['CustomerID'] == customer_id, 'Email'] = new_email
    return jsonify({"message": "Email updated successfully!"})
