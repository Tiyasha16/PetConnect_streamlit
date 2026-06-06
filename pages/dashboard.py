import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO
from datetime import datetime

from app import DJANGO_API_URL

st.set_page_config(
    page_title="Pet Rescue - Dashbaord",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

PROFILE_API = f"{DJANGO_API_URL}/api/users/profile/"
PETS_API = f"{DJANGO_API_URL}/api/pets/adoptable/"
API_NOTIF_LIST = f"{DJANGO_API_URL}/api/notifications/"      # GET
API_NOTIF_MARK = f"{DJANGO_API_URL}/api/notifications/mark-read/"  # POST <id>/
API_NOTIF_MARK_ALL = f"{DJANGO_API_URL}/api/notifications/mark-all-read/"  # POST

#pre processing
# assume JWT token is stored after login
token = st.session_state.get("access_token")
headers = {"Authorization": f"Bearer {token}"} if token else {}
st.session_state.show_notifications = False
if token and "user" not in st.session_state:
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(PROFILE_API, headers=headers)

    if response.status_code == 200:
        data = response.json()
        st.session_state["user"] = data
        if(st.session_state["user"].get("user_role", '') == "admin"):
            st.session_state["admin"] = "true"
        else:
            st.session_state["admin"] = "false"

    else:
        st.error("Failed to fetch profile data")

# notification feature
# Helper to fetch notifications (cached for short TTL so it refreshes periodically)
@st.cache_data(ttl=10)   # cache for 10 seconds
def fetch_notifications():
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(API_NOTIF_LIST, headers=headers, timeout=6)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"unread_count": 0, "notifications": []}

def mark_notification_read(notif_id):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        resp = requests.post(f"{API_NOTIF_MARK}{notif_id}/", headers=headers, timeout=6)
        return resp.status_code == 200
    except:
        return False

def mark_all_read():
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        resp = requests.post(API_NOTIF_MARK_ALL, headers=headers, timeout=6)
        return resp.status_code == 200
    except:
        return False

# Check if user is logged in
if "user" not in st.session_state:
    st.warning("Please login first")
    st.switch_page("app.py")
    st.stop()

# --- Bell in navbar (call this from your nav rendering code) ---
unread_count = 0

@st.dialog("Notifications")
def requestNotifications(data):
    # if st.session_state.get("show_notifications", False):
        # st.session_state.show_notifications = not st.session_state.get("show_notifications", False)
    # refresh and show unread on top
    notifications = data.get("notifications", [])
    if not notifications:
        st.info("No notifications")
    else:
        for n in notifications:
            nid = n['id']
            title = n['title']
            msg = n.get('message') or ""
            is_read = n.get('is_read', False)
            created = n.get('created_at')
            created_fmt = created
            try:
                created_fmt = datetime.fromisoformat(created).strftime("%b %d %H:%M")
            except:
                pass

            row_cols = st.columns([3, 1])
            with row_cols[0]:
                style = "opacity:0.6;" if is_read else "font-weight:600;"
                st.markdown(f"<div style='{style}'><b>{title}</b><br><small>{msg}</small></div>", unsafe_allow_html=True)
                st.caption(created_fmt)
            with row_cols[1]:
                if not is_read:
                    if st.button("Mark read", key=f"mark-read_{nid}"):
                        approve_url = f"{DJANGO_API_URL}/api/notifications/mark-read/{nid}/"
                        r = requests.post(approve_url, headers=headers)
                        if r.status_code == 200:
                            # clear cache and refresh
                            fetch_notifications.clear()
                            st.rerun()
                        else:
                            st.error("Failed to mark read")

        # bulk actions
        c1, c2 = st.columns([1,1])
        with c1:
            if st.button("Mark all read"):
                ok = mark_all_read()
                if ok:
                    fetch_notifications.clear()
                    st.rerun()
                else:
                    st.error("Failed to mark all")

        with c2:
            if st.button("Refresh"):
                fetch_notifications.clear()
                st.rerun()

