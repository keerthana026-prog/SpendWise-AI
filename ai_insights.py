
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

# Load the API key from the project's .env file
env_path = Path(__file__).with_name(".env")
load_dotenv(env_path)

API_KEY = os.getenv("GEMINI_API_KEY")

MODEL_NAME = "gemini-3.5-flash-lite"


def generate_insights(expense_records, monthly_budget, question):

    if not API_KEY:
        return "Gemini API key not found. Please check your .env file."

    if not expense_records:
        return "Please add some expenses before requesting AI insights."

    expense_summary = []

    for record in expense_records:
        expense_id, name, amount, category, expense_date = record

        expense_summary.append({
            "expense": name,
            "amount": float(amount),
            "category": category,
            "date": str(expense_date)
        })

    total_spent = sum(
        item["amount"] for item in expense_summary
    )

    prompt = f"""
You are SpendWise AI, a helpful personal finance assistant.

Analyse the user's actual expense information.

Monthly budget: ₹{monthly_budget}
Total recorded spending: ₹{total_spent}

Expense records:
{expense_summary}

User's question:
{question}

Instructions:
1. Analyse the actual expense data carefully.
2. Give practical and realistic saving suggestions.
3. Use Indian Rupees (₹).
4. Explain recommendations in simple language.
5. Do not invent expenses or financial information.
6. Mention clearly if information is insufficient.
7. Do not present your response as professional financial advice.
"""

    try:
        client = genai.Client(
            api_key=API_KEY,
           http_options={"timeout": 90000}
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        if response.text:
            return response.text

        return "Gemini did not return a text response. Please try again."

    except Exception as error:
        return (
            "Unable to generate insights right now. "
            f"Please try again later. Details: {error}"
        )
