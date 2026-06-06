import streamlit as st
import requests
from PIL import Image
from io import BytesIO
from pages.chatFunc import render_chat_popup, open_chat_for_pet
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



ADOPT_API = "http://127.0.0.1:8000/api/pets/adopt/"
CLAIM_API = "http://127.0.0.1:8000/api/pets/claim/"

# nav bar
col1, col2 = st.columns([5,8])

with col1:
    if st.button("🏠", key="home_btn"):
        st.switch_page("pages/dashboard.py")
        st.rerun()

with col2:
    st.markdown("### 🐶 PetConnect")

# Page title
st.title("Pets Profile")
DEFAULT_IMG = "https://cdn-icons-png.flaticon.com/512/616/616408.png"

def show_pet_details():
    pet = st.session_state.get("petInfo")

    if not pet:
        st.error("No pet selected.")
        return

    st.title(f"🐶 Pet Details: {pet['name']}")
    open_chat_for_pet(pet)

    # Image
    image_url = ""
    if pet.get("image") is None:
        image_url = DEFAULT_IMG
    else:
        image_url = pet['image']

    col1, col2, col3 = st.columns([1,1, 1])
    # Info grid
    with col1:
        st.markdown(f"""<img src="{image_url}" style="height:250px; object-fit:contain; border-radius:10px; margin-bottom: 20px;">""", unsafe_allow_html=True)
    with col2:
        st.write(f"**Species:** {pet['species']}")
        st.write(f"**Breed:** {pet['breed']}")
        st.write(f"**Color:** {pet['color']}")
        st.write(f"**Location Found:** {pet['location_found']}")
        st.write(f"**Details:** {pet.get('details', '-')}")
        st.write(f"**Status:** {pet['status']}")

    st.markdown("---")

    # Buttons
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        if st.session_state["admin"]=="false" and st.button("🐾 Adopt", key="adopt_btn"):
            st.info("Sending adoption request...")
            try:
                headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
                response = requests.post(f"{ADOPT_API}{pet['pet_id']}/", headers=headers)

                if response.status_code == 201:
                    st.success(f"Adoption request for {pet['name']} sent successfully! ✅")
                    st.session_state[f"adopted_{pet['pet_id']}"] = True
                elif response.status_code == 400:
                    st.warning(response.json().get("message", "Request already exists!"))
                else:
                    st.error("Something went wrong while sending request.")
            except Exception as e:
                st.error(f"Error: {e}")

    with c2:
        if st.session_state["admin"]=="false" and st.button("📍 Claims Pet", key="claim_btn"):
            st.info("Sending claim request...")
            try:
                headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
                response = requests.post(f"{CLAIM_API}{pet['pet_id']}/", headers=headers)

                if response.status_code == 201:
                    st.success(f"Claim request for {pet['name']} sent successfully! ✅")
                    st.session_state[f"adopted_{pet['pet_id']}"] = True
                elif response.status_code == 400:
                    st.warning(response.json().get("message", "Request already exists!"))
                else:
                    st.error("Something went wrong while sending request.")
            except Exception as e:
                st.error(f"Error: {e}")

    with c3:
        if st.session_state.get("msg_refresh") == True:
            del st.session_state["chat_input"]
            render_chat_popup()
        st.session_state["msg_refresh"] = False

        if st.session_state["admin"]=="false" and st.session_state["user"].get('id',0) != pet['user'] and st.button("💬 Chat - Ask Queries", key="chat_btn"):
            render_chat_popup()

show_pet_details()
