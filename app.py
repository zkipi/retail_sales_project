import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Retail Sales Insights Dashboard",
    page_icon="🛍️",
    layout="wide"
)

# --- 2. LOAD AND PREPARE DATA ---
@st.cache_data
def load_and_clean_data():
    # Load dataset
    df = pd.read_csv("data/retail_sales_dataset.csv")
    
    # Convert date column to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Feature Engineering
    df['Month'] = df['Date'].dt.month_name()
    df['Day_of_Week'] = df['Date'].dt.day_name()
    df['Year_Month'] = df['Date'].dt.to_period('M').astype(str)
    
    # Create Age Groups
    bins = [0, 25, 35, 45, 55, 100]
    labels = ['18-24', '25-34', '35-44', '45-54', '55+']
    df['Age Group'] = pd.cut(df['Age'], bins=bins, labels=labels, right=False)
    
    return df

try:
    df = load_and_clean_data()
except FileNotFoundError:
    st.error("Error: 'retail_sales_dataset.csv' not found. Please ensure the file is in the same directory as this script.")
    st.stop()

# --- 3. SIDEBAR (FILTERS) ---
st.sidebar.header("Dashboard Filters")

# Date Filter
min_date = df['Date'].min().to_pydatetime()
max_date = df['Date'].max().to_pydatetime()
date_range = st.sidebar.date_input("Select Date Range:", [min_date, max_date])

# Category Filter
categories = st.sidebar.multiselect(
    "Select Product Categories:",
    options=df["Product Category"].unique(),
    default=df["Product Category"].unique()
)

# Gender Filter
genders = st.sidebar.multiselect(
    "Select Gender:",
    options=df["Gender"].unique(),
    default=df["Gender"].unique()
)

# Apply Filter Logic
mask = (
    (df['Date'].dt.date >= date_range[0]) & 
    (df['Date'].dt.date <= date_range[1]) &
    (df['Product Category'].isin(categories)) &
    (df['Gender'].isin(genders))
)
df_filtered = df.loc[mask]

# --- 4. MAIN LAYOUT & KPIs ---
st.title("📊 Retail Sales Analysis Dashboard")
st.markdown("""
This dashboard provides a deep dive into retail transaction data to uncover customer behavior, 
product performance, and seasonal trends. Use the sidebar to filter the data.
""")

# Key Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${df_filtered['Total Amount'].sum():,.0f}")
col2.metric("Total Transactions", f"{len(df_filtered):,}")
col3.metric("Avg. Transaction Value", f"${df_filtered['Total Amount'].mean():.2f}")
col4.metric("Average Customer Age", f"{df_filtered['Age'].mean():.1f} yrs")

st.divider()

# --- 5. VISUALIZATIONS ---

# Row 1: Time Series Trend
st.subheader("📈 Monthly Revenue Trend")
trend_data = df_filtered.groupby('Year_Month')['Total Amount'].sum()
st.line_chart(trend_data)
st.caption("This chart tracks the total revenue growth over the selected time period.")

# Row 2: Demographics & Product Categories
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Revenue by Age Group")
    fig1, ax1 = plt.subplots()
    sns.barplot(data=df_filtered, x='Age Group', y='Total Amount', estimator=sum, palette='viridis', ax=ax1)
    ax1.set_ylabel("Total Sales ($)")
    st.pyplot(fig1)
    st.info("Insight: This visual highlights which age demographic is our most valuable customer segment.")

with col_right:
    st.subheader("Sales Distribution by Gender")
    fig2, ax2 = plt.subplots()
    gender_counts = df_filtered['Gender'].value_counts()
    ax2.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', startangle=140, colors=['#87CEEB','#FFB6C1'])
    st.pyplot(fig2)

# Row 3: Weekdays & Product Pricing
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Most Popular Shopping Days")
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    fig3, ax3 = plt.subplots()
    sns.countplot(data=df_filtered, x='Day_of_Week', order=day_order, palette='magma', ax=ax3)
    plt.xticks(rotation=45)
    st.pyplot(fig3)

with col_b:
    st.subheader("Price Range by Category")
    fig4, ax4 = plt.subplots()
    sns.boxplot(data=df_filtered, x='Product Category', y='Price per Unit', ax=ax4)
    plt.xticks(rotation=45)
    st.pyplot(fig4)
    st.info("Analysis: Use this to check for price consistency or premium products across categories.")

# --- 6. DATA EXPLORER ---
st.divider()
with st.expander("🔍 View Raw Filtered Data"):
    st.write(df_filtered)