# Navbar container
with st.container():
    cols = st.columns([1, 1, 1, 3, 1, 1, 1, 1, 1])
    # home
    if cols[0].button("Home"):
        st.session_state["page"] = "home"
        if "pets" in st.session_state:
            del st.session_state["pets"]
        st.switch_page("app.py")
    # Lost
    if cols[1].button("Lost"):
        st.session_state["page"] = "lost"
        if "pets" in st.session_state:
            del st.session_state["pets"]
        st.switch_page("pages/registerPet.py")
    
    # Found
    if cols[2].button("Found"):
        st.session_state["page"] = "found"
        if "pets" in st.session_state:
            del st.session_state["pets"]
        st.switch_page("pages/registerPet.py")

    if cols[3].markdown("### 🐶 PetConnect"):
        a=""
    
    # notification
    if cols[4].button("🔔", key="notif_bell"):
        # open notifications panel
        st.session_state.show_notifications = True
        # show badge (simple)
        if unread_count > 0:
            st.markdown(f"<span style='color:#ff3b30; font-weight:bold'>{unread_count}</span>", unsafe_allow_html=True)

    # Profile
    if cols[5].button("Profile"):
        st.session_state["page"] = "profile"
        if "pets" in st.session_state:
            del st.session_state["pets"]
        st.switch_page("pages/profile.py")
    
    # Logout
    if cols[6].button("Logout"):
        st.session_state.clear()
        st.success("Logged out successfully")
        st.switch_page("app.py")
        st.rerun()

     # Logout
    if cols[7].button("📫", key="messages"):
        st.session_state["page"] = "messages"
        if "pets" in st.session_state:
            del st.session_state["pets"]
        st.switch_page("pages/adminChat.py")
    
    #admin dash
    if st.session_state["admin"]=="true" and cols[8].button("Admin Panel"):
        st.session_state["page"] = "adminDash"
        if "pets" in st.session_state:
            del st.session_state["pets"]
        st.switch_page("pages/adminDashboard.py")
    elif st.session_state["admin"]=="false" and cols[8].button("My Pets"):
        st.session_state["page"] = "mypets"
        if "pets" in st.session_state:
            del st.session_state["pets"]
        st.switch_page("pages/mypets.py")

def render_notification_bell():
    data = fetch_notifications()
    unread_count = data.get("unread_count", 0)
    # Notification panel (native)
    if st.session_state.get("show_notifications", False):
        requestNotifications(data)


# Custom CSS for gradient background
st.markdown("""
<style>
    .stApp {
        background: #cf88a6;
        background: radial-gradient(circle, rgba(207, 136, 166, 1) 0%, rgba(148, 187, 233, 1) 100%);
    }
</style>
""", unsafe_allow_html=True)

# Redirect if user is not logged in
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("You must log in first to access the dashboard.")
    st.stop()  # Stop execution of the rest of the dashboard

# st.set_page_config(page_title="Pet Rescue Dashboard", layout="wide")

render_notification_bell()

