import streamlit as st
import requests

from app import DJANGO_API_URL
LOGIN_API =  f"{DJANGO_API_URL}/api/users/login/"

st.set_page_config(page_title="Pet Rescue - Login", page_icon="🐾", layout="centered")

# nav bar
col1, col2 = st.columns([5,8])

with col1:
    if st.button("🏠", key="home_btn"):
        st.switch_page("app.py")
        st.experimental_rerun()

with col2:
    st.markdown("### 🐶 PetConnect")

# Custom CSS for gradient background
st.markdown("""
<style>
    .stApp {
        background: #cf88a6;
        background: radial-gradient(circle, rgba(207, 136, 166, 1) 0%, rgba(148, 187, 233, 1) 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "login"

def go_to_register():
    st.session_state.page = "register"

st.title("Log In to Continue Your Journey of Love & Rescue")

with st.form("login_form", clear_on_submit=True):
    username = st.text_input("email:")
    password = st.text_input("password:", type="password")
    login_btn = st.form_submit_button("Login")

    if login_btn:
        if username and password:
            response = requests.post(LOGIN_API, data={"email_id": username, "passkey": password})
            if response.status_code == 200:
                tokens = response.json()
                st.session_state["access_token"] = tokens["access"]
                st.session_state["user_email"] = username
                st.success("Login successful ✅")
            else:
                st.error("Invalid credentials ❌")
            st.session_state.logged_in = True
            st.success(f"Welcome back, {username}!")
            # Redirect to dashboard
            st.session_state.page = "dashboard"
            st.switch_page("pages/dashboard.py")  # Refresh the app to switch page
        else:
            st.error("Please enter both username and password.")

# Footer → Button to switch page
st.write("New here? Join the family")
if st.button("Register Today"):
    go_to_register()

# Page navigation
if st.session_state.page == "register":
    st.switch_page("pages/register.py")

# Redirect to dashboard if page is set
if st.session_state.page == "dashboard":
    st.switch_page("pages/dashboard.py")
