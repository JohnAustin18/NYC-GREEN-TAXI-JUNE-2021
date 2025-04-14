import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Page Config
st.set_page_config(page_title="NYC Green Taxi Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_parquet("green_tripdata_2021-06.parquet")
    df['lpep_pickup_datetime'] = pd.to_datetime(df['lpep_pickup_datetime'])
    df['lpep_dropoff_datetime'] = pd.to_datetime(df['lpep_dropoff_datetime'])
    df['trip_duration'] = (df['lpep_dropoff_datetime'] - df['lpep_pickup_datetime']).dt.total_seconds() / 60
    df['weekday'] = df['lpep_pickup_datetime'].dt.day_name()
    df['hour'] = df['lpep_pickup_datetime'].dt.hour
    return df

df = load_data()

# Title
st.title("🚕 NYC Green Taxi Dashboard (June 2021)")

# Filters
st.markdown("### 🎛️ Filter Your Data")

col1, col2, col3 = st.columns(3)

with col1:
    selected_weekday = st.selectbox("Select Weekday", ['All'] + sorted(df['weekday'].unique()))
with col2:
    selected_payment = st.selectbox("Select Payment Type", ['All'] + sorted(df['payment_type'].dropna().unique()))
with col3:
    distance_range = st.slider("Trip Distance (miles)", 0.0, float(df['trip_distance'].max()), (0.0, 10.0))

# Apply filters
filtered_df = df.copy()
if selected_weekday != "All":
    filtered_df = filtered_df[filtered_df['weekday'] == selected_weekday]
if selected_payment != "All":
    filtered_df = filtered_df[filtered_df['payment_type'] == selected_payment]
filtered_df = filtered_df[(filtered_df['trip_distance'] >= distance_range[0]) & (filtered_df['trip_distance'] <= distance_range[1])]

st.markdown(f"##### Showing {len(filtered_df)} filtered trips")

# Row 1: Trip Duration + Payment Pie
st.subheader("📊 Trip Overview")

col4, col5 = st.columns(2)

with col4:
    fig1 = px.histogram(filtered_df, x="trip_duration", nbins=40,
                        title="Trip Duration Distribution (minutes)",
                        color_discrete_sequence=["#00cc96"])
    st.plotly_chart(fig1, use_container_width=True)

with col5:
    fig2 = px.pie(filtered_df, names='payment_type', title="Payment Type Share",
                  color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig2, use_container_width=True)

# Row 2: Total Amount by Weekday + Tip Amount by Payment
st.subheader("📅 Weekly & Tip Trends")

col6, col7 = st.columns(2)

with col6:
    weekday_avg = filtered_df.groupby('weekday')['total_amount'].mean().reindex([
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    fig3 = px.bar(weekday_avg, title="Average Total Amount by Weekday", labels={'value': 'Avg Total ($)', 'index': 'Weekday'})
    st.plotly_chart(fig3, use_container_width=True)

with col7:
    tip_avg = filtered_df.groupby('payment_type')['tip_amount'].mean().sort_values(ascending=False)
    fig4 = px.bar(tip_avg, title="Average Tip Amount by Payment Type", labels={'value': 'Avg Tip ($)', 'index': 'Payment Type'})
    st.plotly_chart(fig4, use_container_width=True)

# Row 3: Trips by Hour of Day
st.subheader("🕐 Trips by Hour of the Day")
hour_count = filtered_df['hour'].value_counts().sort_index()
fig5 = px.bar(hour_count, labels={'index': 'Hour of Day', 'value': 'Trip Count'}, title="Trip Count by Pickup Hour")
st.plotly_chart(fig5, use_container_width=True)

# Row 4: Correlation Heatmap
st.subheader("📉 Correlation Heatmap")

numeric_cols = ['trip_distance', 'extra', 'mta_tax', 'tip_amount', 'tolls_amount',
                'improvement_surcharge', 'congestion_surcharge', 'trip_duration', 'passenger_count', 'total_amount']

corr = filtered_df[numeric_cols].corr()

fig6, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
st.pyplot(fig6)

# Footer
st.markdown("---")

