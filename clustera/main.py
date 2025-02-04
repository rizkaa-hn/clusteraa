import streamlit as st
from time import sleep
from streamlit_option_menu import option_menu
from core.connection import connect_to_app_database
from core.init_db import create_data_table, create_eda_history, create_user_table, create_clustering_history_table
from core.auth import authenticate, register_user
from core.crud import save_data_to_db
from login import login_or_register  # Gabungan login dan registrasi

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="clustera.",
    page_icon="logo.png"
)

# Periksa apakah pengguna sudah login
if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
    # Tampilkan halaman login/registrasi sebagai default
    login_or_register()
else:
    # Jika sudah login, tampilkan navigasi halaman utama
    with st.sidebar:
        st.image("logo2-1.png", width=150)
        selected_page = option_menu(
            menu_title=None,
            options=["Dashboard", "Manajemen Data", "Visualisasi Data", "Clustering"],
            icons=["house-fill", "bar-chart-fill", "pie-chart-fill", "activity"],
            default_index=0,
        )

        # Tombol logout
        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state['authenticated'] = False
            st.rerun()

    # Tampilkan halaman sesuai dengan menu yang dipilih
    if selected_page == "Dashboard":
        from dashboard import dashboard_page
        dashboard_page()
    elif selected_page == "Manajemen Data":
        from data import data_page
        data_page()
    elif selected_page == "Visualisasi Data":
        from eda import eda_page
        eda_page()
    elif selected_page == "Clustering":
        from clusterisasi import clusterisasi_page
        clusterisasi_page()
