import mysql.connector
import streamlit as st
import pandas as pd
import numpy as np 
from core.connection import connect_to_app_database
from datetime import datetime
from io import StringIO

# Fungsi untuk menyimpan data ke database
def save_data_to_db(conn, dataset_name, data, user_id):
    try:
        data_json = data.to_json(orient="records")
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO dataset (dataset_name, data, user_id) VALUES (%s, %s, %s)", 
                           (dataset_name, data_json, user_id))
            conn.commit()
    except mysql.connector.Error as e:
        print(f"Error saving data: {e}")
    
# Fungsi untuk membaca data dari database
def read_data_from_db(conn, user_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT dataset_id, dataset_name, data FROM dataset WHERE user_id = %s", (user_id,))
            rows = cursor.fetchall()
        datasets = []
        for row in rows:
            try:
                dataset = {
                    "dataset_id": row[0],
                    "dataset_name": row[1],
                    "data": pd.read_json(StringIO(row[2])) if row[2] else pd.DataFrame(),
                }
                datasets.append(dataset)
            except ValueError as ve:
                print(f"Error parsing data: {row[2]}, {ve}")
        return datasets
    except mysql.connector.Error as e:
        st.error(f"Error membaca data dari database: {e}")
        return None


# Fungsi untuk memperbarui data di database
def update_data_in_db(conn, dataset_id, dataset_name, data, user_id):
    try:
        if data is None:
            st.error("Data tidak boleh kosong.")
            return
        
        if isinstance(data, str):
            try:
                data = pd.read_json(StringIO(data))
            except ValueError as e:
                st.error(f"String bukan JSON valid: {e}")
                return
        
        if isinstance(data, pd.DataFrame):
            data_json = data.to_json(orient="records")
        else:
            st.error("Data harus berupa DataFrame atau string JSON valid.")
            return
        
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE dataset
                SET dataset_name = %s, data = %s
                WHERE dataset_id = %s AND user_id = %s
            """, (dataset_name, data_json, dataset_id, user_id))
            conn.commit()
        st.success("Updated")
    except mysql.connector.Error as e:
        st.error(f"Error update: {e}")

# Fungsi untuk menghapus data dari database
def delete_data_from_db(conn, dataset_id, user_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM dataset WHERE dataset_id = %s AND user_id = %s", (dataset_id, user_id))
            conn.commit()
        st.success("Deleted")
    except mysql.connector.Error as e:
        print(f"Error deleting data: {e}")

# Fungsi menyimpan riwayat EDA
def save_eda_history(conn, dataset_id, analysis_type, analysis_result, user_id):
    try:
        query = """
        INSERT INTO eda_history (dataset_id, analysis_type, analysis_result, user_id)
        VALUES (%s, %s, %s, %s)
        """
        with conn.cursor() as cursor:
            cursor.execute(query, (dataset_id, analysis_type, analysis_result, user_id))
            conn.commit()
        st.success("Riwayat EDA berhasil disimpan.")
    except mysql.connector.Error as e:
        st.error(f"Gagal menyimpan riwayat EDA: {e}")

# Fungsi membaca riwayat EDA
def read_eda_history(conn, dataset_id, user_id):
    try:
        query = "SELECT * FROM eda_history WHERE dataset_id = %s AND user_id = %s"
        return pd.read_sql(query, conn, params=[dataset_id, user_id])
    except mysql.connector.Error as e:
        st.error(f"Gagal membaca riwayat EDA: {e}")
        return None

# Fungsi menyimpan riwayat clustering
def save_clustering_history(conn, dataset_id, method, k, dbi, clustering_result, user_id):
    try:
        dataset_id = int(dataset_id) if isinstance(dataset_id, (np.integer, np.int64)) else dataset_id
        k = int(k) if isinstance(k, (np.integer, np.int64)) else k
        query = """
        INSERT INTO clustering_history (dataset_id, method, k, dbi, clustering_result, created_at, user_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        with conn.cursor() as cursor:
            cursor.execute(query, (dataset_id, method, k, dbi, clustering_result, datetime.now(), user_id))
            conn.commit()
        print("Riwayat clusterisasi berhasil disimpan.")
    except mysql.connector.Error as e:
        print(f"Error saat menyimpan riwayat clusterisasi: {e}")

# Fungsi membaca riwayat clustering
def read_clustering_history(conn, user_id):
    query = """
    SELECT history_id, dataset_id, method, k, dbi, clustering_result, created_at
    FROM clustering_history
    WHERE user_id = %s
    ORDER BY created_at DESC
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        return [
            {
                "history_id": row[0],
                "dataset_id": row[1],
                "method": row[2],
                "k": row[3],
                "dbi": row[4],
                "clustering_result": row[5],
                "created_at": row[6],
            }
            for row in rows
        ]

# Fungsi untuk membaca semua dataset dari database
def read_dataset(conn):
    try:
        query = "SELECT dataset_id, dataset_name, data FROM dataset"
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
        return [{"dataset_id": row[0], "dataset_name": row[1], "data": pd.read_json(StringIO(row[2]))} for row in rows]
    except mysql.connector.Error as e:
        print(f"Error membaca dataset: {e}")
        return []