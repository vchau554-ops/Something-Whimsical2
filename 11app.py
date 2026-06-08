import streamlit as st
import json
import os
from datetime import datetime
from google import genai
from google.genai import types

# --- CONFIGURATION & PROFILES ---
st.set_page_config(page_title="Catholic Mind & Heart", page_icon="🌿", layout="centered")

def get_file_path(username):
    # Creates a unique, safe file name for each user
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
    # Keep everything EXCEPT the one they clicked delete on
    data = [e for e in data if e.get('id') != entry_id]
    with open(get_file_path(username), 'w') as f:
        json.dump(data, f, indent=4)

def check_crisis(text):
    keywords = ['take my life', 'hurt myself', 'give up completely']
    if not text:
        return False
    return any(keyword in text.lower() for keyword in keywords)

def whimsical_divider():
    st.markdown("<div style='text-align: center; letter-spacing: 15px; font-size: 1.2rem; color: #8FBC8F; margin-top: 15px; margin-bottom: 15px;'>🌿 ✨ 🦋 ✨ 🌿</div>", unsafe_allow_html=True)

# --- SIDEBAR: PROFILES & NAVIGATION ---
st.sidebar.markdown("<h1 style='text-align: center; font-size: 5rem; margin-bottom: -20px;'>🕊️</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<h2 style='text-align: center; color: #556B2F; font-family: cursive; margin-bottom: 20px;'>Sanctuary Garden</h2>", unsafe_allow_html=True)

st.sidebar.markdown("**📖 Who is journeying today?**")
username = st.sidebar.text_input("Enter your unique Journal Name", value="MyJournal")

if not username.strip():
    st.warning("Please enter a Journal Name to begin.")
    st.stop() # Stops the app from loading until they enter a name

st.sidebar.markdown("<br>", unsafe_allow_html=True)
page = st.sidebar.radio("Navigate your path:", [
    "🌿 The Daily Examen", 
    "🦋 Custody of the Mind",
    "📖 Seek Scripture",
    "🌱 Growth Dashboard", 
    "🌷 SOS Grounding"
])

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("**✨ AI Spiritual Guide**")
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

st.sidebar.markdown("<br><br><p style='text-align: center; color: gray; font-size: 0.8rem;'>Growing gently... 🪴</p>", unsafe_allow_html=True)

