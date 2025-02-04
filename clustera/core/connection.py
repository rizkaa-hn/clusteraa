import mysql.connector
import streamlit as st

def connect_to_app_database():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",  
            password="Rizsql##2212",
            database="clustera"
        )
        print("Connected to the database successfully.")
        return conn
    except mysql.connector.Error as e:
        st.error(f"Error connecting to application database: {e}")
        return None
