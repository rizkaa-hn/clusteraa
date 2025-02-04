import streamlit as st
import pandas as pd
import requests
from streamlit_lottie import st_lottie
from core.crud import save_data_to_db, read_data_from_db, update_data_in_db, delete_data_from_db
from core.connection import connect_to_app_database

conn = connect_to_app_database()

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def data_page():
    col1, col2 = st.columns(2, gap="small", vertical_alignment="center")
    with col1:
        st.title("Manajemen Data", anchor=False)
        st.write("Yuk olah datamu bersama clustera.")
    with col2:
        lottie_coding = load_lottieurl("https://lottie.host/09eb92fb-c8bd-45ea-ac6f-83d9a1d8486c/jJx7P3BJTj.json")
        st_lottie(lottie_coding, height=200, key="data")

    uploaded_file = st.file_uploader("Upload datasetmu", type=['xlsx','csv'])
    if uploaded_file is not None:
        # Memeriksa ekstensi file
        if uploaded_file.name.endswith('.csv'):
            try:
                # Membaca file CSV
                data = pd.read_csv(uploaded_file)
                st.write("Data dari file CSV:")
            except Exception as e:
                st.error(f"Terjadi kesalahan saat membaca file CSV: {e} 😣")
        elif uploaded_file.name.endswith('.xlsx'):
            try: 
                # Membaca file Excel
                data = pd.read_excel(uploaded_file, engine='openpyxl')
                st.write("Data dari file Excel:")
            except Exception as e:
                st.error(f"Terjadi kesalahan saat membaca file excel: {e}😣")
        st.write("Dataset Asli:")
        st.write(data)

        # Statistik Deskriptif
        st.header("Statistik Deskriptif")
        st.write(data.describe())

        # Penanganan Missing Values
        st.header("Penanganan Missing Values")
        missing_info = data.isnull().sum()
        st.write("Jumlah missing values per kolom:")
        st.write(missing_info[missing_info > 0])

        if missing_info.sum() > 0:
            action = st.radio("Pilih aksi untuk missing values:", ["Hapus data", "Imputasi nilai"])
            if action == "Hapus data":
                option = st.radio("Hapus berdasarkan:", ["Baris", "Kolom"])
                if option == "Baris":
                    data = data.dropna()
                    st.success(f"Berhasil hapus Baris.")
                else:
                    data = data.dropna(axis=1)
                    st.success(f"Berhasil hapus Kolom.")
            else:
                column = st.selectbox("Pilih kolom untuk imputasi:", data.columns[data.isnull().sum() > 0])
                value = st.text_input(f"Masukkan nilai untuk kolom '{column}':")
                if value:
                    data[column] = data[column].fillna(value)
                    st.success(f"Berhasil melakukan imputasi nilai")

        # Simpan data ke database
        st.header("Simpan Data ke Database")
        dataset_name = st.text_input("Masukkan nama dataset:")
        if st.button("Simpan ke Database"):
            if dataset_name:
                # Menyimpan data ke database dengan user_id
                user_id = st.session_state.get('user_id')
                if user_id:
                    save_data_to_db(conn, dataset_name, data, user_id)
                    st.success(f"Dataset '{dataset_name}' berhasil disimpan ke database.")
                    st.success(f"silakan lanjutkan ke halaman Visualisasi Data di Menu 🏃🏼‍♂️‍➡️")
                else:
                    st.error("User ID tidak ditemukan. Pastikan Anda sudah login.")
            else:
                st.error("Nama dataset tidak boleh kosong.")
