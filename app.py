import streamlit as st
import pandas as pd
import sqlite3
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# --- 1. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="BACO Station", page_icon="🎵", layout="centered")

# --- 2. DATA LOADING & DATABASE PIPELINE ---
@st.cache_data
def load_and_setup_db():
    CSV_URL = "https://huggingface.co/datasets/sfiore/spotify-tracks-dataset/resolve/main/dataset.csv"
    df = pd.read_csv(CSV_URL)
    df.columns = [c.lower().strip() for c in df.columns]
    
    wanted = ["track_name", "artists", "track_genre", "energy", "valence", "popularity", "danceability", "tempo"]
    df = df[[c for c in wanted if c in df.columns]].dropna()
    df = df.rename(columns={"track_name": "name", "artists": "artist", "track_genre": "genre"})

    # Mood Logic
    def assign_mood(row):
        e, v = row["energy"], row["valence"]
        if e >= 0.78 and v >= 0.78: return "Energetic"
        if e >= 0.65 and v >= 0.55: return "Happy"
        if e < 0.40 and v < 0.40: return "Sad"
        if e < 0.40: return "Focus"
        return "Chill"
    
    df["mood"] = df.apply(assign_mood, axis=1)
    return df

songs = load_and_setup_db()

# --- 3. THE VIBE QUIZ DATA ---
quiz = [
    {"title": "Which Hogwarts house feels most like you?", "options": [
        {"label": "Gryffindor — bold, loud, main character", "w": {"energy": 0.85, "valence": 0.70, "genres": {"Rock": 3}, "moods": {"Energetic": 3}}},
        {"label": "Slytherin — cool, sharp, powerful", "w": {"energy": 0.70, "valence": 0.30, "genres": {"Electronic": 3}, "moods": {"Energetic": 2}}},
        {"label": "Ravenclaw — thoughtful, curious", "w": {"energy": 0.30, "valence": 0.40, "genres": {"Classical": 3}, "moods": {"Focus": 3}}},
        {"label": "Hufflepuff — warm, soft, comfort", "w": {"energy": 0.45, "valence": 0.85, "genres": {"Pop": 2}, "moods": {"Happy": 3}}},
    ]},
    {"title": "Pick your current aesthetic", "options": [
        {"label": "Cottagecore — fields and flowers", "w": {"energy": 0.35, "valence": 0.75, "genres": {"Indie": 3}, "moods": {"Chill": 3}}},
        {"label": "Dark academia — old libraries", "w": {"energy": 0.30, "valence": 0.30, "genres": {"Classical": 3}, "moods": {"Focus": 3}}},
        {"label": "Y2K — glitter and party", "w": {"energy": 0.85, "valence": 0.85, "genres": {"Pop": 3}, "moods": {"Happy": 3}}},
        {"label": "Clean girl — matcha and gold hoops", "w": {"energy": 0.45, "valence": 0.65, "genres": {"R&B": 2}, "moods": {"Chill": 3}}},
    ]}
]

# --- 4. HELPER FUNCTIONS ---
def fetch_song_meta(name, artist):
    try:
        resp = requests.get("https://itunes.apple.com/search", params={"term": f"{name} {artist}", "limit": 1})
        results = resp.json().get("results", [])
        if results:
            return {"cover": results[0].get("artworkUrl100", "").replace("100x100bb", "600x600bb"), "preview": results[0].get("previewUrl")}
    except: return None

# --- 5. STREAMLIT UI ---
st.markdown('<div style="background-color:#1DB954; padding:20px; border-radius:10px; color:white;"><h1>BACO Station</h1><p>Spotify Vibe Recommender</p></div>', unsafe_allow_html=True)

name = st.text_input("What is your name?", placeholder="Type here...")

user_answers = {}
for i, q in enumerate(quiz):
    choice = st.selectbox(q['title'], ["Select an option..."] + [opt['label'] for opt in q['options']], key=f"q{i}")
    if choice != "Select an option...":
        user_answers[i] = [opt['label'] for opt in q['options']].index(choice)

if st.button("Get My Vibe", type="primary"):
    if not user_answers:
        st.warning("Please answer at least one question!")
    else:
        # Scoring Logic
        energy_target = sum([quiz[i]['options'][ans]['w']['energy'] for i, ans in user_answers.items()]) / len(user_answers)
        valence_target = sum([quiz[i]['options'][ans]['w']['valence'] for i, ans in user_answers.items()]) / len(user_answers)
        
        songs['score'] = -(abs(songs['energy'] - energy_target) + abs(songs['valence'] - valence_target))
        top_song = songs.sort_values('score', ascending=False).iloc[0]
        
        st.balloons()
        st.subheader(f"The vibe for {name} is set!")
        
        col1, col2 = st.columns([1, 2])
        meta = fetch_song_meta(top_song['name'], top_song['artist'])
        
        with col1:
            if meta: st.image(meta['cover'])
        with col2:
            st.metric("Top Pick", top_song['name'])
            st.write(f"**Artist:** {top_song['artist']}")
            st.write(f"**Genre:** {top_song['genre']}")
            if meta and meta['preview']: st.audio(meta['preview'])

        st.write("### Your Vibe Playlist")
        st.dataframe(songs.sort_values('score', ascending=False).head(10)[['name', 'artist', 'genre', 'mood']])

# --- 6. OPTIONAL ANALYTICS ---
with st.expander("View Data Analytics (For Professor)"):
    st.write("Energy vs Valence Distribution")
    fig = px.scatter(songs.sample(1000), x="energy", y="valence", color="mood")
    st.plotly_chart(fig)
