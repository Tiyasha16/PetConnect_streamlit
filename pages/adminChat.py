# pages/adminChat.py
import streamlit as st
import requests
import streamlit.components.v1 as components
import html
from datetime import datetime


st.set_page_config(
    page_title="Messenger",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------- CONFIG -----------------
API_BASE     = "http://127.0.0.1:8000/api"
API_CONVS    = f"{API_BASE}/chats/conversations"                        # GET
API_MESSAGES  = "http://127.0.0.1:8000/api/chats/conversations/{conversation_id}/messages/"
API_MARK_READ = f"{API_BASE}/chats/{{conv_id}}/mark-read/"  # POST
API_ASSIGN    = f"{API_BASE}/chats/{{conv_id}}/assign/"     # POST


# Check if user is logged in
if "user" not in st.session_state:
    st.warning("Please login first")
    st.switch_page("app.py")
    st.stop()

# Custom CSS for gradient background
st.markdown("""
<style>
    .stApp {
        background: #cf88a6;
        background: radial-gradient(circle, rgba(207, 136, 166, 1) 0%, rgba(148, 187, 233, 1) 100%);
    }
</style>
""", unsafe_allow_html=True)

user = st.session_state["user"]
userid = user.get('id', '')

if "access_token" not in st.session_state:
    st.warning("Please login as admin.")
    st.stop()

# Navbar container
with st.container():
    cols = st.columns([3, 1, 1, 1, 1])

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
    
    # Dashbaord
    if cols[2].button("Dashboard", key="home_btn"):
        st.switch_page("pages/dashboard.py")
        st.rerun()

    # Logout
    if cols[3].button("Logout"):
        st.session_state.clear()
        st.success("Logged out successfully")
        st.switch_page("app.py")
        st.rerun()
    
    #admin dash
    if st.session_state["admin"]=="true" and cols[4].button("Admin Dashboard"):
        st.session_state["page"] = "adminDash"
        st.switch_page("pages/adminDashboard.py")

# ----------------- HELPERS -----------------
def get_headers():
    token = st.session_state.get("access_token")     
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

@st.cache_data(ttl=6)
def fetch_conversations():
    try:
        r = requests.get(API_CONVS, headers=get_headers(), timeout=6)
        if r.status_code == 200:
            if len(r.json()) > 0:
                return r.json()
        else:
            st.error(f"Failed to load conversations ({r.status_code})")
            return []
    except Exception as e:
        st.error(f"Network error conv: {e}")
        return []

@st.cache_data(ttl=4)
def fetch_messages(conv_id):
    try:
        url = API_MESSAGES.format(conversation_id=conv_id)
        r = requests.get(url, headers=get_headers(), timeout=6)
        if r.status_code == 200:
            if len(r.json()) > 0:
                return r.json()
        else:
            st.warning(f"Failed to load messages ({r.status_code})")
            return []
    except Exception as e:
        st.warning(f"Network error fetch: {e}")
        return []

def post_message(conv_id, text):
    try:
        url = API_MESSAGES.format(conversation_id=conv_id)
        r = requests.post(url, json={"text": text}, headers=get_headers(), timeout=6)
        return r
    except Exception as e:
        st.error(f"Network error post: {e}")
        return None

def mark_conv_read(conv_id):
    try:
        url = API_MARK_READ.format(conv_id=conv_id)
        r = requests.post(url, headers=get_headers(), timeout=6)
        return r
    except Exception as e:
        st.error(f"Network error mark read: {e}")
        return None

def assign_conv(conv_id):
    try:
        url = API_ASSIGN.format(conversation_id=conv_id)
        r = requests.post(url, headers=get_headers(), timeout=6)
        return r
    except Exception as e:
        st.error(f"Network error assign conv: {e}")
        return None

# ----------------- PAGE STATE -----------------
st.set_page_config(page_title="Admin — Chats", layout="wide")
if "selected_conv" not in st.session_state:
    st.session_state.selected_conv = None
# if "message_input" not in st.session_state:
#     st.session_state.message_input = ""
if "conv_refresh_key" not in st.session_state:
    st.session_state.conv_refresh_key = 0
if "admin_message_input" not in st.session_state:
    st.session_state["admin_message_input"] = ""
# ----------------- UI -----------------
st.title("Conversations")

top_left, top_right = st.columns([0.85, 0.15])
with top_right:
    if st.button("↻ Refresh all", key="refresh_all"):
        fetch_conversations.clear()
        fetch_messages.clear()
        del st.session_state["admin_message_input"]
        st.session_state.conv_refresh_key += 1
        st.rerun()

# Load convs
conversations = fetch_conversations()

if not conversations:
    st.info("No conversations yet.")
    st.stop()

# Layout: left list, right detail
left_col, right_col = st.columns([0.33, 0.67])

with left_col:
    # sort by last message time if available (backend ideally returns order)
    for conv in conversations:
        conv_id = conv.get("conv_id")
        pet = conv.get("pet") or {}
        pet_name = conv.get("pet_name") if isinstance(pet, dict) else str(pet)
        # user = conv.get("user") or {}
        # user_email = last_msg.get("sender") if isinstance(user, dict) else str(user)
        # user_name = conv.get("user_name")
        unread = conv.get("unread_count", 0)
        # last_msg = conv.get("last_message", "")
        label = f"{pet_name or 'Pet'}"
        if unread:
            label = f"{label}  •  🔴 {unread}"

        # Button per conversation to select
        if st.button(label, key=f"conv_{conv_id}"):
            st.session_state.selected_conv = conv_id
            fetch_messages.clear()
            del st.session_state["admin_message_input"]
            st.rerun()

    st.markdown("---")
    st.caption("Click a conversation to view and reply. Use Refresh to reload list.")

# Right area: show selected or first conversation
with right_col:
    selected = st.session_state.selected_conv or conversations[0].get("conv_id")
    conv_meta = next((c for c in conversations if c.get("conv_id") == selected), None)
    if not conv_meta:
        st.warning("Selected conversation metadata not found. Try refreshing.")
    else:
        # pet_data = conv_meta.get("pet")
        # user_data = conv_meta.get("user_name")
        admin_assigned = conv_meta.get("admin")

        # # Handle cases where pet or user is just an ID
        # if isinstance(pet_data, dict):
        #     pet_name = pet_data.get("name", "-")
        # else:
        #     pet_name = f"Pet ID {pet_data}"

        # if isinstance(user_data, dict):
        # user_email = conv_meta.get("user_name", "-")

        # st.subheader(f"Conversation #{selected}")
        # st.write(f"**Pet:** {pet_name}    **User:** {user_email}")
        # if admin_assigned:
        #     st.write(f"**Assigned admin:** {admin_assigned.get('email')}")

        st.markdown("---")

        # ----- Messages: render inside iframe (safe, scrollable) -----
        messages = fetch_messages(selected) or []
        # build messages HTML (escape user text)
        msgs_html = ""
        for m in messages:
            sender_id = m.get("sender").get("id")
            sender_username = html.escape(str(m.get("sender").get("user_name")))
            raw_text = m.get("text", "") or ""
            text = html.escape(raw_text).replace("\n", "<br>")
            created = m.get("created_at", "")
            try:
                ts = datetime.fromisoformat(created).strftime("%b %d %H:%M")
            except Exception:
                ts = created

            is_me = (sender_id == userid)

            if is_me:
                msgs_html += f"""
                <div class="msg-row me">
                  <div class="bubble me-bubble">{text}</div>
                  <div class="ts">{ts}</div>
                </div>
                """
            else:
                msgs_html += f"""
                <div class="msg-row them">
                  <div class="sender">{sender_username}</div>
                  <div class="bubble them-bubble">{text}</div>
                  <div class="ts">{ts}</div>
                </div>
                """

        chat_frame = f"""
        <!doctype html>
        <html>
        <head>
          <meta charset="utf-8"/>
          <meta name="viewport" content="width=device-width, initial-scale=1"/>
          <style>
            body {{ font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial; margin:0; padding:8px; background:transparent; }}
            .chat-wrap {{ max-height: 330px; overflow-y: auto; padding:2px; border-radius:8px; background:#fff; border:1px solid #eaeaea; }}
            .msg-row {{ margin-bottom:10px; clear:both; }}
            .sender {{ font-weight:600; margin-bottom:4px; }}
            .bubble {{ display:inline-block; padding:8px 12px; border-radius:12px; max-width:78%; word-wrap:break-word; white-space:pre-wrap; }}
            .me {{ text-align:right; }}
            .me-bubble {{ background:#dcf8c6; color:#000; border-bottom-right-radius:4px; }}
            .them-bubble {{ background:#f1f1f1; color:#000; border-bottom-left-radius:4px; }}
            .ts {{ font-size:10px; color:#666; margin-top:4px; }}
          </style>
        </head>
        <body>
          <div class="chat-wrap" id="chatWrap">
            {msgs_html}
          </div>
          <script>
            const chat = document.getElementById('chatWrap');
            if (chat) {{ chat.scrollTop = chat.scrollHeight; }}
          </script>
        </body>
        </html>
        """

        components.html(chat_frame, height=330)

        st.markdown("---")

        # ----- Send area (native) -----
        st.text_area("Message", value=st.session_state["admin_message_input"], key="admin_message_input", height=90)
        if st.button("Send Message", key=f"sendmsg_{selected}"):
            text = st.session_state.get("admin_message_input", "").strip()
            if not text:
                st.warning("Please type a message")
            else:
                r = post_message(selected, text)
                if r and getattr(r, "status_code", None) in (200,201):
                    st.success("Sent")
                    # clear input and refresh messages
                    # st.session_state["admin_message_input"] = ""
                    fetch_messages.clear()
                    fetch_conversations.clear()
                    del st.session_state["admin_message_input"]
                    st.rerun()
                else:
                    st.error("Failed to send message")
