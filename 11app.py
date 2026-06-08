import streamlit as st
import json
import os
from datetime import datetime
import google.generativeai as genai

# --- CONFIGURATION ---
st.set_page_config(page_title="Sanctuary", page_icon="🌿")

def load_data(username):
    filename = f"{username}.json"
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

def save_entry(username, entry):
    filename = f"{username}.json"
    data = load_data(username)
    data.insert(0, entry)
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# --- APP UI ---
st.sidebar.title("🕊️ Sanctuary")
user = st.sidebar.text_input("Name", value="Guest")
page = st.sidebar.radio("Go to:", ["Examen", "Scripture", "Dashboard"])
api_key = st.sidebar.text_input("API Key", type="password")

if page == "Examen":
    text = st.text_area("Your reflections:")
    if st.button("Save"):
        save_entry(user, {"date": str(datetime.now()), "text": text})
        st.success("Saved.")
    if st.button("AI Reflection"):
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        st.write(model.generate_content(f"Reflect: {text}").text)

elif page == "Scripture":
    feeling = st.text_input("How are you feeling?")
    if st.button("Get Verse"):
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        st.write(model.generate_content(f"Bible verse for: {feeling}").text)

elif page == "Dashboard":
    st.write(load_data(user))
