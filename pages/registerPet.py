import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/api/pets/add/"
FOUND = "Found"
LOST = "Lost"

# Custom CSS for gradient background
st.markdown("""
<style>
    .stApp {
        background: #cf88a6;
        background: radial-gradient(circle, rgba(207, 136, 166, 1) 0%, rgba(148, 187, 233, 1) 100%);
    }
</style>
""", unsafe_allow_html=True)

subCat = st.session_state["page"]
if subCat == "lost":
    title = LOST
else:
    title = FOUND

# nav bar
col1, col2 = st.columns([5,8])

with col1:
    if st.button("🏠", key="home_btn"):
        st.switch_page("pages/dashboard.py")
        st.rerun()

with col2:
    st.markdown("### 🐶 PetConnect")

st.title(f"Report {title} Pet")

# Check if logged in
if "access_token" not in st.session_state:
    st.warning("⚠️ Please log in first to report a pet.")
else:
    with st.form("pet_form", clear_on_submit=True):
        name = st.text_input("Pet Name")
        species = st.text_input("Species")
        breed = st.text_input("Breed")
        color = st.text_input("Color")
        location_found = st.text_area(f"Location {title}")
        if subCat == "lost":
            health_condition = st.text_input("Health Condition")
        details = st.text_area("Additional Details")
        status = subCat.upper()

        image_file = st.file_uploader("Upload Pet Image", type=["jpg", "jpeg", "png"])

        submitted = st.form_submit_button("Submit")

    if submitted:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        data = {
            "name": name,
            "species": species,
            "breed": breed,
            "color": color,
            "location_found": location_found,
            "details": details,
            "status": status,
        }
        files = None
        if image_file:
            files = {"image": (image_file.name, image_file, image_file.type)}
        if subCat == "lost":
            data["health_condition"] = health_condition

        response = requests.post(API_URL, data=data, files=files, headers=headers)

        if response.status_code == 201:
            st.success("✅ Pet details uploaded successfully!")
        else:
            st.error(f"❌ Error: {response.text}")
