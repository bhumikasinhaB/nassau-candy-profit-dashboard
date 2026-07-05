import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Nassau Candy Profit App", layout="wide")

st.title("🍬 Nassau Candy Distributor: Profitability Dashboard")
st.markdown("Use this interactive dashboard to analyze product margins and isolate pricing leaks.")
st.markdown("---")

# 2. Optimized Data Loading
@st.cache_data
def load_and_clean_data():
    df = pd.read_csv("Nassau Candy Distributor.csv")
    df.columns = df.columns.str.strip()
    
    cleaned_df = df.dropna(subset=['Product Name', 'Sales', 'Cost', 'Units'])
    cleaned_df['Sales'] = pd.to_numeric(cleaned_df['Sales'], errors='coerce')
    cleaned_df['Cost'] = pd.to_numeric(cleaned_df['Cost'], errors='coerce')
    cleaned_df['Units'] = pd.to_numeric(cleaned_df['Units'], errors='coerce')
    
    cleaned_df['Total_Cost'] = cleaned_df['Units'] * cleaned_df['Cost']
    cleaned_df['Calculated_Profit'] = cleaned_df['Sales'] - cleaned_df['Total_Cost']
    cleaned_df['Gross_Margin_Percent'] = (cleaned_df['Calculated_Profit'] / cleaned_df['Sales']) * 100
    
    return cleaned_df

df = load_and_clean_data()

# 3. Sidebar Controls
st.sidebar.header("🎯 Filter Control Panel")
selected_division = st.sidebar.multiselect(
    "Select Product Division:",
    options=df['Division'].unique(),
    default=df['Division'].unique()
)

filtered_df = df[df['Division'].isin(selected_division)]

# 4. Executive Financial Overview Metrics
st.subheader("📊 Executive Financial Overview")

total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Calculated_Profit'].sum()
overall_margin = (total_profit / total_sales) * 100 if total_sales != 0 else 0

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Revenue (Sales)", value=f"${total_sales:,.2f}")
with col2:
    st.metric(label="Total Gross Profit", value=f"${total_profit:,.2f}", delta=f"${total_profit:,.2f}", delta_color="inverse")
with col3:
    st.metric(label="Overall Gross Margin %", value=f"{overall_margin:.2f}%")

st.markdown("---")

# 5. Visual Analytics: Top Financial Drainers
st.subheader("🚨 Top 10 Product Profit Drains")
st.markdown("This chart automatically highlights the candy products costing the company the most money.")

# Isolate the top 10 products with the lowest calculated profit numbers
top_losses = filtered_df.sort_values(by="Calculated_Profit", ascending=True).head(10)

if not top_losses.empty:
    fig = px.bar(
        top_losses,
        x="Calculated_Profit",
        y="Product Name",
        orientation="h",
        color="Calculated_Profit",
        color_continuous_scale=["#d9534f", "#f0ad4e"],
        labels={"Calculated_Profit": "Loss Amount ($)", "Product Name": "Product"},
        title="Deepest Deficits (Negative Values = Losses)"
    )
    fig.update_layout(yaxis={'categoryorder': 'total descending'}, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No negative margin products found for the selected divisions.")

st.markdown("---")

# 6. Lightning-Fast Native Ledger & Download Utility
st.subheader("🔍 Deep-Dive Product Performance Ledger")

display_columns = ['Product Name', 'Division', 'Sales', 'Units', 'Total_Cost', 'Calculated_Profit', 'Gross_Margin_Percent']
ledger_df = filtered_df[display_columns].copy()

# Add Data Export Utility Button
csv_data = ledger_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Export Current Filtered Ledger to CSV",
    data=csv_data,
    file_name="nassau_filtered_margins.csv",
    mime="text/csv"
)

st.dataframe(
    ledger_df, 
    use_container_width=True, 
    hide_index=True,
    column_config={
        "Sales": st.column_config.NumberColumn(format="$%.2f"),
        "Total_Cost": st.column_config.NumberColumn(format="$%.2f"),
        "Calculated_Profit": st.column_config.NumberColumn(format="$%.2f"),
        "Gross_Margin_Percent": st.column_config.NumberColumn(format="%.2f%%")
    }
)
