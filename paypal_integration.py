
import os
from pathlib import Path
from decimal import Decimal, InvalidOperation

import requests
import streamlit as st
from dotenv import load_dotenv

# Load local environment variables
env_path = Path(__file__).with_name(".env")
load_dotenv(env_path)


def get_paypal_credentials():
    """Load PayPal credentials from .env or Streamlit Secrets."""

    client_id = os.getenv("PAYPAL_CLIENT_ID")
    client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
    base_url = os.getenv("PAYPAL_BASE_URL")

    try:
        client_id = client_id or st.secrets["PAYPAL_CLIENT_ID"]
        client_secret = client_secret or st.secrets["PAYPAL_CLIENT_SECRET"]
        base_url = base_url or st.secrets.get(
            "PAYPAL_BASE_URL",
            "https://api-m.sandbox.paypal.com"
        )
    except Exception:
        pass

    if not client_id or not client_secret:
        raise ValueError(
            "PayPal credentials are missing. "
            "Check your .env file or Streamlit Secrets."
        )

    return (
        client_id,
        client_secret,
        base_url.rstrip("/")
    )


def get_paypal_access_token():
    """Generate PayPal OAuth access token."""

    client_id, client_secret, base_url = get_paypal_credentials()

    response = requests.post(
        f"{base_url}/v1/oauth2/token",
        auth=(client_id, client_secret),
        headers={"Accept": "application/json"},
        data={"grant_type": "client_credentials"},
        timeout=30
    )

    if not response.ok:
        raise RuntimeError(
            f"PayPal authentication failed: {response.text}"
        )

    return response.json()["access_token"]


def create_paypal_order(
    amount,
    description,
    return_url,
    cancel_url
):
    """Create a PayPal Sandbox payment order."""

    try:
        payment_amount = Decimal(str(amount)).quantize(
            Decimal("0.01")
        )
    except (InvalidOperation, ValueError):
        raise ValueError("Enter a valid payment amount.")

    if not payment_amount.is_finite() or payment_amount <= 0:
        raise ValueError("Payment amount must be greater than zero.")

    if not description or not description.strip():
        raise ValueError("Enter a payment description.")

    if not return_url.startswith("https://") or not cancel_url.startswith("https://"):
        raise ValueError("Valid HTTPS return and cancel URLs are required.")

    access_token = get_paypal_access_token()
    _, _, base_url = get_paypal_credentials()

    response = requests.post(
        f"{base_url}/v2/checkout/orders",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "description": description.strip(),
                    "amount": {
                        "currency_code": "USD",
                        "value": format(payment_amount, ".2f")
                    }
                }
            ],
            "payment_source": {
                "paypal": {
                    "experience_context": {
                        "return_url": return_url,
                        "cancel_url": cancel_url,
                        "user_action": "PAY_NOW"
                    }
                }
            }
        },
        timeout=30
    )

    if not response.ok:
        raise RuntimeError(
            f"PayPal order creation failed: {response.text}"
        )

    order = response.json()

    approval_url = next(
        (
            link["href"]
            for link in order.get("links", [])
            if link.get("rel") in ("approve", "payer-action")
        ),
        None
    )

    if not approval_url:
        raise RuntimeError(
            "PayPal did not return an approval link."
        )

    order["approval_url"] = approval_url

    return order


def capture_paypal_order(
    order_id,
    expected_amount,
    expected_currency="USD"
):
    """Capture an approved order and verify its details."""

    if not order_id:
        raise ValueError("PayPal order ID is missing.")

    access_token = get_paypal_access_token()
    _, _, base_url = get_paypal_credentials()

    response = requests.post(
        f"{base_url}/v2/checkout/orders/{order_id}/capture",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        },
        json={},
        timeout=30
    )

    if not response.ok:
        raise RuntimeError(
            f"PayPal capture failed: {response.text}"
        )

    result = response.json()

    if result.get("status") != "COMPLETED":
        raise RuntimeError(
            "PayPal payment has not been completed."
        )

    try:
        expected = Decimal(
            str(expected_amount)
        ).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        raise ValueError("Invalid expected payment amount.")

    if not expected.is_finite() or expected <= 0:
        raise ValueError("Invalid expected payment amount.")

    # Verify captured payment details
    for purchase_unit in result.get("purchase_units", []):

        for capture in purchase_unit.get(
            "payments", {}
        ).get("captures", []):

            captured_amount = capture.get("amount", {})

            actual_currency = captured_amount.get(
                "currency_code"
            )

            actual_amount = Decimal(
                captured_amount.get("value", "0")
            ).quantize(Decimal("0.01"))

            if (
                capture.get("status") == "COMPLETED"
                and actual_currency == expected_currency
                and actual_amount == expected
                and capture.get("id")
            ):
                return {
                    "order_id": result["id"],
                    "capture_id": capture["id"],
                    "amount": float(actual_amount),
                    "currency": actual_currency
                }

    raise RuntimeError(
        "Payment verification failed. "
        "The captured amount or currency did not match."
    )
