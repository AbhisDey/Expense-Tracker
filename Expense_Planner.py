import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import numpy as np
import datetime

# Currency Conversion API
CURRENCY_API = "https://api.exchangerate-api.com/v4/latest/INR"

try:
    response = requests.get(CURRENCY_API)
    response.raise_for_status()
    data = response.json()
    vnd_rate = data['rates']['VND']
except requests.exceptions.RequestException as e:
    st.error("⚠️ Failed to fetch the latest currency conversion rate. Using a default rate of ₹1 = 300 VND")
    vnd_rate = 300

# Initialize session state for expenses
if 'expenses' not in st.session_state:
    st.session_state['expenses'] = []

if 'category_limits' not in st.session_state:
    st.session_state['category_limits'] = {}

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

# Set category-wise budget limits
st.sidebar.header("Set Category-wise Budget")
for cat in ["Flight", "Hotel", "Food", "Transport", "Sightseeing", "Shopping", "Miscellaneous", "Personal Shopping"]:
    limit = st.sidebar.number_input(f"{cat} Budget (in ₹)", min_value=0.0, format='%.2f')
    st.session_state['category_limits'][cat] = limit

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

    # Inbuilt Calculator
    st.sidebar.header("Quick Calculator")
    num1 = st.sidebar.number_input("Enter Number 1", value=0)
    num2 = st.sidebar.number_input("Enter Number 2", value=0)
    operation = st.sidebar.selectbox("Operation", ["Add", "Subtract", "Multiply", "Divide"])
    if operation == "Add":
        st.sidebar.write(f"Result: {num1 + num2}")
    elif operation == "Subtract":
        st.sidebar.write(f"Result: {num1 - num2}")
    elif operation == "Multiply":
        st.sidebar.write(f"Result: {num1 * num2}")
    elif operation == "Divide" and num2 != 0:
        st.sidebar.write(f"Result: {num1 / num2}")

    # Check category budget limits
    st.write("### Category-wise Budget Tracking")
    for cat in st.session_state['category_limits'].keys():
        spent = df[df['Category'] == cat]['Amount (₹)'].sum()
        limit = st.session_state['category_limits'][cat]
        if spent > limit > 0:
            st.warning(f"⚠️ Over Budget for {cat}! Spent ₹{spent:.2f} out of ₹{limit:.2f}")

# Show real-time conversion rate
st.sidebar.write(f"💱 Current INR to VND Rate: ₹1 = {vnd_rate:.2f} VND")
