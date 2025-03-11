import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from gdelt import gdelt

# Initialize GDELT connection
gdelt_conn = gdelt.gdelt()

# --- Sidebar Filters ---
st.sidebar.header("Filters")

# Time Span Filter
time_span_options = ["Last Month", "Last 3 Months", "Last 6 Months", "Custom Date Range"]
selected_time_span = st.sidebar.selectbox("Time Span", time_span_options, index=1)  # Default to Last 3 Months

start_date = None
end_date = datetime.now()

if selected_time_span == "Last Month":
    start_date = end_date - timedelta(days=30)
elif selected_time_span == "Last 3 Months":
    start_date = end_date - timedelta(days=90)
elif selected_time_span == "Last 6 Months":
    start_date = end_date - timedelta(days=180)
elif selected_time_span == "Custom Date Range":
    start_date_input = st.sidebar.date_input("Start Date", end_date - timedelta(days=90))
    end_date_input = st.sidebar.date_input("End Date", end_date)
    start_date = datetime.combine(start_date_input, datetime.min.time())
    end_date = datetime.combine(end_date_input, datetime.max.time())

if start_date:
    start_date_str = start_date.strftime('%Y%m%d')
    end_date_str = end_date.strftime('%Y%m%d')
else:
    start_date_str = (end_date - timedelta(days=90)).strftime('%Y%m%d') # Default to last 3 months if custom range is not fully set
    end_date_str = end_date.strftime('%Y%m%d')


# Region Filter (Country)
region_options = ["United Kingdom", "England", "Scotland", "Wales", "Northern Ireland"] # Example regions
selected_region = st.sidebar.selectbox("Region", region_options, index=0) # Default to UK
country_code = "UK" # Default country code

if selected_region == "England":
    region_filter = "Region:England" # Example - GDELT region filtering might need more specific codes
elif selected_region == "Scotland":
    region_filter = "Region:Scotland"
elif selected_region == "Wales":
    region_filter = "Region:Wales"
elif selected_region == "Northern Ireland":
    region_filter = "Region:Northern Ireland"
else:
    region_filter = "Country:UK" # Default to country-level filtering


# Event Type Filter (using CAMEO codes - simplified examples)
event_type_options = ["All Events", "Protests", "Violence", "Diplomacy", "Public Statements"]
selected_event_type = st.sidebar.selectbox("Event Type", event_type_options, index=0)

event_filter = None
if selected_event_type == "Protests":
    event_filter = "EventCode:17*"  # CAMEO codes starting with 17 are protests
elif selected_event_type == "Violence":
    event_filter = "EventCode:18*,19*,20*" # Violence related codes (example - refine based on CAMEO)
elif selected_event_type == "Diplomacy":
    event_filter = "EventCode:01*,02*,03*,04*" # Diplomacy related codes (example)
elif selected_event_type == "Public Statements":
    event_filter = "EventCode:05*,06*" # Public statement codes (example)


# --- Main Panel ---
st.title("UK Historical Events Dashboard (GDELT)")
st.write(f"Displaying events for **{selected_region}** from **{start_date_str}** to **{end_date_str}**")

query_params = [f"DATE>{start_date_str}", f"DATE<{end_date_str}", "COUNTRY:UK"] # Base query for UK and date range

if region_filter and selected_region != "United Kingdom": # Apply region filter if not UK-wide
    query_params.append(region_filter)

if event_filter and selected_event_type != "All Events":
    query_params.append(event_filter)

query_string = " ".join(query_params)

st.info(f"GDELT Query: `{query_string}`") # Display the constructed query for transparency

try:
    st.write("Fetching data from GDELT...")
    uk_events = gdelt_conn.Search(query_string)

    if uk_events.empty:
        st.warning("No events found matching the selected criteria.")
    else:
        st.success(f"Found {len(uk_events)} events.")

        # Select and rename columns for better readability
        display_columns = ['SQLDATE', 'Actor1Name', 'Actor2Name', 'EventCode', 'EventRootCode', 'GoldsteinScale', 'NumMentions', 'AvgTone', 'SOURCEURL']
        uk_events_display = uk_events[display_columns].rename(columns={
            'SQLDATE': 'Event Date',
            'Actor1Name': 'Actor 1',
            'Actor2Name': 'Actor 2',
            'EventCode': 'Event Code',
            'EventRootCode': 'Event Root Code',
            'GoldsteinScale': 'Goldstein Scale',
            'NumMentions': 'Mentions',
            'AvgTone': 'Avg Tone',
            'SOURCEURL': 'Source URL'
        })

        st.dataframe(uk_events_display)

        # --- Optional: Add some basic insights ---
        st.subheader("Event Code Distribution")
        event_code_counts = uk_events_display['Event Root Code'].value_counts()
        st.bar_chart(event_code_counts)


except Exception as e:
    st.error(f"Error fetching data from GDELT: {e}")
    st.error("Please ensure you have internet connectivity and the GDELT library is correctly installed.")
