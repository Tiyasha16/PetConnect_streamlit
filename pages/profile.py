import streamlit as st

# Custom CSS for gradient background

st.markdown("""
<style>
    .stApp {
        background: #cf88a6;
        background: radial-gradient(circle, rgba(207, 136, 166, 1) 0%, rgba(148, 187, 233, 1) 100%);
    }
</style>
""", unsafe_allow_html=True)

# Check if user is logged in
if "user" not in st.session_state:
    st.warning("Please login first")
    st.stop()

user = st.session_state["user"]

# nav bar
col1, col2 = st.columns([5,8])

with col1:
    if st.button("🏠", key="home_btn"):
        st.switch_page("pages/dashboard.py")
        st.experimental_rerun()

with col2:
    st.markdown("### 🐶 PetConnect")

# Page title
st.title("Profile Page")

# Create two columns: one for image, one for details
col1, col2 = st.columns([1, 2])

# Column 1: Profile Image
with col1:
    st.image(user.get("profile_image", "https://via.placeholder.com/150"), width=150)

# Column 2: User Details
with col2:
    st.subheader(user.get("user_name", "Username"))
    st.text(f"Email: {user.get('email_id', '')}")
    st.text(f"Contact: {user.get('contact_no', '')}")
    st.text(f"Gender: {user.get('gender', '')}")
    st.text(f"City: {user.get('city', '')}")

# Add a logout button
if st.button("Logout"):
    st.session_state.clear()
    st.success("Logged out successfully")
    st.switch_page("app.py")
    st.experimental_rerun()
