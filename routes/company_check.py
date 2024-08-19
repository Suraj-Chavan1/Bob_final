from flask import Flask, request, jsonify
from openai import AzureOpenAI
import json
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify

cp = Blueprint('company_check', __name__, url_prefix='/company_check')

# Define your Azure OpenAI credentials and endpoint
endpoint = "https://bobopenai1.openai.azure.com/"
key = "8af8440fb3e34b99b5abe914d8548709"
model_name = "gpt23133"

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_version="2024-02-15-preview",
    api_key=key
)
# Function to get news about a company
def get_company_news(company_name):
    prompt = f"""
    Provide a point-wise summary of recent news about the company {company_name}.
    Include the following details with dates:
    - Lawsuits
    - Market trends
    - Market sentiment
    - People sentiment

    Limit the summary to the most recent and significant news from this year, including both positive and negative news (limit the size of output).
    """

    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_tokens=300,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
    )

    news_summary = completion.choices[0].message.content.strip()

    return news_summary

# Function to classify loan approval based on news summary
def classify_loan_approval(news_summary):
    classification_prompt = f"""
    Based on the following news summary, classify the sentiment  for the company to give a loan to as:
    - Overall Positive
    - Negative
    - Moderate

    Provide only the classification in the first line.

    Summary:
    {news_summary}
    """

    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": classification_prompt,
            },
        ],
        max_tokens=100,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
    )

    classification = completion.choices[0].message.content.strip()

    return classification

# Route to get news and classify loan approval
@cp.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    company_name = data.get('company_name')

    if not company_name:
        return jsonify({"error": "Company name is required"}), 400

    # Fetch and analyze news
    news_summary = get_company_news(company_name)
    
    # Classify loan approval risk
    classification = classify_loan_approval(news_summary)

    # Format results as JSON
    result = {
        "company_name": company_name,
        "news_summary": news_summary,
        "loan_approval_risk": classification
    }

    return jsonify(result), 200


