import streamlit as st
import requests

from app import DJANGO_API_URL

st.set_page_config(
    page_title="Pet Rescue - My Pets",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# nav bar
col1, col2 = st.columns([5,8])

with col1:
    if st.button("🏠", key="home_btn"):
        st.switch_page("pages/dashboard.py")
        st.experimental_rerun()

with col2:
    st.markdown("### 🐶 PetConnect")

API_URL = f"{DJANGO_API_URL}/api/pets/mypets/"

# 🧠 Ensure user is logged in
if "access_token" not in st.session_state:
    st.error("Please login to view your pets.")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

st.title("🐾 My Pets")
st.markdown("View all pets you've requested to adopt or successfully adopted.")

# Fetch Data
response = requests.get(API_URL, headers=headers)
if response.status_code != 200:
    st.error("Failed to load pets.")
    st.stop()

pets = response.json()

# ✅ Custom CSS for cards
st.markdown("""
    <style>
    .pet-card {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 3px 6px rgba(0,0,0,0.1);
        padding: 15px;
        margin-bottom: 20px;
        width: 300px;
        text-align: center;
        transition: transform 0.2s ease-in-out;
    }
    .pet-card:hover {
        transform: scale(1.02);
    }
    .status-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 8px;
        font-size: 12px;
        color: white;
        margin-top: 5px;
    }
    .status-PENDING { background-color: #FFC107; }
    .status-APPROVED { background-color: #4CAF50; }
    .status-REJECTED { background-color: #F44336; }
    </style>
""", unsafe_allow_html=True)

# ✅ Display pets in grid
cols = st.columns(3)
for i, pet in enumerate(pets):
    with cols[i % 3]:
        image_url = pet.get("image_url", "https://placehold.co/300x250?text=No+Image")
        adoption_status = pet.get("adoption_status", "PENDING")

        st.markdown(
            f"""
            <div class="pet-card">
                <img src="{image_url}" style="width:100%;height:250px;object-fit:contain;border-radius:8px;">
                <h5 style="color:#2E8B57;margin:5px 0;">{pet['name']}</h5>
                <p style="font-size:13px;margin:2px 0;"><b>Species:</b> {pet['species']}</p>
                <p style="font-size:13px;margin:2px 0;"><b>Breed:</b> {pet['breed'] or 'Unknown'}</p>
                <p style="font-size:13px;margin:2px 0;"><b>Status:</b> {pet['status']}</p>
                <span class="status-badge status-{adoption_status}">{adoption_status}</span>
            </div>
            """,
            unsafe_allow_html=True
        )