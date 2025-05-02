# Import libraries
import pandas as pd
import mysql.connector
import streamlit as slt
from streamlit_option_menu import option_menu
import plotly.express as px
import re
# List of states and their CSVs
states_csv = {
    "Andhra_Pradesh": "ap_bus_details.csv",
    "Bihar": "bihar_bus_details.csv",
    "Chandigarh": "chandigarh_bus_details.csv",
    "Himachal": "himachal_bus_details.csv",
    "Kadamba": "kadamba_bus_details.csv",
    "Kerala": "kerala_bus_details.csv",
    "North_Bengal": "Northbengal_bus_details.csv",
    "Punjab": "Punjab_bus_details.csv",
    "Telangana": "telangana_bus_details.csv",
    "Uttar_Pradesh": "up_bus_details.csv"
}

# Loading all CSVs dynamically
route_map = {}

for state, file in states_csv.items():
    df = pd.read_csv(file)

    # --- Clean Bus_Type here ---
    def clean_bus_type(bus_type):
        if pd.isnull(bus_type):
            return ""
        bus_type = bus_type.lower()
        bus_type = re.sub(r'[\(\)\-\,\+]', ' ', bus_type)   # remove unwanted symbols
        bus_type = re.sub(r'\s+', ' ', bus_type)            # collapse multiple spaces
        return bus_type.strip()

    df["Bus_Type"] = df["Bus_Type"].apply(clean_bus_type)
    # ----------------------------

    routes = list(set(df["Route_Name"]))
    route_map[state] = routes


# Setting up Streamlit page
slt.set_page_config(page_title="OnlineBus Dashboard", layout="wide")

# Streamlit Option Menu
web = option_menu(
    menu_title="OnlineBus",
    options=["Home", "States and Routes"],
    icons=["house", "bus-front-fill"],
    orientation="horizontal"
)

# Home page settings
if web == "Home":
    slt.title("Redbus Data Scraping with Selenium &Dynamic Filtering using Streamlit")
    slt.subheader(":blue[Domain:] Transportation")
    slt.subheader(":blue[Ojective:]")
    slt.markdown("The project aims to streamline bus data analysis by automating Redbus data extraction and enabling real-time filtering via a Streamlit dashboard backed by a MySQL database.")
    slt.subheader(":blue[Overview:]")
    slt.markdown("Selenium: Selenium is a tool used for automating web browsers. It is commonly used for web scraping, which involves extracting data from websites.")
    slt.markdown("Pandas:It is a powerful Python library used to load, transform, and preprocess CSV data into structured DataFrames for efficient analysis and manipulation.")
    slt.markdown("MySQL:  Used to store the transformed data in structured tables, enabling efficient insertion, storage, and retrieval through SQL queries.")
    slt.markdown("Streamlit: Used to build an interactive web app for real-time data filtering and visualization with a simple, Python-based UI framework.")
    slt.subheader(":blue[Skill-take:]")
    slt.markdown("Selenium,Pyhton,Pnadas,MySQL,mysql-connector-python,streamlit.")
    slt.subheader(":blue[Developed-by:] Mugil ")

