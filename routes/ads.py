import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from openai import AzureOpenAI
from flask import Flask, request, jsonify
import pyodbc
from datetime import datetime
from openai import AzureOpenAI
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for , jsonify
)
ads = Blueprint('ads', __name__, url_prefix='/ads')
# Sample Data
# Sample Customer Data (same as before)
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

# Define the customer DataFrame
customers = pd.DataFrame({
    'CustomerID': [86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98],
    'Name': ['Aisha Ahmed', 'Kevin Nguyen', 'Anuj Tadkase', 'Mohammed Ali', 'Grace Kim', 
             'Daniel Lee', 'Pratham Gadkari', 'James Patel', 'Sophia Garcia', 'Michael Johnson',
             'Aaliyah Williams', 'Kevin Nguyen', 'Suraj Chavan'],
    'Income (INR)': [50000, 75000, 40000, 60000, 55000, 80000, 35000, 65000, 45000, 70000, 52000, 78000, 42000],
    'CreditScore': [650, 700, 620, 680, 670, 710, 600, 690, 630, 720, 660, 730, 610],
    'Email': ['aisha.ahmed@example.com', 'kevin.nguyen@example.com', 'anujtadkase@gmail.com', 
              'mohammed.ali@example.com', 'grace.kim@example.com', 'daniel.lee@example.com', 
              'prathamgadkari@gmail.com', 'james.patel@example.com', 'sophia.garcia@example.com',
              'michael.johnson@example.com', 'aaliyah.williams@example.com', 
              'kevin.nguyen@example.com', 'suraj.chavan22@vit.edu'],
    'ExistingSchemes': ['Home Loan', 'Car Loan', 'Education Loan', 'Personal Loan', 'Home Loan', 
                        'Car Loan', 'Education Loan', 'Personal Loan', 'Home Loan', 
                        'Car Loan', 'Education Loan', 'Personal Loan', 'Home Loan'],
    'Age': [32, 41, 28, 36, 39, 45, 25, 34, 31, 42, 37, 46, 29],
    'Gender': ['Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female', 
               'Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
    'Occupation': ['Teacher', 'Business Owner', 'Student', 'Farmer', 'Business Owner', 'Engineer', 'Student',
                   'Engineer', 'Teacher', 'Business Owner', 'Doctor', 'Business Owner', 'Student']
})
# Link DataFrame for reference (same as before)
scheme_links = schemes[['SchemeName', 'Link']]

def get_scheme_details(scheme_name):
    if scheme_name not in schemes['SchemeName'].values:
        print(f"Scheme '{scheme_name}' not found!")
        return None, None
    
    scheme_details = schemes[schemes['SchemeName'] == scheme_name].iloc[0]
    scheme_info = scheme_details['SchemeInfo']
    scheme_link = scheme_details['Link']
    
    return scheme_info, scheme_link

import pandas as pd

def get_eligible_customers(scheme_name):
    # Check if the scheme exists
    if scheme_name not in schemes['SchemeName'].values:
        print(f"Scheme '{scheme_name}' not found!")
        return pd.DataFrame()  # Return an empty DataFrame if scheme not found

    # Get scheme details
    scheme_details = schemes[schemes['SchemeName'] == scheme_name].iloc[0]
    
    # Initialize eligible customers based on income and credit score
    eligible_customers = customers[
        (customers['Income (INR)'] >= scheme_details['MinIncome(INR)']) &
        (customers['CreditScore'] >= scheme_details['MinCreditScore'])
    ].copy()
    
    # Apply additional filters based on scheme details
    if pd.notna(scheme_details.get('Occupation')):
        eligible_customers = eligible_customers[eligible_customers['Occupation'] == scheme_details['Occupation']]
    
    if pd.notna(scheme_details.get('Gender')):
        eligible_customers = eligible_customers[eligible_customers['Gender'] == scheme_details['Gender']]
    
    if pd.notna(scheme_details.get('MinAge')):
        eligible_customers = eligible_customers[eligible_customers['Age'] >= scheme_details['MinAge']]
    
    eligible_customers = eligible_customers[~eligible_customers['ExistingSchemes'].str.contains(scheme_name, na=False)]

    return eligible_customers




def generate_email(customer_name, scheme_name, scheme_info, scheme_link):
    prompt = f"""
    Generate a personalized email for the customer from Bank of Baroda. 
    Include details of the {scheme_name} and its benefits: {scheme_info}. 
    Include the scheme link: {scheme_link}. 
    Also, make sure it's a well-crafted and short email, don't include personal info of banker, 
    regards should be from the Bank of Baroda team.
    Customer details: 
    Name: {customer_name}
    """
    endpoint = "https://bobopenai1.openai.azure.com/"
    key = "8af8440fb3e34b99b5abe914d8548709"
    model_name = "gpt23133"
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_version="2024-02-15-preview",
        api_key=key
    )
    # Replace with actual Azure OpenAI interaction
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
    )
    return response.choices[0].message.content.strip()

