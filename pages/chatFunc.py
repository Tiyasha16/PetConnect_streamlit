import streamlit as st
import requests
import streamlit.components.v1 as components
import html
from datetime import datetime

from app import DJANGO_API_URL

START_CHAT_API = f"{DJANGO_API_URL}/api/chats/conversations/find-or-create/"
CHAT_MESSAGES_API = f"{DJANGO_API_URL}/api/chats/conversations/{{conversation_id}}/messages/"

user = st.session_state["user"]
userid = user.get('id', '')

# Custom CSS for gradient background
st.markdown("""
<style>
    .stApp {
        background: #cf88a6;
        background: radial-gradient(circle, rgba(207, 136, 166, 1) 0%, rgba(148, 187, 233, 1) 100%);
    }
</style>
""", unsafe_allow_html=True)

#  chat features
def open_chat_for_pet(pet):
    """
    Ensure conversation exists and open chat modal.
    pet: dict with 'pet_id', 'name', 'image' etc.
    """
    token = st.session_state.get("access_token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    r = requests.post(START_CHAT_API, json={"pet_id": pet["pet_id"]}, headers=headers)
    if r.status_code not in (200,201):
        st.error("Failed to start chat")
        return None

    conv = r.json()
    conv_id = conv["conv_id"]
    st.session_state.current_conversation = conv_id
    st.session_state.chat_pet = pet
    st.session_state.show_chat = True

def fetch_messages(conv_id):
    token = st.session_state.get("access_token")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = CHAT_MESSAGES_API.format(conversation_id=conv_id)
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        if len(r.json()) > 0:
            return r.json()
    return []

def send_message(conv_id, text):
    token = st.session_state.get("access_token")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = CHAT_MESSAGES_API.format(conversation_id=conv_id)
    r = requests.post(url, json={"text": text}, headers=headers)
    return r

# --- in your pet card (where you currently show details) add a button:
# Example usage:
# if st.button("Chat with admin", key=f"chat_{pet['pet_id']}"):
#     open_chat_for_pet(pet)

@st.dialog("Chat Dialog")
def render_chat_popup():
    # only render if explicitly requested (optional guard)
    if not st.session_state.get("show_chat"):
        return

    conv_id = st.session_state.get("current_conversation")
    pet = st.session_state.get("chat_pet", {})

    # --- Guard if no conversation ---
    if not conv_id:
        st.error("No conversation selected.")
        if st.button("Close Chat", key="chat_close_no_conv"):
            st.session_state.show_chat = False
            st.rerun()
        return

    # --- Header: pet info + close button ---
    st.subheader(f"Chat about: {pet.get('name', 'Pet')}")

    st.divider()

    # --- Messages area (scrollable look) ---
    try:
        messages = fetch_messages(conv_id) or []
    except Exception as e:
        st.error(f"Failed to load messages: {e}")
        messages = []

    # Use a container so we can refresh the messages area independently if needed
    msg_container = st.container()
    chat_html = ""
    # Render messages in chronological order
    with msg_container:
        if not messages:
            st.info("No messages yet. Start the conversation!")
        else:
            # Build inner HTML for messages (escaped)
            msgs_html = ""
            for m in messages:
                sender_id = m.get("sender").get("id")
                sender_email = html.escape(str(m.get("sender").get("user_name", "User")))
                raw_text = m.get("text", "") or ""
                text = html.escape(raw_text).replace("\n", "<br>")  # preserve newlines
                created = m.get("created_at", "")
                try:
                    ts = datetime.fromisoformat(created).strftime("%b %d %H:%M")
                except Exception:
                    ts = created

                is_me = (sender_id == userid)
                print(userid)
                print(sender_id)
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
                    <div class="sender">{sender_email}</div>
                    <div class="bubble them-bubble">{text}</div>
                    <div class="ts">{ts}</div>
                    </div>
                    """

            # Wrap in a full HTML doc for the iframe
            chat_frame = f"""
            <!doctype html>
            <html>
            <head>
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1"/>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial; margin:0; padding:10px; background:transparent; }}
                .chat-wrap {{ max-height: 420px; overflow-y: auto; padding:6px 6px; }}
                .msg-row {{ margin-bottom:10px; display:block; clear:both; }}
                .msg-row .sender {{ font-weight:600; margin-bottom:4px; }}
                .bubble {{ display:inline-block; padding:10px 12px; border-radius:12px; max-width:78%; word-wrap:break-word; white-space:pre-wrap; }}
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
                // Auto-scroll to bottom
                const chat = document.getElementById('chatWrap');
                if (chat) {{
                chat.scrollTop = chat.scrollHeight;
                }}
            </script>
            </body>
            </html>
            """

            # render inside an iframe via components.html
            # height can be tuned (e.g., 380, 400)
            components.html(chat_frame, height=420)

    # st.divider()

    # --- Send area ---
    if "chat_input" not in st.session_state:
        st.session_state["chat_input"] = ""

    st.text_area("Message", value=st.session_state["chat_input"], key="chat_input", height=90)

    send_col, refresh_col = st.columns([0.8, 0.2])
    with refresh_col:
        if st.button("⟳", key="chat_refresh"):
            # clear cached messages if you used caching, then rerun to refresh
            try:
                fetch_messages.clear()
            except Exception:
                pass
            st.rerun()

    with send_col:
        if st.button("Send", key="chat_send"):
            text = st.session_state.get("chat_input", "").strip()
            if not text:
                st.warning("Please enter a message before sending.")
            else:
                # send the message via your helper
                try:
                    resp = send_message(conv_id, text)
                    # adapt to your helper's return value
                    if resp is None:
                        st.error("Network error while sending message.")
                    elif getattr(resp, "status_code", None) in (200, 201):
                        st.success("Message sent.")
                        # clear input, clear message cache and rerun to show new message
                        # del st.session_state["chat_input"]
                        # st.session_state["chat_input"] = ""
                        st.session_state["msg_refresh"] = True
                        try:
                            fetch_messages.clear()
                        except Exception:
                            pass
                        st.rerun()
                    else:
                        # show response text when available
                        try:
                            err = resp.json()
                        except Exception:
                            err = getattr(resp, "text", str(resp))
                        st.error(f"Failed to send message: {err}")
                except Exception as e:
                    st.error(f"Send failed: {e}")