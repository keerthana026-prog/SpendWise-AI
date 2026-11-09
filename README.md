# SpendWise AI 💸

**An AI-powered personal finance and expense management application.**

SpendWise AI helps users track their expenses, manage monthly budgets, monitor savings goals, and understand their spending habits through AI-powered financial insights.
## 🚀 Live Demo

[https://spendwise-aigit-etpgbbispmauucnifnwmca.streamlit.app/](https://spendwise-aigit-etpgbbispmauucnifnwmca.streamlit.app/)

## 🚀 Project Overview

Managing personal finances can be difficult without proper tracking and insights. SpendWise AI provides a simple dashboard to help users understand where their money goes and make more informed financial decisions.

## ✨ Features

- **Expense Tracking:** Add, view, search, filter, and delete expenses.
- **Budget Management:** Set monthly budgets and monitor spending.
- **Interactive Dashboard:** View monthly spending, remaining budget, and category-wise charts.
- **AI Financial Assistant:** Generate financial insights using Google Gemini.
- **Savings Goals:** Create savings goals and track contributions.
- **Financial Summary:** Review spending patterns and financial activity.
- **Data Persistence:** Store expense and savings information using SQLite.
- **Privacy Consent:** Ask for user consent before sharing expense information with the AI assistant.

## 🛠️ Tech Stack

- Python
- Streamlit
- SQLite
- Google Gemini API
- Pandas and data visualization libraries

## 📂 Project Structure

```text
SpendWise-AI/
│
├── app.py
├── database.py
├── ai_insights.py
├── paypal_integration.py
├── .streamlit/
│   └── config.toml
├── .gitignore
├── README.md
├── requirements.txt
└── .env  (local only; not committed)
```

## ⚙️ Installation and Setup

1. Clone the repository:

```bash
git clone https://github.com/keerthana026-prog/SpendWise-AI.git
cd SpendWise-AI
```

2. Create and activate a virtual environment.

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project folder and add your own Gemini API credentials.

5. Start the application:

```bash
streamlit run app.py
```

## 🔐 Privacy and Security

- API credentials are stored in a local `.env` file.
- Local database files and virtual environments are excluded from Git.
- Expense information is shared with the AI assistant only after user consent.

## 💳 PayPal Integration

PayPal Sandbox order creation has been implemented and tested. Buyer checkout approval and payment capture are still under development.

## 👥 Team

Developed as a collaborative student project for the PayPal AI Hackathon 2026.

## 🎯 Project Goal

To make personal finance management simpler and more accessible through expense tracking, budgeting, savings monitoring, and AI-powered insights.

---

**Spend smarter. Save better. Understand your money.**
