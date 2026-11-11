
import streamlit as st
import pandas as pd
from datetime import date

from database import (
    create_table,
    add_expense,
    get_expenses,
    delete_expense,
    add_savings_goal,
    get_savings_goals,
    update_saved_amount,
    delete_savings_goal
)
from paypal_integration import (
    create_paypal_order,
    capture_paypal_order
)

from database import (
    save_paypal_order,
    complete_paypal_payment,
    update_paypal_payment_status,
    get_paypal_payments
)

from ai_insights import generate_insights


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="SpendWise AI",
    page_icon="💰",
    layout="wide"
)

create_table()


# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------

st.markdown("""
<style>
    .main {
        background-color: #FFFFFF;
    }

    h1, h2, h3 {
        color: #172B4D;
    }

    div[data-testid="stMetric"] {
        background-color: #F2F6FC;
        padding: 15px;
        border-radius: 10px;
    }

    .stButton button {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

records = get_expenses()
goals = get_savings_goals()

today = date.today()
current_month = today.month
current_year = today.year

monthly_records = [
    record for record in records
    if pd.to_datetime(record[4]).month == current_month
    and pd.to_datetime(record[4]).year == current_year
]

monthly_spending = sum(
    float(record[2]) for record in monthly_records
)

all_time_spending = sum(
    float(record[2]) for record in records
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.title("💰 SpendWise AI")

    st.caption("Smart Personal Finance Assistant")

    st.divider()

    page = st.radio(
        "Navigation",
        [
    "Dashboard",
    "Expenses",
    "AI Assistant",
    "Savings Goals",
    "Financial Summary",
    "PayPal Payments"
]
    )

    st.divider()

    st.subheader("Monthly Budget")

    budget = st.number_input(
        "Set your monthly budget (₹)",
        min_value=0.0,
        value=10000.0,
        step=500.0,
        key="monthly_budget"
    )

    st.divider()

    st.caption("Spend smarter. Save better.")

    st.caption("SpendWise AI | Built with Streamlit")


# --------------------------------------------------
# MAIN HEADER
# --------------------------------------------------

st.title("💰 SpendWise AI")

st.caption("Your personal finance companion")

st.divider()


# ==================================================
# 1. DASHBOARD
# ==================================================

if page == "Dashboard":

    st.header("📊 Financial Dashboard")

    st.write(
        "Get a quick overview of your spending and budget."
    )

    remaining_budget = budget - monthly_spending

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Monthly Budget",
        f"₹{budget:,.2f}"
    )

    col2.metric(
        "Total Spent",
        f"₹{monthly_spending:,.2f}"
    )

    col3.metric(
        "Remaining Budget",
        f"₹{remaining_budget:,.2f}",
        delta=f"₹{remaining_budget:,.2f}"
    )

    st.subheader("Monthly Budget Usage")

    if budget > 0:

        spending_ratio = monthly_spending / budget

        st.progress(
            min(spending_ratio, 1.0)
        )

        st.write(
            f"You have used {spending_ratio * 100:.1f}% "
            "of your monthly budget."
        )

    else:
        st.info("Set a monthly budget to see your budget usage.")

    if remaining_budget < 0:
        st.error(
            f"You have exceeded your budget by "
            f"₹{abs(remaining_budget):,.2f}."
        )

    elif budget > 0:
        st.success(
            f"You have ₹{remaining_budget:,.2f} remaining."
        )

    st.divider()

    st.subheader("Spending by Category")

    if monthly_records:

        df = pd.DataFrame(
            monthly_records,
            columns=[
                "ID",
                "Expense",
                "Amount",
                "Category",
                "Date"
            ]
        )

        category_summary = (
            df.groupby("Category")["Amount"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(category_summary)

        st.subheader("Recent Expenses")

        recent_df = df[
            ["Expense", "Amount", "Category", "Date"]
        ].head(5)

        st.dataframe(
            recent_df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info(
            "No expenses recorded this month. "
            "Add your first expense from the Expenses page."
        )


# ==================================================
# 2. EXPENSES
# ==================================================

elif page == "Expenses":

    st.header("🧾 Expense Management")

    st.write(
        "Add, search, filter and manage your expenses."
    )

    st.subheader("Add a New Expense")

    with st.form("add_expense_form"):

        expense_name = st.text_input(
            "Expense Name",
            placeholder="Example: Lunch"
        )

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            step=10.0
        )

        category = st.selectbox(
            "Category",
            [
                "Food",
                "Travel",
                "Education",
                "Shopping",
                "Entertainment",
                "Health",
                "Bills",
                "Other"
            ]
        )

        expense_date = st.date_input(
            "Expense Date",
            value=date.today()
        )

        submitted = st.form_submit_button(
            "Add Expense"
        )

        if submitted:

            if not expense_name.strip():
                st.error("Please enter an expense name.")

            elif amount <= 0:
                st.error("Please enter an amount greater than zero.")

            else:

                add_expense(
                    expense_name.strip(),
                    amount,
                    category,
                    expense_date
                )

                st.success("Expense added successfully!")

                st.rerun()

    st.divider()

    st.subheader("Your Expenses")

    records = get_expenses()

    if records:

        df = pd.DataFrame(
            records,
            columns=[
                "ID",
                "Expense",
                "Amount",
                "Category",
                "Date"
            ]
        )

        search_text = st.text_input(
            "Search expenses",
            placeholder="Search by expense name..."
        )

        categories = ["All"] + sorted(
            df["Category"].unique().tolist()
        )

        selected_category = st.selectbox(
            "Filter by Category",
            categories
        )

        filtered_df = df.copy()

        if search_text.strip():

            filtered_df = filtered_df[
                filtered_df["Expense"].str.contains(
                    search_text,
                    case=False,
                    na=False
                )
            ]

        if selected_category != "All":

            filtered_df = filtered_df[
                filtered_df["Category"] == selected_category
            ]

        st.dataframe(
            filtered_df[
                ["ID", "Expense", "Amount", "Category", "Date"]
            ],
            use_container_width=True,
            hide_index=True
        )

        csv_data = filtered_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="⬇️ Download Expenses as CSV",
            data=csv_data,
            file_name="spendwise_expenses.csv",
            mime="text/csv"
        )

        st.divider()

        st.subheader("Delete an Expense")

        expense_options = {
            f"{record[1]} — ₹{record[2]:,.2f} — {record[4]} "
            f"(ID: {record[0]})": record[0]
            for record in records
        }

        selected_expense = st.selectbox(
            "Select an expense to delete",
            list(expense_options.keys())
        )

        if st.button("Delete Selected Expense"):

            delete_expense(
                expense_options[selected_expense]
            )

            st.success("Expense deleted successfully!")

            st.rerun()

    else:
        st.info("You haven't added any expenses yet.")


# ==================================================
# 3. AI ASSISTANT
# ==================================================

elif page == "AI Assistant":

    st.header("🤖 Ask SpendWise AI")

    st.write(
        "Get personalised spending insights and practical "
        "saving suggestions using Gemini AI."
    )

    st.info(
        "Your current-month expense names, amounts, categories, "
        "dates and budget will be shared with Gemini when you "
        "submit a question. Continue only if you consent."
    )

    consent = st.checkbox(
        "I agree to share my expense data with Gemini for analysis."
    )

    question = st.text_area(
        "Ask your financial question",
        placeholder=(
            "Example: How can I reduce my monthly expenses?"
        )
    )

    if st.button("Ask Gemini"):

        if not consent:

            st.warning(
                "Please provide consent before continuing."
            )

        elif not question.strip():

            st.warning(
                "Please enter a question."
            )

        elif not monthly_records:

            st.warning(
                "No expenses found for the current month. "
                "Add some expenses before requesting insights."
            )

        else:

            st.write(
                "Expenses sent to Gemini:",
                len(monthly_records)
            )

            with st.spinner(
                "SpendWise AI is analysing your expenses..."
            ):

                answer = generate_insights(
                    monthly_records,
                    budget,
                    question.strip()
                )

            st.subheader("💬 SpendWise AI Response")

            st.markdown(answer)


# ==================================================
# 4. SAVINGS GOALS
# ==================================================

elif page == "Savings Goals":

    st.header("🎯 Savings Goals")

    st.write(
        "Create savings goals and track your progress."
    )

    st.subheader("Create a New Goal")

    with st.form("savings_goal_form"):

        goal_name = st.text_input(
            "Goal Name",
            placeholder="Example: Buy a Laptop"
        )

        target_amount = st.number_input(
            "Target Amount (₹)",
            min_value=1.0,
            value=10000.0,
            step=500.0
        )

        deadline = st.date_input(
            "Target Date",
            value=date.today()
        )

        goal_submitted = st.form_submit_button(
            "Create Savings Goal"
        )

        if goal_submitted:

            if not goal_name.strip():

                st.error("Please enter a goal name.")

            elif deadline < date.today():

                st.error("Please choose a future target date.")

            else:

                add_savings_goal(
                    goal_name.strip(),
                    target_amount,
                    deadline
                )

                st.success("Savings goal created!")

                st.rerun()

    st.divider()

    st.subheader("Your Savings Goals")

    goals = get_savings_goals()

    if goals:

        for goal in goals:

            (
                goal_id,
                goal_name,
                target_amount,
                saved_amount,
                deadline
            ) = goal

            target_amount = float(target_amount)
            saved_amount = float(saved_amount)

            progress = (
                saved_amount / target_amount
                if target_amount > 0
                else 0
            )

            with st.container(border=True):

                st.subheader(f"🎯 {goal_name}")

                col1, col2 = st.columns(2)

                col1.metric(
                    "Target Amount",
                    f"₹{target_amount:,.2f}"
                )

                col2.metric(
                    "Saved Amount",
                    f"₹{saved_amount:,.2f}"
                )

                st.progress(
                    min(progress, 1.0)
                )

                st.write(
                    f"Progress: {progress * 100:.1f}%"
                )

                st.write(
                    f"Target date: {deadline}"
                )

                remaining = max(
                    target_amount - saved_amount,
                    0
                )

                st.write(
                    f"Amount remaining: ₹{remaining:,.2f}"
                )

                if saved_amount >= target_amount:

                    st.success("Congratulations! Goal achieved!")

                else:

                    contribution = st.number_input(
                        "Add savings contribution (₹)",
                        min_value=0.0,
                        step=100.0,
                        key=f"contribution_{goal_id}"
                    )

                    col_add, col_delete = st.columns(2)

                    with col_add:

                        if st.button(
                            "Add Contribution",
                            key=f"add_{goal_id}"
                        ):

                            if contribution <= 0:

                                st.warning(
                                    "Enter a contribution greater than zero."
                                )

                            else:

                                update_saved_amount(
                                    goal_id,
                                    contribution
                                )

                                st.success(
                                    "Contribution added successfully!"
                                )

                                st.rerun()

                    with col_delete:

                        if st.button(
                            "Delete Goal",
                            key=f"delete_{goal_id}"
                        ):

                            delete_savings_goal(goal_id)

                            st.success("Savings goal deleted.")

                            st.rerun()

    else:

        st.info(
            "No savings goals yet. Create your first goal above."
        )


# ==================================================
# 5. FINANCIAL SUMMARY
# ==================================================

elif page == "Financial Summary":

    st.header("📈 Financial Summary")

    st.write(
        "Understand your monthly and overall financial activity."
    )

    remaining_budget = budget - monthly_spending

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Current Month Spending",
        f"₹{monthly_spending:,.2f}"
    )

    col2.metric(
        "Budget Remaining",
        f"₹{remaining_budget:,.2f}"
    )

    col3.metric(
        "All-Time Spending",
        f"₹{all_time_spending:,.2f}"
    )

    st.divider()

    st.subheader("Monthly Expense Breakdown")

    if monthly_records:

        df = pd.DataFrame(
            monthly_records,
            columns=[
                "ID",
                "Expense",
                "Amount",
                "Category",
                "Date"
            ]
        )

        category_summary = (
            df.groupby("Category")["Amount"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(category_summary)

        st.subheader("Expense Details")

        st.dataframe(
            df[
                ["Expense", "Amount", "Category", "Date"]
            ],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No expenses recorded in the current month."
        )

    st.divider()

    st.subheader("Savings Overview")

    goals = get_savings_goals()

    if goals:

        total_target = sum(
            float(goal[2]) for goal in goals
        )

        total_saved = sum(
            float(goal[3]) for goal in goals
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Number of Goals",
            len(goals)
        )

        col2.metric(
            "Total Target",
            f"₹{total_target:,.2f}"
        )

        col3.metric(
            "Total Saved",
            f"₹{total_saved:,.2f}"
        )

    else:

        st.info(
            "Create a savings goal to see your savings overview."
        )

# --------------------------------------------------
# PAYPAL PAYMENTS
# --------------------------------------------------


# --------------------------------------------------
# PAYPAL PAYMENTS
# --------------------------------------------------

elif page == "PayPal Payments":

    st.title("💳 PayPal Payments")

    st.write(
        "Create and test secure payments using PayPal Sandbox."
    )

    st.info(
        "This is a Sandbox demonstration. "
        "Payments are made using test accounts, not real money."
    )

    app_url = (
        "https://spendwise-aigit-etpgbbispmauucnifnwmca.streamlit.app/"
    )

    return_url = app_url + "?paypal=return"
    cancel_url = app_url + "?paypal=cancel"

    paypal_action = st.query_params.get("paypal")
    returned_order_id = st.query_params.get("token")

    # ----------------------------------------------
    # HANDLE CANCELLED PAYMENT
    # ----------------------------------------------

    if paypal_action == "cancel":

        st.warning(
            "Payment was cancelled. "
            "No completed payment was recorded."
        )

    # ----------------------------------------------
    # HANDLE PAYPAL RETURN
    # ----------------------------------------------

    elif paypal_action == "return" and returned_order_id:

        st.subheader("Verify and Record Your Payment")

        payments = get_paypal_payments()

        saved_order = next(
            (
                payment
                for payment in payments
                if payment[1] == returned_order_id
            ),
            None
        )

        if saved_order is None:

            st.error(
                "This PayPal order was not found "
                "in SpendWise AI."
            )

        else:

            st.write(
                f"Payment description: {saved_order[3]}"
            )

            st.write(
                f"Original payment: "
                f"{saved_order[5]} {saved_order[4]:.2f}"
            )

            if saved_order[6] == "COMPLETED":

                st.success(
                    "PayPal capture is already completed. "
                    "We will not capture it again."
                )

                if not saved_order[2]:
                    st.error(
                        "The completed payment has no saved capture ID. "
                        "Please inspect the database before proceeding."
                    )

            else:

                st.info(
                    "Your payment has returned from PayPal. "
                    "Click the button below to capture and verify it."
                )

            st.divider()

            st.subheader("USD to INR Conversion")

            exchange_rate = st.number_input(
                "Enter INR value for 1 USD",
                min_value=0.0,
                value=0.0,
                step=0.1,
                format="%.4f",
                key=f"paypal_rate_{returned_order_id}"
            )

            st.caption(
                "Enter the exchange rate you want to use "
                "for your expense record. The original USD "
                "amount remains unchanged in PayPal history."
            )

            if st.button(
                "Verify Payment and Record INR Expense",
                type="primary",
                key=f"verify_paypal_{returned_order_id}"
            ):

                if exchange_rate <= 0:

                    st.error(
                        "Please enter a valid USD to INR exchange rate."
                    )

                elif (
                    saved_order[6] == "COMPLETED"
                    and not saved_order[2]
                ):

                    st.error(
                        "Capture ID is missing. "
                        "Please inspect the saved payment."
                    )

                else:

                    try:

                        # If already completed, reuse its capture ID.
                        # Never capture the same completed order again.

                        if saved_order[6] == "COMPLETED":

                            verified_payment = {
                                "order_id": saved_order[1],
                                "capture_id": saved_order[2],
                                "amount": float(saved_order[4]),
                                "currency": saved_order[5]
                            }

                        else:

                            # Capture and verify with PayPal.
                            verified_payment = capture_paypal_order(
                                returned_order_id,
                                saved_order[4],
                                saved_order[5]
                            )

                        # Save payment status and INR expense
                        # together in one database transaction.

                        result = complete_paypal_payment(
                            verified_payment["order_id"],
                            verified_payment["capture_id"],
                            exchange_rate
                        )

                        st.success(
                            "Payment verified successfully!"
                        )

                        if result["expense_created"]:

                            st.success(
                                "INR expense created automatically!"
                            )

                        else:

                            st.info(
                                "This payment's expense was already "
                                "recorded. No duplicate was created."
                            )

                        st.metric(
                            "Expense Recorded",
                            f"₹{result['expense_amount_inr']:,.2f}"
                        )

                        st.write(
                            f"Original payment: "
                            f"{verified_payment['currency']} "
                            f"{verified_payment['amount']:.2f}"
                        )

                        st.write(
                            f"Exchange rate: "
                            f"₹{exchange_rate:.4f} per USD"
                        )

                        st.write(
                            f"Expense ID: {result['expense_id']}"
                        )

                        st.write(
                            f"Capture ID: "
                            f"{verified_payment['capture_id']}"
                        )

                    except Exception as error:

                        st.error(
                            f"Payment verification failed: {error}"
                        )

    st.divider()

    # ----------------------------------------------
    # CREATE NEW PAYPAL ORDER
    # ----------------------------------------------

    st.subheader("Create a Sandbox Payment")

    with st.form("paypal_payment_form"):

        payment_description = st.text_input(
            "Payment Description",
            placeholder="Example: Online purchase"
        )

        payment_amount = st.number_input(
            "Payment Amount (USD)",
            min_value=1.0,
            value=10.0,
            step=1.0
        )

        create_payment = st.form_submit_button(
            "Create PayPal Payment"
        )

    if create_payment:

        try:

            order = create_paypal_order(
                payment_amount,
                payment_description,
                return_url,
                cancel_url
            )

            save_paypal_order(
                order["id"],
                payment_description,
                payment_amount,
                "USD"
            )

            st.session_state["paypal_approval_url"] = (
                order["approval_url"]
            )

            st.session_state["paypal_order_id"] = (
                order["id"]
            )

            st.success(
                "PayPal order created successfully!"
            )

        except Exception as error:

            st.error(
                f"Could not create PayPal order: {error}"
            )

    # ----------------------------------------------
    # DISPLAY APPROVAL LINK
    # ----------------------------------------------

    if st.session_state.get("paypal_approval_url"):

        st.subheader("Approve Your Payment")

        st.write(
            "Click below to open PayPal Sandbox "
            "and approve your test payment."
        )

        st.link_button(
            "Open PayPal to Approve Payment",
            st.session_state["paypal_approval_url"],
            type="primary"
        )

        st.caption(
            "After approval, PayPal will redirect you "
            "to SpendWise AI for verification."
        )

        st.caption(
            f"Order ID: "
            f"{st.session_state.get('paypal_order_id', '')}"
        )

    st.divider()

    # ----------------------------------------------
    # PAYPAL PAYMENT HISTORY
    # ----------------------------------------------

    st.subheader("PayPal Payment History")

    payment_history = get_paypal_payments()

    if payment_history:

        payment_df = pd.DataFrame(
            payment_history,
            columns=[
                "ID",
                "Order ID",
                "Capture ID",
                "Description",
                "Amount",
                "Currency",
                "Status",
                "Created At"
            ]
        )

        st.dataframe(
            payment_df[
                [
                    "Description",
                    "Amount",
                    "Currency",
                    "Status",
                    "Created At"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No PayPal payments recorded yet. "
            "Create your first Sandbox payment above."
        )
