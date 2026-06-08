import streamlit as st
import json
import os
from datetime import datetime
import google.generativeai

# --- CONFIGURATION ---
st.set_page_config(page_title="Catholic Mind & Heart", page_icon="🌿", layout="centered")

def get_file_path(username):
    safe_name = "".join(c for c in username if c.isalnum() or c in (' ', '_')).rstrip()
    return f"{safe_name}_journal.json"

def load_data(username):
    file_path = get_file_path(username)
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_entry(username, entry):
    data = load_data(username)
    data.insert(0, entry)
    with open(get_file_path(username), 'w') as f:
        json.dump(data, f, indent=4)

def delete_single_entry(username, entry_id):
    data = load_data(username)
    data = [e for e in data if e.get('id') != entry_id]
    with open(get_file_path(username), 'w') as f:
        json.dump(data, f, indent=4)

def check_crisis(text):
    keywords = ['take my life', 'hurt myself', 'give up completely']
    return any(keyword in text.lower() for keyword in keywords) if text else False

def whimsical_divider():
    st.markdown("<div style='text-align: center; letter-spacing: 15px; font-size: 1.2rem; color: #8FBC8F; margin-top: 15px; margin-bottom: 15px;'>🌿 ✨ 🦋 ✨ 🌿</div>", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.markdown("<h1 style='text-align: center; font-size: 5rem; margin-bottom: -20px;'>🕊️</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<h2 style='text-align: center; color: #556B2F; font-family: cursive; margin-bottom: 20px;'>Sanctuary Garden</h2>", unsafe_allow_html=True)

username = st.sidebar.text_input("Enter your unique Journal Name", value="MyJournal")
if not username.strip(): st.stop()

page = st.sidebar.radio("Navigate your path:", ["🌿 The Daily Examen", "🦋 Custody of the Mind", "📖 Seek Scripture", "🌱 Growth Dashboard", "🌷 SOS Grounding"])

api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

# --- PAGES ---
if page == "🌿 The Daily Examen":
    st.markdown("<h1 style='color: #4A7023;'>The Daily Examen 🌿</h1>", unsafe_allow_html=True)
    with st.form("examen_form", clear_on_submit=True):
        gratitude = st.text_area("What are you most grateful for today?")
        review = st.text_area("Where did you feel God's presence today?")
        sorrow = st.text_area("What do you need to bring to His mercy?")
        grace = st.text_area("What grace do you need for tomorrow?")
        submitted = st.form_submit_button("Seal & Save Locally 🪴")
        if submitted:
            new_entry = {"id": str(datetime.now().timestamp()), "date": datetime.now().strftime("%B %d, %Y - %I:%M %p"), "type": "Examen", "text": f"{gratitude}\n{review}\n{sorrow}\n{grace}"}
            save_entry(username, new_entry)
            st.success("Saved! 🌿")

    if st.button("✨ Generate Catholic Devotional"):
        if not api_key: st.warning("Enter API Key first.")
        else:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"You are a Catholic guide. Reflect on this Examen: {load_data(username)[0]['text']}")
            st.info(response.text)

elif page == "🦋 Custody of the Mind":
    st.markdown("<h1 style='color: #4682B4;'>Custody of the Mind 🦋</h1>", unsafe_allow_html=True)
    with st.form("reframe_form", clear_on_submit=True):
        trigger = st.text_input("Trigger?")
        auto_thought = st.text_area("Negative thought?")
        reframed = st.text_area("Reframed thought?")
        if st.form_submit_button("Save"):
            save_entry(username, {"id": str(datetime.now().timestamp()), "date": datetime.now().strftime("%c"), "type": "Cognitive Reframe", "text": f"{trigger}\n{auto_thought}\n{reframed}"})
            st.success("Saved. 🦋")

elif page == "📖 Seek Scripture":
    st.markdown("<h1 style='color: #8B4513;'>Word of Light 📖</h1>", unsafe_allow_html=True)
    feeling = st.text_input("How are you feeling?")
    if st.button("Find Verse"):
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"Provide one Catholic Bible verse (RSV-CE) for the feeling: {feeling}. Follow with 2 sentences of comfort.")
        st.success(response.text)

elif page == "🌱 Growth Dashboard":
    st.markdown(f"<h1 style='color: #2E8B57;'>{username}'s Garden 🌱</h1>", unsafe_allow_html=True)
    for entry in load_data(username):
        with st.expander(f"{entry['type']} - {entry['date']}"):
            st.write(entry['text'])
            if st.button("🗑️ Delete", key=entry['id']):
                delete_single_entry(username, entry['id'])
                st.rerun()

elif page == "🌷 SOS Grounding":
    st.markdown("<h1 style='color: #C71585;'>SOS: Anchorage 🌷</h1>", unsafe_allow_html=True)
    st.error("🚨 Call 988 if in danger.")
    st.markdown("### The Jesus Prayer\n**Lord Jesus Christ, Son of God, have mercy on me, a sinner.**")
    st.markdown("### The Memorare\n> Remember, O most gracious Virgin Mary...")
