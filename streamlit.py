# IMPORTING Libraries
import pandas as pd 
import mysql.connector
import streamlit as slt 
from streamlit_option_menu import option_menu
import plotly.express as px

#andhra
df_ap=pd.read_csv("ap_bus_details.csv")
list_ap=(set(df_ap["Route_Name"]))

#bihar
df_bh=pd.read_csv("bihar_bus_details.csv")
list_bh=(set(df_bh["Route_Name"]))

#chandigarh
df_ch=pd.read_csv("chandigarh_bus_details.csv")
list_ch=(set(df_ch["Route_Name"]))

#himachal
df_hl=pd.read_csv("himachal_bus_details.csv")
list_hl=list(set(df_hl["Route_Name"]))

#kadamba
df_kb=pd.read_csv("kadamba_bus_details.csv")
list_kb=list(set(df_kb["Route_Name"]))

#kerala
df_kl = pd.read_csv("kerala_bus_details.csv")
# Get unique route names using set()
list_kl = list(set(df_kl["Route_Name"]))

#northbengal
df_nb=pd.read_csv("Northbengal_bus_details.csv")
list_nb=(set(df_nb["Route_Name"]))

#punjab
df_pb=pd.read_csv("Punjab_bus_details.csv")
list_pb=(set(df_pb["Route_Name"]))

#telangana
df_ta=pd.read_csv("telangana_bus_details.csv")
list_ta=(set(df_ta["Route_Name"]))

#uttarpradesh
df_up=pd.read_csv("up_bus_details.csv")
list_up=(set(df_up["Route_Name"]))


#setting up streamlit page 
slt.set_page_config(layout="wide")

web=option_menu(menu_title="OnlineBus",
                options=["Home","States and Routes"],
                icons=["house","info-circle"],
                orientation="horizontal"
                )
#home page settings 
if web=="Home":
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



def fetch_and_display_data(route_name, price_range):
    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="red_bus_details")
    my_cursor = conn.cursor()
    
    if price_range == "50-1000":
        query = f'''
            SELECT DISTINCT * FROM bus_details 
            WHERE Price BETWEEN 50 AND 1000 AND Route_name = %s 
            ORDER BY Price DESC
        '''
        my_cursor.execute(query, (route_name,))
    elif price_range == "1000-2000":
        query = f'''
            SELECT DISTINCT * FROM bus_details 
            WHERE Price BETWEEN 1000 AND 2000 AND Route_name = %s 
            ORDER BY Price DESC
        '''
        my_cursor.execute(query, (route_name,))
    elif price_range == "2000 and above":
        query = f'''
            SELECT DISTINCT * FROM bus_details 
            WHERE Price > 2000 AND Route_name = %s 
            ORDER BY Price DESC
        '''
        my_cursor.execute(query, (route_name,))
    else:
        slt.warning("Invalid fare range selected.")
        return

    out = my_cursor.fetchall()
    df = pd.DataFrame(out, columns=['Route_Name', 'Route_Link', 'Bus_Name', 'Bus_Type', 'Departing_Time',
                                    'Duration', 'Reaching_Time', 'Star_Rating', 'Price', 'Seat_Availability'])
    if df.empty:
        slt.info("No buses found for the selected criteria.")
    else:
        slt.write(df)


route_map = {
    "Andhra_Pradesh": list_ap,
    "Bihar": list_bh,
    "Chandigarh": list_ch,
    "Kadamba": list_kb,
    "Kerala": list_kl,
    "Punjab": list_pb,
    "Uttar_Pradesh": list_up,
    "Himachal": list_hl,
    "North_Bengal": list_nb,
    "Telangana": list_ta,
}

# states and routes page setting
if web=="States and Routes":    
    S = slt.selectbox("List of States", list(route_map.keys()))
    route_selected = slt.selectbox("Select a route", route_map[S])
    fare_range = slt.radio("Choose bus fare range", ("50-1000", "1000-2000", "2000 and above"))

    fetch_and_display_data(route_selected, fare_range)
