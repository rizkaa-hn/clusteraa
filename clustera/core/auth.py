import mysql.connector
import streamlit as st
import bcrypt
import re
from core.connection import connect_to_app_database

def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    """Check if a plaintext password matches a hashed password."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def register_user(username: str, email: str, password: str) -> bool:
    """Register a new user after checking if the username and email are unique."""
    conn = connect_to_app_database()
    if conn:
        try:
            cursor = conn.cursor()

            # Check if the username already exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
            if cursor.fetchone()[0] > 0:
                st.error(f"Username '{username}' already exists.")
                return False

            # Check if the email already exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
            if cursor.fetchone()[0] > 0:
                st.error(f"Email '{email}' already exists.")
                return False
            
            # Hash the password before storing it
            hashed_password = hash_password(password)

            # Insert new user into the database
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
            conn.commit()
            st.success(f"User '{username}' registered successfully!")
            return True
        except mysql.connector.Error as e:
            st.error(f"Error registering user: {e}")
            return False
        finally:
            conn.close()

def validate_password(password: str) -> bool:
    """Validate if the password meets the strong password criteria."""
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):  # At least one uppercase letter
        return False
    if not re.search(r"[0-9]", password):  # At least one digit
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):  # At least one special character
        return False
    return True

def authenticate(email: str, password: str) -> bool:
    """Authenticate a user by verifying their email and password."""
    conn = connect_to_app_database()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, username, password FROM users WHERE email = %s", (email,))
            result = cursor.fetchone()

            if result:
                user_id, username, hashed_password = result

                # Debugging output
                print(f"Email: {email}, Password Input: {password}")
                print(f"Hashed Password from DB: {hashed_password}")

                # Verify password with bcrypt
                if check_password(password, hashed_password):
                    st.session_state['authenticated'] = True
                    st.session_state['username'] = username
                    st.session_state['user_id'] = user_id
                    return True
                else:
                    st.error("Invalid email or password.")
                    print("Password mismatch.")  # Debugging output
                    return False
            else:
                st.error("Invalid email or password.")
                print("No user found.")  # Debugging output
                return False
        except mysql.connector.Error as e:
            st.error(f"Error authenticating user: {e}")
            print(f"Database error: {e}")  # Debugging output
            return False
        finally:
            conn.close()
    else:
        st.error("Failed to connect to the database.")
        print("Connection failed.")  # Debugging output
        return False