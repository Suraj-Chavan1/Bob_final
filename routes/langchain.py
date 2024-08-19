import json
from flask import Blueprint, request, jsonify, Response
from langchain_openai import AzureOpenAI
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents import AgentExecutor
from langchain.agents.agent_types import AgentType
from langchain.prompts.chat import ChatPromptTemplate
from urllib.parse import quote_plus

# Variables
OPENAI_API_KEY = "8af8440fb3e34b99b5abe914d8548709"
OPENAI_API_BASE = "https://bobopenai1.openai.azure.com/"
OPENAI_API_VERSION = "2024-02-01"
OPENAI_DEPLOYMENT_NAME = "langchaingpt"
OPENAI_MODEL_NAME = "gpt-35-turbo-instruct"

server = 'cbnewbase.database.windows.net'
database = 'bobdb'
username = 'suraj'
password = 'cyberwardens123@'
dsn = "ODBC Driver 18 for SQL Server"

# Connection string format
DATABASE_CONNECTION_STRING = f"mssql+pyodbc://{username}:{quote_plus(password)}@{server}/{database}?driver={dsn}"

# LangChain uses SQLAlchemy under the hood, here we establish database and LLM variables for use later in the script.
db = SQLDatabase.from_uri(DATABASE_CONNECTION_STRING)
llm = AzureOpenAI(
    deployment_name=OPENAI_DEPLOYMENT_NAME,
    model_name=OPENAI_MODEL_NAME,
    api_key=OPENAI_API_KEY,
    azure_endpoint=OPENAI_API_BASE,  # Correct parameter for Azure endpoint
    api_version=OPENAI_API_VERSION,
    temperature=0  # Adjusted to a typical range
)

# Establish SQL Database toolkit and LangChain Agent Executor
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)

# Create the prompt template
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a SQL Server expert. Your task is to execute SQL queries and format the results as JSON objects with column names."),
        ("user", "{query}\n Question: "),
        ("system", "Provide the output in the following structured format:\n"
                   "1. For each row, include the column names and values in JSON format.\n"
                   "2. Each row should be a separate JSON object.\n"
                   "3. Ensure the output is clear and systematic.\n"
                   "Answer: "),
        ("system", "Tables and column names:\n"
                   "PersonalApplication (Application_id, Customer_ID, Name, Age, Occupation, Annual_Income, Monthly_Inhand_Salary, Num_Bank_Accounts, Num_Credit_Card, Interest_Rate, Num_of_Loan, Delay_from_due_date, Num_of_Delayed_Payment, Changed_Credit_Limit, Num_Credit_Inquiries, Outstanding_Debt, Credit_Utilization_Ratio, Credit_History_Age, Total_EMI_per_month, Amount_invested_monthly, Monthly_Balance, Applied_date_time, Status, Result, Message_to_User, Type_of_Loan)\n"
                   "BusinessLoanApplication (application_id, company_name, auditing_company_name, current_assets, current_liabilities, inventory, total_debt, total_equity, total_assets, net_income, net_sales, ebit, interest_expense, operating_cash_flow, capital_expenditures, Current_Ratio, Quick_Ratio, Debt_to_Equity_Ratio, Debt_Ratio, Net_Profit_Margin, Return_on_Assets, Return_on_Equity, Interest_Coverage_Ratio, Operating_Cash_Flow_to_Total_Debt_Ratio, Free_Cash_Flow_to_Firm, User_id, Status, result)\n"
                   "EmailClassifications (application_id, email_id, email_content, category, status, reply_message, classification_date, user_id)")
    ]
)

ln = Blueprint('langchain', __name__, url_prefix='/langchain')

import json
from flask import Blueprint, request, jsonify, Response
from langchain_openai import AzureOpenAI
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents import AgentExecutor
from langchain.agents.agent_types import AgentType
from langchain.prompts.chat import ChatPromptTemplate
from urllib.parse import quote_plus

