import streamlit as st
import hashlib
import sqlite3
from functools import wraps

def init_auth_db():
    """Initialize authentication database and create admin user if not exists"""
    conn = sqlite3.connect('consultorio.db')
    cursor = conn.cursor()
    
    # Create users table if not exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    # Check if admin user exists
    cursor.execute('SELECT * FROM users WHERE username = ?', ('Mariel',))
    if not cursor.fetchone():
        
        hashed_password = hashlib.sha256('kenti'.encode()).hexdigest()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                      ('Mariel', hashed_password))
    
    conn.commit()
    conn.close()

def verify_password(username, password):
    """Verify user credentials"""
    conn = sqlite3.connect('consultorio.db')
    cursor = conn.cursor()
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                  (username, hashed_password))
    user = cursor.fetchone()
    
    conn.close()
    return user is not None

def login_required(func):
    """Decorator to require login for accessing pages"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
            
        if not st.session_state.authenticated:
            st.title("Login")
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            
            if st.button("Iniciar Sesión"):
                if verify_password(username, password):
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
            return
        
        return func(*args, **kwargs)
    return wrapper

def logout():
    """Logout user"""
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.authenticated = False
        st.rerun()

# Initialize authentication database
init_auth_db()