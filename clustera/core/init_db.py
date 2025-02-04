import mysql.connector
import streamlit as st
from core.connection import connect_to_app_database

def create_user_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                password VARCHAR(255) NOT NULL
            )
            """
        )
        conn.commit()
        print("Table 'user' created or already exists.")
    except mysql.connector.Error as e:
        print(f"Error creating 'user' table: {e}")

def create_data_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS dataset (
                dataset_id INT AUTO_INCREMENT PRIMARY KEY,
                dataset_name VARCHAR(100) NOT NULL,
                data LONGTEXT NOT NULL,
                user_id INT,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
            """
        )
        conn.commit()
        print("Table 'dataset' created or already exists.")
    except mysql.connector.Error as e:
        print(f"Error creating 'dataset' table: {e}")

def create_eda_history(conn):
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS eda_history (
                eda_id INT AUTO_INCREMENT PRIMARY KEY,
                dataset_id INT NOT NULL,
                analysis_type VARCHAR(255) NOT NULL,
                analysis_result TEXT NOT NULL,
                user_id INT NOT NULL,
                FOREIGN KEY (dataset_id) REFERENCES dataset(dataset_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
            """
        )
        conn.commit()
    except mysql.connector.Error as e:
        print(f"Error creating 'dataset' table: {e}")

def create_clustering_history_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS clustering_history (
                history_id INT AUTO_INCREMENT PRIMARY KEY,
                dataset_id INT NOT NULL,
                method VARCHAR(255) NOT NULL,
                k INT NOT NULL,
                dbi FLOAT NOT NULL,
                clustering_result LONGTEXT NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                user_id INT NOT NULL,
                FOREIGN KEY (dataset_id) REFERENCES dataset(dataset_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
            """
        )
        conn.commit()
        print("Table 'clustering_history' created or already exists.")
    except mysql.connector.Error as e:
        print(f"Error creating 'clustering_history' table: {e}")