# --- PAGE 1: THE IGNATIAN EXAMEN ---
if page == "🌿 The Daily Examen":
    st.markdown(f"<h1 style='color: #4A7023;'>The Daily Examen 🌿</h1>", unsafe_allow_html=True)
    st.markdown(f"*Welcome, {username}. This is a safe space to recognize God's presence in your day.*")
    
    with st.form("examen_form", clear_on_submit=True):
        st.markdown("**🌸 1. Presence & Gratitude**")
        gratitude = st.text_area("What are you most grateful for today?", height=68)
        
        st.markdown("**🍃 2. Review the Day**")
        review = st.text_area("Where did you feel God's presence today? Where did you feel distant?", height=100)
        
        st.markdown("**💧 3. Sorrow & Forgiveness**")
        sorrow = st.text_area("What thoughts or actions do you need to bring to His mercy?", height=68)
        
        st.markdown("**✨ 4. Grace for Tomorrow**")
        grace = st.text_area("What specific grace do you need from God for tomorrow?", height=68)
        
        submitted = st.form_submit_button("Seal & Save Locally 🪴")
        
        if submitted:
            combined_text = f"Gratitude: {gratitude}\nReview: {review}\nSorrow: {sorrow}\nGrace: {grace}"
            fields_have_text = any(field.strip() for field in [gratitude, review, sorrow, grace])
            
            if check_crisis(combined_text):
                st.error("⚠️ **You are not alone.** Please call or text **988** immediately.")
            elif not fields_have_text:
                st.warning("Please reflect on at least one step before saving.")
            else:
                new_entry = {
                    "id": str(datetime.now().timestamp()),
                    "date": datetime.now().strftime("%B %d, %Y - %I:%M %p"),
                    "type": "Examen",
                    "text": combined_text
                }
                save_entry(username, new_entry)
                st.success(f"Your Examen has been saved privately to {username}'s journal. 🌿")

    whimsical_divider()
    
    st.subheader("Seek Counsel 🕊️")
    if st.button("✨ Generate Catholic Devotional"):
        data = load_data(username)
        examens = [e for e in data if e.get('type') == 'Examen']
        
        if not api_key:
            st.warning("Please enter your Gemini API Key in the sidebar.")
        elif not examens:
            st.info("Please complete and save an Examen first.")
        else:
            with st.spinner("Reflecting on your entry... ✨"):
                try:
                    client = genai.Client(api_key=api_key)
                    latest_examen = examens[0]['text']
                    
                    sys_instruct = "You are a compassionate Catholic spiritual guide. Read the user's Examen. Write a comforting reflection (max 150 words). Provide a verse (RSV-CE) or Saint quote. Do not diagnose. Use rich Catholic terminology."
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=f"User's Examen:\n{latest_examen}",
                        config=types.GenerateContentConfig(
                            system_instruction=sys_instruct,
                            safety_settings=[
                                types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
                                types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE")
                            ]
                        )
                    )
                    st.info(response.text)
                except Exception as e:
                    st.error("We encountered an issue. Please check your API key.")

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🕊️ Read the Closing Prayer"):
        st.markdown("**A Prayer of Surrender and Renewal**\n\nHeavenly Father, source of all peace and boundless mercy, I come before You exactly as I am at the end of this day. You see the hidden movements of my heart, and You know the weight of the words I have poured into this journal.\n\nThank You for the quiet graces of today—the moments of light, the strength to endure, and the breath in my lungs. Even when the hours are heavy, I trust that Your love is holding me.\n\nLord, I surrender to You every anxiety, every rushing thought, and every burden I have recorded here. Where my mind has been clouded by fear, distortion, or the lies of the enemy, shine the light of Your truth. Help me to take every thought captive to Christ. Anchor my identity not in my fleeting emotions or my perceived failures, but in my eternal dignity as Your beloved child.\n\nFor the moments I have fallen short, lost my peace, or doubted Your goodness, I ask for Your gentle mercy. Protect my heart from despair and my mind from scrupulosity. Remind me always that Your grace builds upon my weakness.\n\nAs I close this journal and look toward tomorrow, grant me the specific graces I am most in need of. Give me custody of my mind, stillness in my soul, and the courage to pick up my cross with hope.\n\nMay I rest tonight safely in the shelter of Your wings.\n\nJesus, I trust in You.\n*Amen.*")

# --- PAGE 2: CUSTODY OF THE MIND ---
elif page == "🦋 Custody of the Mind":
    st.markdown("<h1 style='color: #4682B4;'>Custody of the Mind 🦋</h1>", unsafe_allow_html=True)
    
    with st.form("reframe_form", clear_on_submit=True):
        trigger = st.text_input("🌱 What triggered this feeling?")
        auto_thought = st.text_area("What is the automatic negative thought?", height=68)
        
        distortions = ["All-or-Nothing (Black & White)", "Catastrophizing", "Scrupulosity (Seeing mortal sin in weakness)"]
        distortion = st.selectbox("🕸️ Which mental filter is twisting your perspective?", distortions)
        
        anchors = ["St. Dymphna - 'Do not be anxious...'", "St. Francis de Sales - 'Have patience...'", "Romans 8:1 - 'No condemnation...'"]
        anchor = st.selectbox("⚓ Select a Spiritual Anchor", anchors)
        
        reframed = st.text_area("✨ Write the Reframed Thought", height=68)
        submitted_reframe = st.form_submit_button("Save Reframe Locally 🦋")
        
        if submitted_reframe:
            if check_crisis(auto_thought) or check_crisis(reframed):
                 st.error("⚠️ **Emergency:** Please call **988** immediately.")
            elif reframed.strip() and auto_thought.strip():
                new_entry = {
                    "id": str(datetime.now().timestamp()),
                    "date": datetime.now().strftime("%B %d, %Y - %I:%M %p"),
                    "type": "Cognitive Reframe",
                    "text": f"Trigger: {trigger}\nThought: {auto_thought}\nReframed: {reframed}"
                }
                save_entry(username, new_entry)
                st.success("Thought saved to your device. 🦋")
            else:
                st.warning("Please complete both thought boxes.")

