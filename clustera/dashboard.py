import streamlit as st 
import requests
from streamlit_lottie import st_lottie
from core.connection import connect_to_app_database
from core.crud import read_clustering_history
import pandas as pd
from io import StringIO

conn = connect_to_app_database()

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def dashboard_page():
    if 'username' in st.session_state and 'user_id' in st.session_state:
        username = st.session_state['username']
        user_id = st.session_state['user_id']
        st.subheader(f"Halo lagi, {username}🕵🏼‍♂️👋🏼")
        col1, col2 = st.columns(2, gap="small", vertical_alignment="center")
        with col1:
            st.title("Dashboard")
            st.write("\n")
            st.write("\n")
            st.write("\n")
        with col2:
            lottie_coding =load_lottieurl("https://lottie.host/531e7373-e467-40a4-bce7-6b58410deddb/NU9MXAAInQ.json")
            st_lottie(lottie_coding, height=300, key="data")



    # Membaca riwayat clusterisasi dari database
    try:
        clustering_history = read_clustering_history(conn, user_id)
    except Exception as e:
        st.error(f"Gagal membaca riwayat clusterisasi: {e}")
        st.stop()

    # Periksa apakah ada data riwayat
    if not clustering_history:
        st.warning("Belum ada riwayat clusterisasi yang tersedia.")
    else:
        # Konversi riwayat clusterisasi ke DataFrame
        df_history = pd.DataFrame(clustering_history)

        # Tampilkan tabel riwayat clusterisasi
        st.subheader("Riwayat Clusterisasi")
        st.write("Berikut adalah riwayat clusterisasi yang pernah dilakukan:")
        st.dataframe(df_history[['history_id', 'dataset_id', 'method', 'k', 'dbi', 'created_at']])

        # Pilih riwayat untuk melihat detail
        selected_id = st.selectbox("Pilih ID riwayat untuk melihat detail:", df_history['history_id'])

        if selected_id:
            # Ambil data riwayat yang dipilih
            selected_history = df_history[df_history['history_id'] == selected_id].iloc[0]

            st.subheader("Detail Riwayat Clusterisasi")
            st.write(f"**Dataset:** {selected_history['dataset_id']}")
            st.write(f"**Metode:** {selected_history['method']}")
            st.write(f"**Jumlah Cluster (K):** {selected_history['k']}")
            st.write(f"**Davies-Bouldin Index (DBI):** {selected_history['dbi']:.4f}")
            st.write(f"**Waktu Clusterisasi:** {selected_history['created_at']}")

            try:
                clustering_result = pd.read_json(StringIO(selected_history['clustering_result']), orient="records")
                if 'Cluster' in clustering_result.columns:
                    st.subheader("Hasil Clusterisasi")
                    st.write(clustering_result)

                    csv = clustering_result.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Unduh hasil clusterisasi sebagai CSV",
                        data=csv,
                        file_name=f"clustering_result_{selected_id}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("Hasil clusterisasi tidak memiliki kolom 'Cluster'.")
            except ValueError as e:
                st.error(f"Gagal membaca hasil clusterisasi: {e}")