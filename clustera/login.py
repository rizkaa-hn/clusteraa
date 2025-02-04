import streamlit as st
from core.auth import authenticate, register_user, validate_password
import requests
from streamlit_lottie import st_lottie

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def login_or_register():
    st.image("logo2-1.png", width=150)
    
    with st.container():
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            # Membuat tab untuk Login dan Register
            tabs = st.tabs(["Login", "Sign Up"])

            with tabs[0]:  # Tab Login
                st.subheader("Login")
                email = st.text_input("Email", placeholder="Masukkan email Anda")
                password = st.text_input("Password", placeholder="Masukkan password Anda", type="password", key="login_password")
                
                if st.button("Login", key="login_button"):
                    if authenticate(email, password):
                        st.session_state['authenticated'] = True
                        st.success("Login berhasil!")
                        st.rerun()
                    else:
                        st.error("Email atau password salah.")

            with tabs[1]:  # Tab Registrasi
                st.subheader("Sign Up")
                username = st.text_input("Username", placeholder="Masukkan username", key="register_username")
                reg_email = st.text_input("Email", placeholder="Masukkan email Anda", key="register_email")
                reg_password = st.text_input("Password", placeholder="Masukkan password Anda", type="password", key="register_password")
                confirm_password = st.text_input("Konfirmasi Password", placeholder="Masukkan ulang password Anda", type="password")
                
                if st.button("Sign Up", key="register_button"):
                    if reg_password != confirm_password:
                        st.error("Password dan konfirmasi password tidak cocok.")
                    elif not validate_password(reg_password):
                        st.error("Password harus memiliki minimal 8 karakter, termasuk huruf kapital, angka, dan simbol.")
                    else:
                        if register_user(username, reg_email, reg_password):
                            st.success("Registrasi berhasil! Silakan login.")
                        else:
                            st.error("Registrasi gagal. Silakan coba lagi.")

        with col2:
            # Menambahkan animasi di sebelah kanan form
            lottie_coding = load_lottieurl("https://lottie.host/bdefeea8-4538-4b31-85a2-6813b9c552a7/6a6gcYjgpV.json")
            st_lottie(lottie_coding, height=400, key="data")