# --- PAGE 3: SEEK SCRIPTURE ---
elif page == "📖 Seek Scripture":
    st.markdown("<h1 style='color: #8B4513;'>Word of Light 📖</h1>", unsafe_allow_html=True)
    st.markdown("*Your word is a lamp to my feet and a light to my path. (Psalm 119:105)*")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### How are you feeling right now?")
    feeling = st.text_input("Enter an emotion or struggle (e.g., anxious, lonely, overwhelmed by work, deeply grateful):")
    
    if st.button("✨ Find a Comforting Verse"):
        if not api_key:
            st.warning("Please enter your Gemini API Key in the sidebar first.")
        elif not feeling.strip():
            st.warning("Please enter a feeling to search for.")
        else:
            with st.spinner("Searching the Scriptures... 🕊️"):
                try:
                    client = genai.Client(api_key=api_key)
                    sys_instruct = "You are a comforting Catholic scriptural guide. The user will share a feeling. Reply with ONE relevant Catholic Bible verse (RSV-CE) formatted in bold. Follow the verse with a 2-3 sentence gentle, empathetic Catholic reflection. Do not preach, just comfort."
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=f"I am feeling: {feeling}",
                        config=types.GenerateContentConfig(
                            system_instruction=sys_instruct,
                            safety_settings=[
                                types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
                                types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE")
                            ]
                        )
                    )
                    st.success(response.text)
                except Exception as e:
                    st.error("We encountered an issue. Please check your API key.")

# --- PAGE 4: GROWTH DASHBOARD ---
elif page == "🌱 Growth Dashboard":
    st.markdown(f"<h1 style='color: #2E8B57;'>{username}'s Garden 🌱</h1>", unsafe_allow_html=True)
    data = load_data(username)
    
    if not data:
        st.info("Your garden is just beginning to grow. Complete an Examen to see your metrics. 🌿")
    else:
        total = len(data)
        reframes = len([e for e in data if e.get('type') == 'Cognitive Reframe'])
        examens = len([e for e in data if e.get('type') == 'Examen'])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Reflections ✨", total)
        col2.metric("Examens Completed 🌿", examens)
        col3.metric("Thoughts Reframed 🦋", reframes)
        
        whimsical_divider()
        st.subheader("Your Entries 🪴")
        
        for entry in data:
            with st.expander(f"{entry.get('type', 'Entry')} - {entry['date']}"):
                st.write(entry['text'])
                if st.button("🗑️ Delete this specific entry", key=f"del_{entry['id']}"):
                    delete_single_entry(username, entry['id'])
                    st.rerun() 
                
        whimsical_divider()
        st.subheader("Garden Maintenance 🍂")
        if st.button(f"⚠️ Clear ALL of {username}'s Data"):
            with open(get_file_path(username), 'w') as f:
                json.dump([], f)
            st.rerun()

# --- PAGE 5: SOS GROUNDING ---
elif page == "🌷 SOS Grounding":
    st.markdown("<h1 style='color: #C71585;'>SOS: Anchorage 🌷</h1>", unsafe_allow_html=True)
    st.error("🚨 **If you are in immediate danger, call 988 or 911.**")
    
    st.markdown("### The Jesus Prayer 💧")
    st.markdown("Breathe in slowly through your nose for 4 seconds, and pray in your mind:")
    st.success("**Lord Jesus Christ, Son of God...**")
    st.markdown("Exhale slowly through your mouth for 6 seconds, and pray:")
    st.success("**...have mercy on me, a sinner.**")
    
    whimsical_divider()
    
    st.markdown("### The Memorare 🌹")
    st.markdown("> Remember, O most gracious Virgin Mary, that never was it known that anyone who fled to thy protection, implored thy help, or sought thine intercession was left unaided. \n> \n> Inspired by this confidence, I fly unto thee, O Virgin of virgins, my mother; to thee do I come, before thee I stand, sinful and sorrowful. O Mother of the Word Incarnate, despise not my petitions, but in thy mercy hear and answer me. Amen.")