# Variables
OPENAI_API_KEY = "8af8440fb3e34b99b5abe914d8548709"
OPENAI_API_BASE = "https://bobopenai1.openai.azure.com/"
OPENAI_API_VERSION = "2024-02-01"
OPENAI_DEPLOYMENT_NAME = "langchaingpt"
OPENAI_MODEL_NAME = "gpt-35-turbo-instruct"

server = 'cbnewbase.database.windows.net'
database = 'bobdb'
username = 'suraj'
password = 'cyberwardens123@'
dsn = "ODBC Driver 18 for SQL Server"

# Connection string format
DATABASE_CONNECTION_STRING = f"mssql+pyodbc://{username}:{quote_plus(password)}@{server}/{database}?driver={dsn}"

# LangChain uses SQLAlchemy under the hood, here we establish database and LLM variables for use later in the script.
db = SQLDatabase.from_uri(DATABASE_CONNECTION_STRING)
llm = AzureOpenAI(
    deployment_name=OPENAI_DEPLOYMENT_NAME,
    model_name=OPENAI_MODEL_NAME,
    api_key=OPENAI_API_KEY,
    azure_endpoint=OPENAI_API_BASE,
    api_version=OPENAI_API_VERSION,
    temperature=0
)

# Establish SQL Database toolkit and LangChain Agent Executor
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)

# Create the prompt template
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a SQL Server expert. Your task is to execute SQL queries and format the results as JSON objects with column names."),
        ("user", "{query}\n Question: "),
        ("system", "Provide the output in the following structured format:\n"
                   "1. For each row, include the column names and values in JSON format.\n"
                   "2. Each row should be a separate JSON object.\n"
                   "3. Ensure the output is clear and systematic.\n"
                   "Answer: "),
        ("system", "Tables and column names:\n"
                   "PersonalApplication (Application_id, Customer_ID, Name, Age, Occupation, Annual_Income, Monthly_Inhand_Salary, "
                   "Num_Bank_Accounts, Num_Credit_Card, Interest_Rate, Num_of_Loan, Delay_from_due_date, Num_of_Delayed_Payment, "
                   "Changed_Credit_Limit, Num_Credit_Inquiries, Outstanding_Debt, Credit_Utilization_Ratio, Credit_History_Age, "
                   "Total_EMI_per_month, Amount_invested_monthly, Monthly_Balance, Applied_date_time, Status, Result, "
                   "Message_to_User, Type_of_Loan)\n"
                   "BusinessLoanApplication (application_id, company_name, auditing_company_name, current_assets, current_liabilities, "
                   "inventory, total_debt, total_equity, total_assets, net_income, net_sales, ebit, interest_expense, operating_cash_flow, "
                   "capital_expenditures, Current_Ratio, Quick_Ratio, Debt_to_Equity_Ratio, Debt_Ratio, Net_Profit_Margin, "
                   "Return_on_Assets, Return_on_Equity, Interest_Coverage_Ratio, Operating_Cash_Flow_to_Total_Debt_Ratio, "
                   "Free_Cash_Flow_to_Firm, User_id, Status, result)\n"
                   "EmailClassifications (application_id, email_id, email_content, category, status, reply_message, classification_date, user_id)")
    ]
)

ln = Blueprint('langchain', __name__, url_prefix='/langchain')

@ln.route('/query', methods=['POST'])
def query():
    data = request.json
    user_query = data.get('query')
    if not user_query:
        return jsonify({"error": "Query parameter is required"}), 400
    
    try:
        formatted_query = prompt_template.format(query=user_query)
        result = agent_executor.invoke(formatted_query)
        
        # Log the raw result for inspection
        print("Raw result:", result)

        # Convert the result to JSON format
        if isinstance(result, (list, dict)):
            response = json.dumps({"result": result}, indent=4)
            return Response(response, mimetype='application/json'), 200

        else:
            return jsonify({"error": "Unexpected result format"}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
