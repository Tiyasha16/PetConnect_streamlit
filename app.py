import streamlit as st
from PIL import Image
import os

DJANGO_API_URL = os.environ.get("DJANGO_API_BASE_URL", "http://127.0.0.1:8000")

loggedIn = False
# Check if user is logged in
if "user" in st.session_state:
    loggedIn = True

# Custom CSS for gradient background
st.markdown("""
<style>
    .stApp {
        background: #cf88a6;
        background: radial-gradient(circle, rgba(207, 136, 166, 1) 0%, rgba(148, 187, 233, 1) 100%);
    }
</style>
""", unsafe_allow_html=True)

# st.sidebar.title("🐾 PetRescue Navigation")
# menu = st.sidebar.radio("Menu", ["Home", "Register", "Login"])

# --- Navbar ---
login_clicked = False
register_clicked = False
dashboard_clicked = False
col1, col2, col3 = st.columns([12, 1, 2])  # adjust widths
with col1:
    st.markdown("### 🐶 PetConnect")  # App title / logo
with col2:
    if loggedIn:
        a=""
    else:
        login_clicked = st.button("Login")
with col3:
    if not loggedIn:
        register_clicked = st.button("Register")
    else:
        dashboard_clicked = st.button("Dashboard")


st.title("**Welcome to Pet Adoption and Rescue Portal 🐾**")
st.markdown("**Helping lost pets reunite with their families ❤️**")

# --- Display in 3 columns ---
col1, col2, col3 = st.columns(3)

with col1:
    st.image("./resources/image5.jpg", caption="Take me home 🐶", width=350 )

with col2:
    st.image("./resources/image1.jpg", caption="Pets at shelter 🐾", width=350)

with col3:
    st.image("./resources/image4.jpg", caption="Safe at home 🐱", width=350)

# --- Handle Button Clicks ---
if dashboard_clicked:
    st.switch_page("pages/dashboard.py")
    st.rerun()
elif login_clicked:
    st.switch_page("pages/login.py")   # assumes you create pages/login.py
elif register_clicked:
    st.switch_page("pages/register.py") 

# elif menu == "Register":
#     import pages.register

# elif menu == "Login":
#     import pages.login
