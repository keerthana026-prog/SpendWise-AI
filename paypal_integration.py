
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

env_path = Path(__file__).with_name(".env")
load_dotenv(env_path)

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")

PAYPAL_BASE_URL = os.getenv(
    "PAYPAL_BASE_URL",
    "https://api-m.sandbox.paypal.com"
)


def get_paypal_access_token():
    if not PAYPAL_CLIENT_ID or not PAYPAL_CLIENT_SECRET:
        raise ValueError("PayPal credentials are missing from .env")

    response = requests.post(
        f"{PAYPAL_BASE_URL}/v1/oauth2/token",
        auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET),
        headers={"Accept": "application/json"},
        data={"grant_type": "client_credentials"},
        timeout=30
    )

    response.raise_for_status()
    return response.json()["access_token"]


def create_paypal_order(amount):
    if float(amount) <= 0:
        raise ValueError("Payment amount must be greater than zero.")

    access_token = get_paypal_access_token()

    response = requests.post(
        f"{PAYPAL_BASE_URL}/v2/checkout/orders",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "intent": "CAPTURE",
            "payment_source": {
                "paypal": {
                    "experience_context": {
                        "return_url": "https://example.com/payment/success",
                        "cancel_url": "https://example.com/payment/cancel",
                        "user_action": "PAY_NOW"
                    }
                }
            },
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": "USD",
                        "value": f"{float(amount):.2f}"
                    }
                }
            ]
        },
        timeout=30
    )

    response.raise_for_status()
    return response.json()
