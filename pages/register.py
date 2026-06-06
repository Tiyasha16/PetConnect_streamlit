import streamlit as st
import re
import requests

from app import DJANGO_API_URL
REGISTER_API =  f"{DJANGO_API_URL}/api/users/register/"

st.set_page_config(page_title="Pet Rescue - Register", page_icon="🐾", layout="centered")

# nav bar
col1, col2 = st.columns([5,8])

with col1:
    if st.button("🏠", key="home_btn"):
        st.switch_page("app.py")
        st.experimental_rerun()

with col2:
    st.markdown("### 🐶 PetConnect")

# Custom CSS for gradient background and password rules styling
st.markdown("""
<style>
    .stApp {
        background: #cf88a6;
        background: radial-gradient(circle, rgba(207, 136, 166, 1) 0%, rgba(148, 187, 233, 1) 100%);
    }
    .rule-ok {
        color: green;
        font-size: 13px;
    }
    .rule-not {
        color: #555;
        font-size: 13px;
    }
    .rule-counter {
        font-size: 14px;
        font-weight: bold;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)


def go_to_login():
    st.session_state.page = "login"


def validate_password(password: str):
    """Return dictionary of password rule validation"""
    return {
        "At least 8 characters": len(password) >= 8,
        "One uppercase letter (A–Z)": bool(re.search(r'[A-Z]', password)),
        "One lowercase letter (a–z)": bool(re.search(r'[a-z]', password)),
        "One number (0–9)": bool(re.search(r'[0-9]', password)),
        "One special character (@, #, $, %, etc.)": bool(re.search(r'[@$!%*?&]', password)),
    }


st.title("Join the Pack — Start Your Journey With Us")

with st.form("signup_form", clear_on_submit=True):
    fullname = st.text_input("Full Name:")
    mobile = st.text_input("Mobile Number:")
    city = st.text_input("City:")
    options = ["", "Male", "Female", "Others", "Prefer not to say"]
    choice = st.selectbox("Gender:", options)
    email = st.text_input("Email Address:")

    is_admin = st.checkbox("Register as Admin")
    admin_code = st.text_input("Enter 6-character Admin Code", max_chars=6)

    # Password fields
    password = st.text_input("Password", type="password", key="password")
    confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")

    # Show password rules always
    rules = validate_password(password)
    passed_count = sum(rules.values())
    total_rules = len(rules)

    st.markdown("#### Password Requirements:")
    for rule, passed in rules.items():
        if passed:
            st.markdown(f"<span class='rule-ok'>✅ {rule}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span class='rule-not'>• {rule}</span>", unsafe_allow_html=True)

    # Counter below rules
    st.markdown(
        f"<div class='rule-counter'>✔️ {passed_count}/{total_rules} conditions met</div>",
        unsafe_allow_html=True,
    )

    register_btn = st.form_submit_button("Register")

    if register_btn:
        if not (fullname and mobile and email and password and confirm_password):
            st.error("⚠️ Please fill out all fields.")
        elif password != confirm_password:
            st.error("❌ Passwords do not match. Please try again.")
        elif not all(validate_password(password).values()):
            st.error("🔐 Password does not meet the required conditions.")
        else:
            if is_admin and admin_code == "":
                    st.error("⚠️ Please enter a valid 6-character alphanumeric admin code")
            else:
                try:
                    payload = {
                            "email_id": email,
                            "user_name": fullname,
                            "city": city,
                            "contact_no": mobile,
                            "passkey": password,
                            "user_role": "user",
                            "gender": choice,
                            "is_admin": is_admin
                        }
                    if is_admin and admin_code:
                        payload["admin_code"] = admin_code

                    response = requests.post(
                        REGISTER_API,
                        json=payload,
                    )

                    if response.status_code == 201:
                        st.success("🎉 Registration successful! You can now login.")
                    else:
                        st.error(f"❌ Error: {response.json()}")
                except Exception as e:
                    st.error(f"⚠️ Could not connect to backend: {e}")

# Footer → Button to go back
st.write("Already have an account?")
if st.button("👉 Back to Login"):
    go_to_login()
    st.switch_page("pages/login.py")
