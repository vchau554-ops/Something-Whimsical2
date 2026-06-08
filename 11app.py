import streamlit as st
import json
import os
from datetime import datetime
import google.generativeai as genai

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

# --- SIDEBAR ---
st.sidebar.title("🕊️ Sanctuary Garden")
username = st.sidebar.text_input("Enter your Journal Name", value="MyJournal")
if not username.strip(): st.stop()

page = st.sidebar.radio("Navigation:", ["🌿 Examen", "🦋 Custody", "📖 Scripture", "🌱 Dashboard", "🌷 SOS"])
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

# --- PAGES ---
if page == "🌿 Examen":
    st.header("Daily Examen")
    with st.form("examen"):
        text = st.text_area("Reflect on your day:")
        if st.form_submit_button("Save"):
            save_entry(username, {"id": str(datetime.now().timestamp()), "date": datetime.now().strftime("%c"), "type": "Examen", "text": text})
            st.success("Saved!")
    if st.button("Generate Devotional"):
        if not api_key: st.warning("Enter API Key")
        else:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            res = model.generate_content(f"Reflect on this: {load_data(username)[0]['text']}")
            st.info(res.text)

elif page == "📖 Scripture":
    st.header("Seek Scripture")
    feeling = st.text_input("How are you feeling?")
    if st.button("Find Verse"):
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        res = model.generate_content(f"Provide a Catholic Bible verse for: {feeling}")
        st.success(res.text)

elif page == "🌱 Dashboard":
    st.header("Garden")
    for entry in load_data(username):
        with st.expander(f"{entry['type']} - {entry['date']}"):
            st.write(entry['text'])
            if st.button("Delete", key=entry['id']):
                delete_single_entry(username, entry['id'])
                st.rerun()

elif page == "🌷 SOS":
    st.error("🚨 Call 988 if in danger.")
    st.markdown("### The Jesus Prayer\n**Lord Jesus Christ, Son of God, have mercy on me, a sinner.**")