def send_email(subject, body, recipient_email):
    sender_email = "cyberwardensbankofbaroda@gmail.com"
    sender_password = "mepw ipyw lffr jviw"  # Update this with the application-specific password

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True, "Email sent successfully!"
    except smtplib.SMTPAuthenticationError:
        return False, "Authentication error. Check your email and password."
    except smtplib.SMTPConnectError:
        return False, "Failed to connect to the server. Check your internet connection or SMTP server settings."
    except Exception as e:
        return False, f"An error occurred: {e}"

def edit_email(scheme_name, scheme_info, scheme_link):
    eligible_customers = get_eligible_customers(scheme_name)
    if not eligible_customers.empty:
        customer_indices = eligible_customers.index.tolist()
        while customer_indices:
            print("Eligible Customers:")
            for idx in customer_indices:
                customer = eligible_customers.loc[idx]
                print(f"{idx}: {customer['Name']}")

            customer_index = int(input("Enter the index of the customer you want to email (or -1 to exit): ").strip())
            
            if customer_index == -1:
                break
            
            if customer_index not in customer_indices:
                print("Invalid index. Please try again.")
                continue
            
            customer_name = eligible_customers.loc[customer_index]['Name']
            
            while True:
                email_body = generate_email(customer_name, scheme_name, scheme_info, scheme_link)
                print(f"Generated email body for {customer_name}:\n{email_body}\n")

                print("Press 'E' to edit the email body, '1' to send this email, '2' to regenerate, or '3' to exit.")
                user_input = input().strip().upper()
                
                if user_input == 'E':
                    # Allow user to edit the email body
                    print("Edit the email body below (enter 'END' on a new line to finish):")
                    edited_body = []
                    while True:
                        line = input()
                        if line == 'END':
                            break
                        edited_body.append(line)
                    email_body = "\n".join(edited_body)
                
                elif user_input == '2':
                    # Regenerate the email
                    email_body = generate_email(customer_name, scheme_name, scheme_info, scheme_link)
                    print(f"Regenerated email body for {customer_name}:\n{email_body}\n")
                    continue  # Continue to prompt for editing or sending
                
                elif user_input == '3':
                    break  # Exit the editing loop
                
                if user_input in ['1', 'E']:
                    send_email("anujtadkase@gmail.com", f"Opportunity: {scheme_name}", email_body)
                    print(f"Email sent to anujtadkase@gmail.com for scheme '{scheme_name}'")
                    
                    # Remove the sent customer from the list and prompt for another customer
                    customer_indices.remove(customer_index)
                    if not customer_indices:
                        print("All eligible customers have been emailed.")
                        break
                    print("\nRemaining eligible customers:")
                    for idx in customer_indices:
                        customer = eligible_customers.loc[idx]
                        print(f"{idx}: {customer['Name']}")
                    break  # Break out of the inner loop to process the next customer
                
                if user_input == '3':
                    break  # Exit the editing loop if requested

    else:
        print("No eligible customers found.")
        

@ads.route('/eligible_customers', methods=['POST'])
def eligible_customers():
    data = request.json
    scheme_name = data.get('scheme_name')
    
    if not scheme_name:
        return jsonify({"error": "Scheme name is required"}), 400
    
    eligible_customers_df = get_eligible_customers(scheme_name)
    
    if eligible_customers_df.empty:
        return jsonify({"message": f"No eligible customers for scheme '{scheme_name}'"}), 404
    
    # Convert DataFrame to JSON
    result = eligible_customers_df.to_dict(orient='records')
    return jsonify(result)

@ads.route('/generate_email', methods=['POST'])
def generate_email_route():
    data = request.json
    customer_name = data.get('customer_name')
    scheme_name = data.get('scheme_name')

    if not all([customer_name, scheme_name]):
        return jsonify({"error": "Missing required parameters"}), 400

    # Fetch scheme details
    scheme_info, scheme_link = get_scheme_details(scheme_name)
    if scheme_info is None or scheme_link is None:
        return jsonify({"error": f"Scheme '{scheme_name}' not found!"}), 404

    try:
        email_content = generate_email(customer_name, scheme_name, scheme_info, scheme_link)
        return jsonify({"email": email_content}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ads.route('/send_email', methods=['POST'])
def send_email_route():
    data = request.json
    subject = data.get('subject')
    body = data.get('body')
    recipient_email = data.get('recipient_email')
    
    success, message = send_email(subject, body, recipient_email)
    
    if success:
        return jsonify({"status": "success", "message": message}), 200
    else:
        return jsonify({"status": "error", "message": message}), 400
