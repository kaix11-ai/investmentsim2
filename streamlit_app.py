import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import gc

st.title("Investment Portfolio Simulator")

# Cache the data loading function to avoid reloading it multiple times
@st.cache_data
def load_data():
    # Load only necessary columns and optimize data types
    df = pd.read_csv('https://github.com/kaix11-ai/investmentsim2/blob/main/TQQQ_v2.csv', usecols=['Date', 'Close', 'Open'], parse_dates=['Date'], dtype={'Close': 'float32', 'Open': 'float32'})
    return df

# Load the data
df = load_data()

# User Inputs
start_date = st.date_input("Investment Start Date", min_value=df['Date'].min(), max_value=df['Date'].max())
initial_investment = st.number_input("Initial Investment Amount", min_value=0.0, step=100.0)
recurring_amount = st.number_input("Recurring Investment Amount", min_value=0.0, step=100.0)
frequency = st.selectbox("Recurring Investment Frequency", ["Weekly", "Monthly", "Quarterly"])
condition_percentage = st.slider("Investment Condition (if close is below X% of last 90 days low)", min_value=0, max_value=100, value=10)

frequency_days = {'Weekly': 7, 'Monthly': 30, 'Quarterly': 90}[frequency]

# Filter the data and create a copy to avoid SettingWithCopyWarning
df_filtered = df[df['Date'] >= pd.to_datetime(start_date)].copy()

# Calculate the 90-day low for the condition
df_filtered['90_day_low'] = df_filtered['Close'].rolling(window=90, min_periods=1).min()

# Initialize variables for the investment simulation
portfolio_value = initial_investment
investment_dates = []
portfolio_values = []
current_date = start_date

# Simulate the investment strategy
for index, row in df_filtered.iterrows():
    if current_date > row['Date']:
        continue

    if row['Date'] >= current_date:
        if row['Close'] < (1 - condition_percentage / 100) * row['90_day_low']:
            portfolio_value += recurring_amount

        investment_dates.append(row['Date'])
        portfolio_values.append(portfolio_value)

        current_date += timedelta(days=frequency_days)

# Plot the portfolio development
st.subheader("Portfolio Value Development Over Time")
plt.figure(figsize=(10, 6), dpi=80)  # Use a lower DPI for less memory usage
plt.plot(investment_dates, portfolio_values, label="Portfolio Value")
plt.xlabel("Date")
plt.ylabel("Portfolio Value")
plt.title("Investment Portfolio Value Over Time")
plt.legend()
st.pyplot(plt)

# Display the final portfolio value
st.write(f"Final Portfolio Value: ${portfolio_value:,.2f}")

# Force garbage collection to free up unused memory
del df, df_filtered
gc.collect()
