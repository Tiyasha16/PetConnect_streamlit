from django import http
import streamlit as st
import requests

from app import DJANGO_API_URL

st.set_page_config(page_title="Admin Dashboard", layout="wide", initial_sidebar_state="collapsed")

# getting api data
STATS_API = f"{DJANGO_API_URL}/api/pets/admin/stats/"
REQUEST_PENDING_API = f"{DJANGO_API_URL}/api/pets/admin/requests/pending/"
API_LIST = f"{DJANGO_API_URL}/api/pets/admin/adoptions/"
API_MANAGE = f"{DJANGO_API_URL}/api/pets/admin/adoptions/"

if "access_token" not in st.session_state:
    st.warning("Please login as admin.")
    st.stop()

adminStats = {
    "total_pets": 0,
    "adoptable_pets": 0,
    "pending_requests": 0,
}
try:
    token = st.session_state.get("access_token")  # JWT from login
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = requests.get(STATS_API, headers=headers)

    if response.status_code == 200:
        pets = response.json()  # Expecting list of pet dicts
        adminStats = {}
        adminStats = pets
    else:
        adminStats = {}
        st.error("Failed to load stats")
except Exception as e:
    st.session_state.pets = []
    st.error(f"Error fetching stats: {e}")

# Custom CSS for gradient background
page_bg = """
<style>
.stApp {
    background: linear-gradient(90deg, 
        #f8f9eb 0%, 
        #b7e6f7 30%, 
        #c9d8f9 60%, 
        #eac2f5 100%
    );
    background-attachment: fixed;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# Check if user is logged in
if "user" not in st.session_state:
    st.warning("Please login first")
    st.switch_page("app.py")
    st.stop()

# Navbar container
with st.container():
    cols = st.columns([5, 1, 1, 1])

    #Title
    if cols[0].markdown("""
        <div style="
            display:inline-block;
            background-color:#2b6edc;
            color:white;
            padding:6px 14px;
            border-radius:6px;
            font-size:20px;
            font-weight:600;
        ">
            🐶 PetConnect
        </div>
    """, unsafe_allow_html=True):
        a = ""

    # Profile
    if cols[1].button("Profile"):
        st.session_state["page"] = "profile"
        if "pets" in st.session_state:
            del st.session_state["pets"]
        st.switch_page("pages/profile.py")
    
    # Logout
    if cols[2].button("Logout"):
        st.session_state.clear()
        st.success("Logged out successfully")
        st.switch_page("app.py")
        st.experimental_rerun()
    
    #admin dash
    if st.session_state["admin"]=="true" and cols[3].button("Dashboard"):
        st.session_state["page"] = "dashboard"
        st.switch_page("pages/dashboard.py")

# --- Custom CSS ---
st.markdown("""
    <style>
    # body {
    #     background-color: #111111;
    # }
    .dashboard-header {
        background: linear-gradient(90deg, #ff7f7f, #7f7fff);
        padding: 20px 40px;
        border-radius: 15px;
        color: white;
        margin-bottom: 15px;
    }
    .dashboard-header h1 {
        margin: 0;
        font-size: 32px;
        font-weight: 700;
    }
    .dashboard-header p {
        font-size: 16px;
        opacity: 0.9;
    }
    .card {
        background-color: #896C6C;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        transition: transform 0.2s, box-shadow 0.2s;
        text-decoration: none;
        display: block;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(255,255,255,0.2);
    }
    .card h2 {
        margin: 0;
        font-size: 32px;
        font-weight: bold;
        color: white;
    }
    .card p {
        margin-top: 5px;
        font-size: 14px;
        color: #ccc;
    }
    .btn {
        border-radius: 10px;
        padding: 10px 20px;
        color: white;
        border: none;
        cursor: pointer;
        font-weight: bold;
        margin-right: 10px;
    }
    .btn-pets {
        background-color: #ff6b6b;
    }
    .btn-users {
        background-color: #3cb371;
    }
    .card:hover { text-decoration: none; }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="dashboard-header">
    <span style="background:#444;padding:4px 10px;border-radius:8px;font-size:14px;">Administrator</span>
    <h1>Admin Dashboard</h1>
    <p>Manage the Pet Welfare Hub platform and oversee all pet listings and user activities.</p>
    
</div>
""", unsafe_allow_html=True)

if st.button("Manage Users Chat", type='primary'):
    st.session_state["page"] = "userChat"
    st.switch_page("pages/adminChat.py")

# --- Clickable Cards ---
col0, col1, col2, col3, col4 = st.columns(5)

def clickable_card(link, number, title, subtitle, emoji):
    card_html = f"""
    <a href="{link}" target="_self" class="card" style="text-decoration: none;">
        <h2>{number}</h2>
        <p>{emoji} {title}<br><small>{subtitle}</small></p>
    </a>
    """
    return card_html

with col1:
    st.markdown(clickable_card("#", adminStats['total_pets'], "Total Pets", "All listings", "🐾"), unsafe_allow_html=True)
with col2:
    st.markdown(clickable_card("#", adminStats['adoptable_pets'], "For Adoption", "Available now", "💚"), unsafe_allow_html=True)
with col3:
    st.markdown(clickable_card("#", adminStats['pending_requests'], "Pending Requests", "Need review", "⏳"), unsafe_allow_html=True)

st.markdown("### 🐾 Pending Pet Requests")
st.markdown("---")

token = st.session_state.get("access_token")
headers = {"Authorization": f"Bearer {token}"} if token else {}
response = requests.get(REQUEST_PENDING_API, headers=headers)
if response.status_code == 200:
    requests_data = response.json()
else:
    st.error("Failed to load requests.")
    requests_data = []

@st.dialog("Approve or Reject Pet Request")
def requestDialog(req):
    pet = req.get("pet", {})
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image(
            pet.get("image_url", "https://placehold.co/300x200?text=No+Image"),
            width=200,
        )
    pet_info = f"""
        ### {pet.get('name', 'Unnamed Pet')}
        **Species:** {pet.get('species', '-')}  
        **Breed:** {pet.get('breed', '-')}  
        **Color:** {pet.get('color', '-')}  
        **Location Found:** {pet.get('location_found', '-')}  
        **Details:** {pet.get('details', '-')}  
        **Health Condition:** {pet.get('health_condition', '-')}  
        **Status:** `{req.get('request_type', '-')}`
        """
    st.markdown(pet_info)
    colA, colB = st.columns(2)
    with colA:
        if st.button("✅ Approve", key=f"approve_{req['request_id']}"):
            approve_url = f"{DJANGO_API_URL}/api/pets/admin/requests/approve/{req['request_id']}/"
            r = requests.post(approve_url, headers=headers)
            if r.status_code == 200:
                st.success("Request Approved ✅")
                st.rerun()

    with colB:
        if st.button("❌ Reject", key=f"reject_{req['request_id']}"):
            reject_url = f"{DJANGO_API_URL}/api/pets/admin/requests/reject/{req['request_id']}//"
            r = requests.post(reject_url, headers=headers)
            if r.status_code == 200:
                st.warning("Request Rejected ❌")
                st.rerun()

if not requests_data:
    # st.info("No pending requests found.")
    print("no found or lost request")
else:
    for req in requests_data:
        pet = req.get("pet", {})
        with st.container(border=True, height=120):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.markdown(f"**Species:** {pet.get('species', '-')}")
            with col2:
                st.markdown(f"**Breed:** {pet.get('breed', '-')}")
            with col3:
                st.markdown(f"**Status:** `{req.get('request_type', '-')}`")

            # Button to open modal (popup)
            if st.button(f"View Details 🐶", key=f"view_{req['request_id']}"):
                requestDialog(req)
                # with st.modal(f"Request #{req['request_id']} Details"):
                    

            st.markdown(
                """
                <style>
                div[data-testid="stDialog"] > div {
                    border-radius: 10px;
                    padding: 10px 20px;
                    margin-bottom: 10px;
                    align-content: center;
                    box-shadow: 0 1px 4px rgba(0,0,0,0.1);
                }
                </style>
                """,
                unsafe_allow_html=True
            )

# adoption requests
headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

response = requests.get(API_LIST, headers=headers)
if response.status_code != 200:
    st.error("Failed to fetch adoption requests.")
    st.stop()

requests_data = response.json()

if not requests_data:
    st.info("No pending requests at the moment.")
    st.stop()

# CSS for cards
st.markdown("""
    <style>
    .adopt-card {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        padding: 15px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .adopt-card img {
        height: 80px;
        width: 80px;
        object-fit: cover;
        border-radius: 8px;
    }
    .adopt-btn {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 5px 10px;
        border-radius: 5px;
        cursor: pointer;
    }
    .reject-btn {
        background-color: #E74C3C;
        color: white;
        border: none;
        padding: 5px 10px;
        border-radius: 5px;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

@st.dialog("Approve or Reject Pet Adoption Request")
def requestAdoptionDialog(pet, adopter, adoption_id):
    col1, col2 = st.columns([1, 2])
    with col1:
        pet_img = pet.get("image_url", "https://placehold.co/300x250?text=No+Image")
        if pet_img == "":
            pet_img = "https://placehold.co/300x250?text=No+Image"
        else:
            pet_img = f"{DJANGO_API_URL}"+pet_img
        st.image(pet_img, use_container_width=True)
    
    with col2:
        st.subheader("🐾 Pet Information")
        st.markdown(f"**Name:** {pet['name']}")
        st.markdown(f"**Species:** {pet['species']}")
        st.markdown(f"**Breed:** {pet['breed'] or 'Unknown'}")
        st.markdown(f"**Color:** {pet['color']}")
        st.markdown(f"**Status:** {pet['status']}")
        st.markdown(f"**Details:** {pet.get('details', 'No details available')}")

    st.divider()

    st.subheader("👤 Adopter Information")
    st.markdown(f"**Name:** {adopter['username']}")
    st.markdown(f"**Email:** {adopter['email']}")
    st.markdown(f"**City:** {adopter['city']}")
    st.markdown(f"**Contact:** {adopter['contact']}")
    st.markdown(f"**Previous Approved Adoptions:** {adopter['total_adopted']}")

    st.divider()

    colA, colB = st.columns([1, 1])
    with colA:
        if st.button("✅ Approve", key="approve_btn", use_container_width=True):
            manage_res = requests.post(f"{API_MANAGE}{adoption_id}/", json={"action": "APPROVE"}, headers=headers)
            if manage_res.status_code == 200:
                st.success("Adoption approved successfully!")
                st.rerun()
            else:
                st.error("Failed to approve request.")

    with colB:
        if st.button("❌ Reject", key="reject_btn", use_container_width=True):
            manage_res = requests.post(f"{API_MANAGE}{adoption_id}/", json={"action": "REJECT"}, headers=headers)
            if manage_res.status_code == 200:
                st.warning("Adoption rejected.")
                st.rerun()
            else:
                st.error("Failed to reject request.")

# ✅ Show requests
for req in requests_data:
    pet = req["pet"]
    adopter = req["user"]
    pet_img = pet.get("image_url", "")

    with st.container(border=True):
        st.markdown(f"**🐕 Pet Name:** {pet['name']}")
        st.markdown(f"**Species:** {pet['species']} | **Breed:** {pet['breed'] or 'Unknown'}")
        st.markdown(f"**Requested by:** {adopter['username']} ({adopter['email']})")

        # View details button
        view_key = f"view_{req['adoption_id']}"
        if st.button("👁 View Details", key=view_key, use_container_width=True):
            requestAdoptionDialog(pet, adopter, req["adoption_id"])
