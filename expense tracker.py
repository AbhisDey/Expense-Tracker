import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import numpy as np

# Currency Conversion API
CURRENCY_API = "https://api.exchangerate-api.com/v4/latest/INR"

try:
    response = requests.get(CURRENCY_API)
    response.raise_for_status()  # Raise HTTPError for bad responses
    data = response.json()
    vnd_rate = data['rates']['VND']
except requests.exceptions.RequestException as e:
    st.error("⚠️ Failed to fetch the latest currency conversion rate. Using a default rate of ₹1 = 300 VND")
    vnd_rate = 300  # Default conversion rate in case of API failure

# Initialize session state for expenses
if 'expenses' not in st.session_state:
    st.session_state['expenses'] = []

# App title
st.title("Vietnam Trip Expense Tracker")

# Input fields
st.header("Add Expense")
category = st.selectbox("Category", ["Flight", "Hotel", "Food", "Transport", "Sightseeing", "Shopping", "Miscellaneous", "Personal Shopping"])
date = st.date_input("Date")
amount = st.number_input("Amount (in ₹)", min_value=0.0, format='%.2f')
description = st.text_input("Description")

if st.button("Add Expense"):
    vnd_amount = amount * vnd_rate
    st.session_state['expenses'].append({
        'Date': date,
        'Category': category,
        'Amount (₹)': amount,
        'Amount (VND)': vnd_amount,
        'Description': description
    })

# Display the expenses in a table
st.header("Expense Summary")
if len(st.session_state['expenses']) > 0:
    df = pd.DataFrame(st.session_state['expenses'])
    st.dataframe(df)

    # Calculate total expense
    total_expense = df['Amount (₹)'].sum()
    st.write(f"### Total Expense: ₹{total_expense:.2f}")

    # Plot expenses by category
    st.write("### Expense Breakdown")
    fig, ax = plt.subplots()
    df.groupby('Category')['Amount (₹)'].sum().plot(kind='pie', autopct='%1.1f%%', ax=ax)
    ax.set_ylabel('')
    ax.set_title('Expense Distribution by Category')
    ax.legend(loc='best')
    st.pyplot(fig)

    # Plot spending trend by date
    st.write("### Daily Spending Trend")
    fig, ax = plt.subplots()
    df.groupby('Date')['Amount (₹)'].sum().plot(kind='line', marker='o', ax=ax)
    ax.set_ylabel('Amount (₹)')
    ax.set_title('Spending Trend Over Time')
    st.pyplot(fig)

    # Download the expenses as CSV
    st.download_button(
        label="Download CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name='vietnam_expenses.csv',
        mime='text/csv'
    )
else:
    st.write("No expenses added yet.")

# Remaining budget alert
st.sidebar.header("Budget Tracker")
total_budget = st.sidebar.number_input("Total Trip Budget (in ₹)", min_value=0.0, format='%.2f')
trip_days = st.sidebar.number_input("Total Trip Days", min_value=1, value=6)

if total_budget > 0:
    remaining_budget = total_budget - total_expense
    st.sidebar.write(f"### Remaining Budget: ₹{remaining_budget:.2f}")

    if remaining_budget < 0:
        st.sidebar.error("⚠️ You have exceeded your budget!")
    else:
        st.sidebar.success("✅ You are within your budget.")

    # Expense Forecasting
    daily_spending = total_expense / len(df['Date'].unique())
    projected_expense = daily_spending * trip_days

    st.sidebar.write(f"💸 **Projected Total Expense:** ₹{projected_expense:.2f}")

    if projected_expense > total_budget:
        st.sidebar.error("⚠️ You are likely to exceed your budget!")
    else:
        remaining_daily_budget = remaining_budget / (trip_days - len(df['Date'].unique()))
        st.sidebar.write(f"💵 **Suggested Daily Budget:** ₹{remaining_daily_budget:.2f}")

# Show real-time conversion rate
st.sidebar.write(f"💱 Current INR to VND Rate: ₹1 = {vnd_rate:.2f} VND")