# Function to fetch and display data
def fetch_and_display_data(route_name, min_price, max_price, bus_type, min_rating, departure_time_period, min_seats):
    with mysql.connector.connect(host="localhost", user="root", password="root", database="red_bus_details") as conn:
        my_cursor = conn.cursor()

        # Lowercase and normalize bus type input
        bus_type = bus_type.strip().lower()

        # Base SQL Query
        query = '''
            SELECT DISTINCT * FROM bus_details 
            WHERE Price BETWEEN %s AND %s 
            AND Route_Name = %s
            AND Star_Rating >= %s
            AND Seat_Availability >= %s
        '''
        params = [min_price, max_price, route_name, min_rating, min_seats]

        # Apply Bus Type Filter (case insensitive)
        if bus_type != "all":
            if "non ac" in bus_type:
                if "sleeper" in bus_type:
                    query += " AND LOWER(Bus_Type) LIKE %s AND LOWER(Bus_Type) LIKE %s"
                    params.append("%non%")
                    params.append("%sleeper%")
                elif "seater" in bus_type:
                    query += " AND LOWER(Bus_Type) LIKE %s AND LOWER(Bus_Type) LIKE %s"
                    params.append("%non%")
                    params.append("%seater%")
            elif "ac" in bus_type:
                if "sleeper" in bus_type:
                    query += " AND LOWER(Bus_Type) LIKE %s AND LOWER(Bus_Type) LIKE %s AND LOWER(Bus_Type) NOT LIKE %s"
                    params.append("%ac%")
                    params.append("%sleeper%")
                    params.append("%non%")
                elif "seater" in bus_type:
                    query += " AND LOWER(Bus_Type) LIKE %s AND LOWER(Bus_Type) LIKE %s AND LOWER(Bus_Type) NOT LIKE %s"
                    params.append("%ac%")
                    params.append("%seater%")
                    params.append("%non%")
            else:
                query += " AND LOWER(Bus_Type) LIKE %s"
                params.append(f"%{bus_type}%")


        # Execute query
        my_cursor.execute(query, tuple(params))
        out = my_cursor.fetchall()

    # Create DataFrame
    df = pd.DataFrame(out, columns=[
        'Route_Name', 'Route_Link', 'Bus_Name', 'Bus_Type', 'Departing_Time',
        'Duration', 'Reaching_Time', 'Star_Rating', 'Price', 'Seat_Availability'
    ])

    # Departure Time Filter
    if not df.empty and departure_time_period != "All":
        def categorize_departure(time_str):
            try:
                hour = int(time_str.split(":")[0])
                if 0 <= hour < 12:
                    return "Morning"
                elif 12 <= hour < 18:
                    return "Afternoon"
                else:
                    return "Evening/Night"
            except:
                return "Unknown"

        df["Time_Category"] = df["Departing_Time"].apply(categorize_departure)
        df = df[df["Time_Category"] == departure_time_period]

    # Display
    if df.empty:
        slt.info("No buses found for the selected criteria. Try changing filters! 🚍")
    else:
        col1, col2 = slt.columns(2)
        col1.metric("Total Buses Found", len(df))
        col2.metric("Average Fare", f"₹{df['Price'].mean():.2f}")

        slt.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False)
        slt.download_button(
            label="Download Filtered Data as CSV",
            data=csv,
            file_name="filtered_bus_data.csv",
            mime="text/csv"
        )

# States and Routes page settings
if web == "States and Routes":
    slt.title("Bus Selection by State, Route, and Advanced Filters")

    # State and Route Selection
    S = slt.selectbox("Select a State", list(route_map.keys()))
    route_selected = slt.selectbox("Select a Route", route_map[S])

    # Bus Fare Range
    min_price, max_price = slt.slider(
        "Select Bus Fare Range (₹)",
        min_value=0,
        max_value=5000,
        value=(100, 2000),
        step=50
    )

    # Bus Type Options
    bus_type_options = {
    "All": "all",
    "AC Seater": "ac seater",
    "AC Sleeper": "ac sleeper",
    "Non AC Seater": "non ac seater",
    "Non AC Sleeper": "non ac sleeper",
    "AC Seater/Sleeper": "seater sleeper",
    "Semi Sleeper": "semi sleeper",
    "Volvo": "volvo",
    "Volvo Sleeper": "volvo sleeper",
    "Mercedes Benz": "mercedes",
    "Electric": "electric",
    "Bharat Benz": "bharat benz"
}

    bus_type_display = slt.selectbox("Select Bus Type", list(bus_type_options.keys()))
    bus_type = bus_type_options[bus_type_display]

    # Star Rating filter
    min_rating = slt.slider("Select Minimum Star Rating", 1.0, 5.0, 3.0, step=0.5)

    # Departure Time Period filter
    departure_time_period = slt.selectbox("Departure Time Period", ["All", "Morning", "Afternoon", "Evening/Night"])

    # Seat Availability filter
    min_seats = slt.slider("Minimum Seat Availability", 0, 50, 1)

    # Display Selected Filters Summary
    with slt.expander("See Your Selected Filters"):
        slt.write(f"State: {S}")
        slt.write(f"Route: {route_selected}")
        slt.write(f"Fare: ₹{min_price} to ₹{max_price}")
        slt.write(f"Bus Type: {bus_type_display}")
        slt.write(f"Minimum Rating: {min_rating}⭐")
        slt.write(f"Departure Time: {departure_time_period}")
        slt.write(f"Minimum Seats Available: {min_seats}")

    # Fetch and Display Data
    with slt.spinner("Fetching matching buses... Please wait 🚍"):
        fetch_and_display_data(route_selected, min_price, max_price, bus_type, min_rating, departure_time_period, min_seats)