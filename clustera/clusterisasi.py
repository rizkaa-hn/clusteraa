import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
from kneed import KneeLocator
from sklearn.metrics import davies_bouldin_score
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from streamlit_lottie import st_lottie
from core.connection import connect_to_app_database
from core.crud import save_clustering_history, read_data_from_db

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

conn = connect_to_app_database()

def clusterisasi_page():
    # Inisialisasi session_state jika belum ada
    if 'k' not in st.session_state:
        st.session_state.k = None  # Inisialisasi k
    if 'dbi_score' not in st.session_state:
        st.session_state.dbi_score = None  # Inisialisasi dbi_score
    if 'clustered_data' not in st.session_state:
        st.session_state.clustered_data = None  # Inisialisasi clustered_data
    if 'is_saved' not in st.session_state:
        st.session_state.is_saved = False 

    col1, col2 = st.columns(2, gap="small", vertical_alignment="center")
    with col1:
        st.title("K-Means++ Clustering", anchor=False)
        st.write("\n")
    with col2:
        lottie_coding = load_lottieurl("https://lottie.host/2916f013-90ff-457f-9fa2-62c92f1a99eb/2cFfJJgiYL.json")
        st_lottie(lottie_coding, height=200, key="data")

    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("Anda harus login terlebih dahulu.")
        return

    if 'eda_data' in st.session_state:
        data = st.session_state['eda_data']
        st.write("Dataset yang digunakan:")
        st.write(data)
        st.write(data.describe())

        # Menentukan Jumlah Cluster (K)
        st.subheader("1. Menentukan Jumlah Cluster (K)")
        method = st.radio("Pilih metode:", ["Manual", "Metode Elbow"])

        if method == "Manual":
            st.session_state.k = st.number_input("Masukkan jumlah cluster (K):", min_value=2, max_value=10, step=1)
            if st.button("Proses Clustering", key="manual_clustering"):
                # Memastikan hanya kolom numerik yang digunakan
                numeric_data = data.select_dtypes(include=['float64', 'int64'])
                if numeric_data.empty:
                    st.error("Data tidak memiliki kolom numerik untuk clustering.")
                else:
                    kmeans = KMeans(n_clusters=st.session_state.k, init="k-means++", random_state=0, n_init=10)
                    data['Cluster'] = kmeans.fit_predict(numeric_data)

                    # Pastikan kolom 'Cluster' ada setelah clustering
                    if 'Cluster' in data.columns:
                        st.session_state.dbi_score = davies_bouldin_score(numeric_data, data['Cluster'])
                        st.session_state.clustered_data = data  # Simpan data yang sudah di-cluster

                        # Menampilkan hasil clustering
                        cluster_counts = data['Cluster'].value_counts().sort_index()
                    else:
                        st.error("Kolom 'Cluster' tidak ditemukan dalam data setelah clustering.")
                
        elif method == "Metode Elbow":
            if st.button("Tampilkan Plot Elbow", key="elbow_plot"):
                distortions = []
                K_range = range(1, 11)
                for k in K_range:
                    kmeans = KMeans(n_clusters=k, init="k-means++", random_state=0, n_init=10)
                    kmeans.fit(data.select_dtypes(include=['float64', 'int64']))
                    distortions.append(kmeans.inertia_)

                # Menentukan jumlah cluster optimal menggunakan KneeLocator
                kl = KneeLocator(K_range, distortions, curve="convex", direction="decreasing")
                st.session_state.k = kl.knee  # Menyimpan k yang ditemukan oleh Elbow

                # Menampilkan grafik Elbow
                plt.figure(figsize=(8, 5))
                plt.plot(K_range, distortions, 'bx-')
                plt.axvline(st.session_state.k, color='r', linestyle='--', label=f"Optimal K = {st.session_state.k}")
                plt.title("Metode Elbow untuk Menentukan Nilai K")
                plt.xlabel("Jumlah Cluster (K)")
                plt.ylabel("Distortion")
                plt.legend()
                st.pyplot(plt)

                st.write(f"Jumlah cluster optimal berdasarkan metode Elbow adalah **{st.session_state.k}**.")

            if st.session_state.k is not None:
                if st.button("Proses Clustering dengan Optimal K", key="optimal_clustering"):
                    kmeans = KMeans(n_clusters=st.session_state.k, init="k-means++", random_state=0, n_init=10)
                    numeric_data = data.select_dtypes(include=['float64', 'int64'])
                    if numeric_data.empty:
                        st.error("Data tidak memiliki kolom numerik untuk clustering.")
                    else:
                        data['Cluster'] = kmeans.fit_predict(numeric_data)
                        st.session_state.dbi_score = davies_bouldin_score(numeric_data, data['Cluster'])
                        st.session_state.clustered_data = data  # Simpan data yang sudah di-cluster

                        # Pastikan kolom 'Cluster' ada setelah clustering
                        if 'Cluster' in data.columns:
                            cluster_counts = data['Cluster'].value_counts().sort_index()
                        else:
                            st.error("Kolom 'Cluster' tidak ditemukan dalam data setelah clustering.")

        # Menampilkan Hasil Clustering jika sudah dilakukan
        if st.session_state.k is not None and st.session_state.dbi_score is not None:
            clustered_data = st.session_state.clustered_data

            # Debugging: Cek apakah kolom 'Cluster' ada di DataFrame
            if 'Cluster' not in clustered_data.columns:
                st.error("Kolom 'Cluster' tidak ditemukan dalam data setelah clustering.")
            else:
                # Hasil Clustering
                st.subheader("2. Hasil Clustering")
                cluster_counts = clustered_data['Cluster'].value_counts().sort_index()
                st.write("Jumlah data per cluster:")
                st.bar_chart(cluster_counts)

                # Tabel Data per Cluster
                selected_cluster = st.selectbox("Pilih cluster untuk melihat datanya:", sorted(clustered_data['Cluster'].unique()))
                st.write(f"Data untuk Cluster {selected_cluster}:")
                st.write(clustered_data[clustered_data['Cluster'] == selected_cluster])

                # Visualisasi Pairplot
                st.subheader("3. Visualisasi Pairplot")
                fig = sns.pairplot(clustered_data[data.select_dtypes(include=['float64', 'int64']).columns.tolist() + ['Cluster']], hue="Cluster", palette="Set2", diag_kind="kde")
                st.pyplot(fig)

                # Evaluasi Clustering
                st.subheader("4. Evaluasi Clustering")
                st.write(f"Davies-Bouldin Index (DBI): **{st.session_state.dbi_score:.4f}**")

                # Simpan Dataset dengan Cluster
                st.subheader("5. Unduh Data dengan Cluster")
                if st.button("Unduh Data Clustered", key="download_clustered_data"):
                    csv = clustered_data.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Unduh data sebagai CSV",
                        data=csv,
                        file_name="data_clustered.csv",
                        mime="text/csv"
                    )
        
        # Simpan hasil clusterisasi ke database di bagian bawah
        if st.session_state.k is not None and st.session_state.dbi_score is not None:
            st.subheader("6. Simpan Hasil Clusterisasi ke Database")
            if st.button("Simpan Hasil Clusterisasi", key="save_clustering_result"):
                datasets = read_data_from_db(conn, user_id)

                if isinstance(datasets, list):
                    datasets_df = pd.DataFrame([{
                        'dataset_id': dataset['dataset_id'],
                        'dataset_name': dataset['dataset_name']
                    } for dataset in datasets])
                    
                    datasets_df['dataset_name'] = datasets_df['dataset_name'].astype(str)
                else:
                    st.error("Tidak ada dataset")
                    return
                
                eda_data = st.session_state.get('eda_data')
                if not isinstance(eda_data, pd.DataFrame):
                    st.error("Nilai eda_Data harus berupa DataFrame")
                    return
                
                eda_dataset_name = st.session_state.get('selected_dataset_name', "Unknown")
                if eda_dataset_name not in datasets_df['dataset_name'].values:
                    st.error(f"Dataset dengan nama '{eda_dataset_name}' tidak ditemukan.")
                    return
                
                dataset_id = datasets_df.loc[datasets_df['dataset_name'] == eda_dataset_name, 'dataset_id'].values
                if len(dataset_id) == 0:
                    st.error("Dataset ID tidak ditemukan.")
                    return
                dataset_id = dataset_id[0] 
                
                for col in datasets_df.select_dtypes(include=['object']).columns:
                    datasets_df[col] = datasets_df[col].astype(str)

                datasets_df.fillna('', inplace=True)

                for col in datasets_df.columns:
                    try:
                        datasets_df[col].to_numpy()
                    except Exception as e:
                        st.error(f"Kolom '{col} bermasalah: {e}")
                        return
                
                    
                try:
                    save_clustering_history(
                        conn, 
                        user_id = user_id,
                        dataset_id=int(dataset_id),
                        method="Metode Elbow" if method == "Metode Elbow" else "Manual",
                        k=int(st.session_state.k),
                        dbi=float(st.session_state.dbi_score),
                        clustering_result=clustered_data.to_json(orient="records")  
                    )
                    st.session_state.is_saved = True  
                    st.success("Hasil clusterisasi berhasil disimpan ke database.")
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat menyimpan hasil clusterisasi: {e}")
    else:
        if not st.session_state.is_saved:
            st.error("Silakan lakukan Visualisasi Data (EDA) pada halaman 'Visualisasi Data' terlebih dahulu.")
