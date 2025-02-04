import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from streamlit_lottie import st_lottie
from core.crud import save_data_to_db, read_data_from_db, update_data_in_db, save_eda_history
from core.connection import connect_to_app_database

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

conn = connect_to_app_database()


def eda_page():
    col1, col2 = st.columns(2, gap="small", vertical_alignment="center")
    with col1:
        st.title("Visualisasi Data", anchor=False)
        st.write("Exploratory Data Analysis (EDA)")
        st.write("\n")
    with col2:
        lottie_coding =load_lottieurl("https://lottie.host/f9e99217-a454-4c86-b898-f8f9ff4681ef/0CatOMVseF.json")
        st_lottie(lottie_coding, height=300, key="data")


    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("Anda harus login terlebih dahulu.")
        return

    dataset_list = read_data_from_db(conn, user_id)
    if dataset_list:
        st.write(f"Jumlah dataset: {len(dataset_list)}")
    else:
        st.warning("Tidak ada dataset di database.")

    user_datasets = dataset_list

    # Pilih dataset dari database
    dataset_name = st.selectbox("Pilih dataset:", [d["dataset_name"] for d in user_datasets])

    if dataset_name:
        selected_dataset = next(d for d in user_datasets if d["dataset_name"] == dataset_name)
        data = selected_dataset["data"]
        st.write("Dataset yang digunakan:")
        st.write(data)

        st.session_state['selected_dataset_name']=dataset_name

        # Statistik Deskriptif
        st.subheader("1. Statistik Deskriptif")
        st.write(data.describe())
        save_eda_history(conn, user_id=user_id, dataset_id=selected_dataset["dataset_id"], analysis_type="Statistik Deskriptif", analysis_result=data.describe().to_json())

        # Korelasi
        st.subheader("2. Korelasi")
        numeric_columns = data.select_dtypes(include=['int64', 'float64'])
        if numeric_columns.empty:
            st.warning("Tidak ada kolom numerik dalam dataset.")
            return
        corr_matrix = numeric_columns.corr()
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', linewidths=0.5)
        st.pyplot(plt)
        plt.clf()
        save_eda_history(conn, user_id=user_id, dataset_id=selected_dataset["dataset_id"], analysis_type="Korelasi", analysis_result=corr_matrix.to_json())

        # Distribusi Data
        st.subheader("3. Distribusi Data")
        selected_column = st.selectbox("Pilih kolom untuk distribusi:", numeric_columns.columns)
        plt.figure(figsize=(10, 6))
        sns.histplot(data[selected_column], kde=True, bins=30, color="blue")
        plt.title(f"Distribusi '{selected_column}' dengan KDE")
        plt.xlabel(selected_column)
        plt.ylabel("Frekuensi")
        st.pyplot(plt)
        plt.clf()

        # Deteksi dan Penanganan Outlier
        st.subheader("4. Deteksi dan Penanganan Outlier")
        # Pilihan untuk memproses satu kolom atau semua kolom
        process_all_columns = st.checkbox("Proses semua kolom numeric")

        if process_all_columns:
        # Iterasi untuk semua kolom numerik
            for column in numeric_columns.columns:
                Q1 = data[column].quantile(0.25)
                Q3 = data[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                outliers = data[(data[column] < lower_bound) | (data[column] > upper_bound)]
                st.write(f"Jumlah outlier di kolom '{column}': {len(outliers)}")

                # Visualisasi Outlier
                plt.figure(figsize=(8, 5))
                plt.boxplot(data[column].dropna(), vert=False, patch_artist=True)
                plt.title(f"Boxplot untuk Kolom '{column}'")
                plt.xlabel(column)
                st.pyplot(plt)

                # Pilihan Penanganan Outlier untuk semua kolom
                action = st.radio(f"Pilih aksi untuk outlier di kolom '{column}':", ["Tidak ada", "Ganti dengan batas bawah/atas"], key=column)
                if action == "Ganti dengan batas bawah/atas":
                    data[column] = data[column].apply(
                        lambda x: upper_bound if x > upper_bound else (lower_bound if x < lower_bound else x)
                    )
                    st.success(f"Outlier di kolom '{column}' berhasil diganti.")
                    st.write(data[column].describe())
        else:
            # Proses untuk satu kolom
            selected_column_outlier = st.selectbox("Pilih kolom untuk deteksi outlier:", numeric_columns.columns)
            Q1 = data[selected_column_outlier].quantile(0.25)
            Q3 = data[selected_column_outlier].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = data[(data[selected_column_outlier] < lower_bound) | (data[selected_column_outlier] > upper_bound)]
            st.write(f"Jumlah outlier di kolom '{selected_column_outlier}': {len(outliers)}")

            # Visualisasi Outlier
            plt.figure(figsize=(8, 5))
            plt.boxplot(data[selected_column_outlier].dropna(), vert=False, patch_artist=True)
            plt.title(f"Boxplot untuk Kolom '{selected_column_outlier}'")
            plt.xlabel(selected_column_outlier)
            st.pyplot(plt)

            # Pilihan Penanganan Outlier
            action = st.radio("Pilih aksi untuk outlier:", ["Tidak ada", "Ganti dengan batas bawah/atas"])
            if action == "Ganti dengan batas bawah/atas":
                data[selected_column_outlier] = data[selected_column_outlier].apply(
                    lambda x: upper_bound if x > upper_bound else (lower_bound if x < lower_bound else x)
                )
                st.success("Outlier berhasil diganti.")
                st.write(data[selected_column_outlier].describe())
        
        # Simpan dataset yang telah diperbaiki ke database
        if st.button("Simpan Hasil"):
            if not isinstance(data, pd.DataFrame):
                st.error("Data harus dalam format DataFrame.")
            else:
                st.session_state['eda_data'] = data
                st.success("Hasil EDA berhasil disimpan")
                st.success(f"silakan lanjutkan ke halaman Clustering Data di Menu 🏃🏼‍♂️‍➡️")