# --- Custom CSS ---
st.markdown("""
<style>
/* Remove Streamlit default padding/margin */
main > div:first-child {
    padding-top: 0rem !important;
    margin-top: 0rem !important;
}

/* Navbar (Header) */
.header {
    position: fixed;
    top: 60px;
    left: 0;
    width: 100vw; /* Full viewport width */
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 20px;
    background-color: black;
    color: white;
    margin: 0;
    box-sizing: border-box;
    z-index: 9999;
}

/* Push page content below navbar */
body, .block-container {
    padding-top: 70px !important; /* Adjust based on navbar height */
}

/* Navbar buttons */
.header button {
    background: linear-gradient(90deg, #f06292, #ffca28);
    border: none;
    color: white;
    padding: 8px 18px;
    margin: 0 5px;
    border-radius: 12px;
    cursor: pointer;
    font-weight: bold;
}

/* Welcome text */
.welcome {
    text-align: center;
    margin: 30px 0 10px 0;
    font-size: 28px;
    font-weight: bold;
}

/* Subtext */
.subtext {
    text-align: center;
    margin-bottom: 30px;
    font-size: 16px;
}

/* Card container */
.cards-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    padding: 0 50px;
}

/* Card styling */
.card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    text-align: center;
    padding: 10px;
}

.card img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    border-radius: 12px;
}

.card p {
    font-weight: bold;
    margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)

# --- Header (Navbar) ---
# st.markdown("""
# <div class="header">
#     <div class="left">
#         <button>Profile</button>
#         <button>Logout</button>
#     </div>
#     <div class="right">
#         <button>Lost</button>
#         <button>Found</button>
#         <button>Adopt</button>
#     </div>
# </div>
# """, unsafe_allow_html=True)

# --- Welcome Section ---
username=st.session_state["user"].get('user_name', '')
# st.title("**Welcome "+ username +" to Pet Adoption and Rescue Portal 🐾**",)
st.markdown('<div class="welcome">Welcome to Pet Rescue! Let’s make tails wag and hearts happy today.</div>', unsafe_allow_html=True)
st.markdown('<div class="subtext">Report lost or found pets, browse adoptable furry friends, and help connect animals with loving homes—all in one compassionate platform.</div>', unsafe_allow_html=True)

# --- Pets Available for Adoption ---
st.markdown('<h3 style="text-align:center;">Pets Available for Adoption</h3>', unsafe_allow_html=True)

# --- Dynamic pet list from folder ---
# Inject CSS for card styling
st.markdown("""
    <style>
        .pet-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .pet-card {
            background: white;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.08);
            display: flex;
            flex-direction: column;
            align-items: center;
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        }
        .pet-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.12);
        }
        .pet-card img {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 10px;
            margin-bottom: 12px;
            background: #f5f5f5;
        }
        .pet-info {
            font-size: 14px;
            margin: 4px 0;
            text-align: left;
            width: 100%;
        }
        .pet-info b {
            color: #444;
        }
        .status {
            margin-top: 8px;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: bold;
            text-align: center;
            display: inline-block;
        }
        .status.lost { background: #ffe5e5; color: #d9534f; }
        .status.found { background: #e6f0ff; color: #0275d8; }
        .status.adoptable { background: #e6ffe6; color: #5cb85c; }
    </style>
""", unsafe_allow_html=True)

# Example grid rendering
def display_local_image(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        html = f'<img src="data:image/jpeg;base64,{b64}">'
        st.markdown(html, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"File not found: {path}")
# Display pets in grid (3 per row)
def display_pet_grid(pets):
    # ====== Default Image ======
    DEFAULT_IMG = "https://cdn-icons-png.flaticon.com/512/616/616408.png"

    # ====== Display Cards ======
    cols_per_row = 3
    for i in range(0, len(pets), cols_per_row):
        cols = st.columns(cols_per_row, gap="medium")
        for j, col in enumerate(cols):
            if i + j < len(pets):
                pet = pets[i + j]
                image_url = ""
                if pet.get("image") is None:
                    image_url = DEFAULT_IMG
                else:
                    image_url = pet['image']
                try:
                    img_response = requests.get(image_url)
                    img = Image.open(BytesIO(img_response.content))
                except:
                    img = Image.open(requests.get(DEFAULT_IMG, stream=True).raw)
                with col:
                    st.markdown(
                        f"""
                        <div style="
                            background-color:white;
                            border-radius:12px;
                            box-shadow: 0px 3px 6px rgba(0,0,0,0.1);
                            padding:2px;
                            margin-bottom:15px;
                            text-align:center;
                            width: 300px;
                            display:flex;
                            flex-direction:column;
                            justify-content:space-between;
                        ">
                            <img src="{image_url}" style="width:100%; height:250px; object-fit:contain; border-radius:10px;">
                            <h5 style="color:#2E8B57; margin:2px 0; color: black;">{pet['name']}</h5>
                            <p style="font-size:13px; margin:2px 0; color: black;"><b>Species:</b> {pet['species']}</p>
                            <p style="font-size:13px; margin:2px 0; color: black;"><b>Breed:</b> {pet['breed'] or 'Unknown'}</p>
                            <p style="font-size:13px; margin:2px 0; color: black;"><b>Color:</b> {pet['color']}</p>
                            <p style="font-size:13px; margin:2px 0; color: black;"><b>Location:</b> {pet['location_found']}</p>
                            <p style="font-size:13px; margin:2px 0; color: black;"><b>Status:</b> {pet['status']}</p>
                            <p style="font-size:12px; margin:2px 0; color:#555;"><b>Details:</b> {pet.get('details', 'No details')}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    # ✅ Add Adopt Button Below the Card (not inside the div)
                    if pet["is_adoptable"]:
                        # if st.button(f"🐾 Adopt {pet['name']}", key=f"adopt_{pet['pet_id']}", width=300, type='secondary'):
                        if st.button(f"Check Details", key=f"adopt_{pet['pet_id']}", width=300, type='secondary'):
                            st.session_state["page"] = "lost"
                            if "pets" in st.session_state:
                                del st.session_state["pets"]
                            st.session_state['petInfo'] = pet
                            st.switch_page("pages/petsProfile.py")
                    else:
                        st.markdown(
                            """
                            <button disabled style="
                                background-color: #ccc;
                                color: #555;
                                border: none;
                                padding: 6px 14px;
                                border-radius: 6px;
                                cursor: not-allowed;
                                font-size: 14px;
                                margin-top: 6px;">
                                ❌ Not Adoptable
                            </button>
                            """,
                            unsafe_allow_html=True
                        )
 
def load_pets():
    """Fetch pets from API only once."""
    if "pets" not in st.session_state:
        try:
            token = st.session_state.get("access_token")  # JWT from login
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            response = requests.get(PETS_API, headers=headers)
            
            if response.status_code == 200:
                pets = response.json()  # Expecting list of pet dicts
                st.session_state.pets = pets
            else:
                st.session_state.pets = []
                st.error("Failed to load pets")
        except Exception as e:
            st.session_state.pets = []
            st.error(f"Error fetching pets: {e}")
    

# Load pets once
load_pets()

pets = st.session_state.get("pets", [])
# initialize controls in session state (keeps inputs persistent)
if "pet_search_text" not in st.session_state:
    st.session_state.pet_search_text = ""
if "pet_species_filter" not in st.session_state:
    st.session_state.pet_species_filter = "All"
if "pet_only_adoptable" not in st.session_state:
    st.session_state.pet_only_adoptable = False

# UI: search + species + adoptable controls (inline)
c1, c2, c3, c4, c5 = st.columns([4, 3, 2, 1, 2])
with c1:
    st.session_state.pet_search_text = st.text_input(
        "Search pets (name, breed, color, location, details, species)",
        value=st.session_state.pet_search_text
    )
with c2:
    # derive species list from pets (keep unique & sorted)
    species_set = sorted({(p.get("species") or "Unknown") for p in pets})
    species_options = ["All"] + species_set
    if st.session_state.pet_species_filter not in species_options:
        st.session_state.pet_species_filter = "All"
    st.session_state.pet_species_filter = st.selectbox(
        "Species",
        species_options,
        index=species_options.index(st.session_state.pet_species_filter)
    )
with c3:
    st.markdown("<br>", unsafe_allow_html=True)
    st.session_state.pet_only_adoptable = st.checkbox(
        "Only adoptable",
        value=st.session_state.pet_only_adoptable
    )
with c4:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Reset"):
        st.session_state.pet_search_text = ""
        st.session_state.pet_species_filter = "All"
        st.session_state.pet_only_adoptable = False
        st.rerun()

# Filtering algorithm (case-insensitive, partial)
def _matches_search(pet, q):
    if not q:
        return True
    q = q.strip().lower()
    for key in ("name", "breed", "color", "location_found", "details", "species"):
        val = pet.get(key) or ""
        if q in str(val).lower():
            return True
    return False

def _matches_species(pet, species_sel):
    if not species_sel or species_sel == "All":
        return True
    return (pet.get("species") or "").strip().lower() == species_sel.strip().lower()

filtered_pets = []
for pet in pets:
    # search text
    if not _matches_search(pet, st.session_state.pet_search_text):
        continue
    # species filter
    if not _matches_species(pet, st.session_state.pet_species_filter):
        continue
    # adoptable filter
    if st.session_state.pet_only_adoptable and not pet.get("is_adoptable", False):
        continue
    filtered_pets.append(pet)

# replace pets variable used by display function with filtered_pets
pets = filtered_pets
if not pets:
    st.info("No pets available right now.")
else:
    display_pet_grid(pets)

 