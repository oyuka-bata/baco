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
    {
        "title": "Which Hogwarts house feels most like you?",
        "options": [
            {"label": "Gryffindor — bold, loud, main character",       "w": {"energy": 0.85, "valence": 0.70, "genres": {"Rock": 3, "Pop": 2, "Hip-Hop": 2}, "moods": {"Energetic": 3, "Happy": 1}}},
            {"label": "Slytherin — cool, sharp, low-key powerful",     "w": {"energy": 0.70, "valence": 0.30, "genres": {"Hip-Hop": 3, "Electronic": 3, "R&B": 2}, "moods": {"Energetic": 2, "Chill": 1}}},
            {"label": "Ravenclaw — thoughtful, curious, in your head", "w": {"energy": 0.30, "valence": 0.40, "genres": {"Indie": 3, "Classical": 3, "Jazz": 2}, "moods": {"Focus": 3, "Chill": 1}}},
            {"label": "Hufflepuff — warm, soft, comfort-food coded",   "w": {"energy": 0.45, "valence": 0.85, "genres": {"Pop": 2, "Indie": 2, "R&B": 2}, "moods": {"Happy": 3, "Chill": 2}}},
        ],
    },
    {
        "title": "Pick your current aesthetic",
        "options": [
            {"label": "Cottagecore — sundress, sourdough, fields",        "w": {"energy": 0.35, "valence": 0.75, "genres": {"Indie": 3, "Classical": 2, "Pop": 1}, "moods": {"Happy": 2, "Chill": 2}}},
            {"label": "Dark academia — tweed, candles, old library",      "w": {"energy": 0.30, "valence": 0.30, "genres": {"Classical": 3, "Indie": 2, "Jazz": 2}, "moods": {"Focus": 3, "Sad": 1}}},
            {"label": "Y2K — glitter, low-rise, butterfly clips",         "w": {"energy": 0.85, "valence": 0.85, "genres": {"Pop": 3, "Electronic": 2, "Hip-Hop": 2}, "moods": {"Energetic": 2, "Happy": 3}}},
            {"label": "Clean girl — slicked back, gold hoops, matcha",    "w": {"energy": 0.45, "valence": 0.65, "genres": {"Pop": 2, "R&B": 2, "Indie": 2}, "moods": {"Chill": 3, "Happy": 1}}},
        ],
    },
    {
        "title": "Pick a season that feels like you right now",
        "options": [
            {"label": "Spring — new crush, green, light",         "w": {"energy": 0.55, "valence": 0.85, "genres": {"Pop": 2, "Indie": 2}, "moods": {"Happy": 3}}},
            {"label": "Summer — sunburn, party, no plans",        "w": {"energy": 0.85, "valence": 0.80, "genres": {"Pop": 2, "Hip-Hop": 2, "Electronic": 2}, "moods": {"Energetic": 2, "Happy": 2}}},
            {"label": "Autumn — sweater weather, long walks",     "w": {"energy": 0.45, "valence": 0.40, "genres": {"Indie": 3, "R&B": 2, "Jazz": 1}, "moods": {"Chill": 3, "Sad": 1}}},
            {"label": "Winter — quiet, candle, big feelings",     "w": {"energy": 0.20, "valence": 0.20, "genres": {"Classical": 3, "Indie": 2, "R&B": 1}, "moods": {"Sad": 2, "Focus": 2}}},
        ],
    },
    {
        "title": "If you had to move tomorrow…",
        "options": [
            {"label": "Paris — slow mornings, cafés, jazz",            "w": {"energy": 0.40, "valence": 0.60, "genres": {"Jazz": 3, "Indie": 2, "Classical": 2}, "moods": {"Chill": 3, "Happy": 1}}},
            {"label": "Tokyo — neon, vending machines, 7-Elevens",     "w": {"energy": 0.85, "valence": 0.65, "genres": {"Electronic": 3, "Pop": 2, "Hip-Hop": 2}, "moods": {"Energetic": 3}}},
            {"label": "New York — bagels, basslines, never sleeps",    "w": {"energy": 0.80, "valence": 0.55, "genres": {"Hip-Hop": 3, "R&B": 2, "Rock": 1}, "moods": {"Energetic": 2, "Chill": 1}}},
            {"label": "Reykjavik — cold air, glaciers, Northern Lights","w": {"energy": 0.25, "valence": 0.30, "genres": {"Indie": 2, "Classical": 3, "Electronic": 1}, "moods": {"Focus": 2, "Sad": 2}}},
        ],
    },
    {
        "title": "Your dream Saturday night looks like…",
        "options": [
            {"label": "Out dancing — with friends, loud, sweaty",      "w": {"energy": 0.90, "valence": 0.75, "genres": {"Electronic": 3, "Hip-Hop": 2, "Pop": 2}, "moods": {"Energetic": 3}}},
            {"label": "Cozy at home — movie, blanket, snacks",         "w": {"energy": 0.35, "valence": 0.55, "genres": {"Indie": 2, "R&B": 2, "Pop": 1}, "moods": {"Chill": 3}}},
            {"label": "Late-night drive — window down, deep playlist", "w": {"energy": 0.55, "valence": 0.30, "genres": {"R&B": 2, "Indie": 2, "Hip-Hop": 1, "Pop": 1}, "moods": {"Chill": 2, "Sad": 1}}},
            {"label": "Studying / focused — headphones in",            "w": {"energy": 0.20, "valence": 0.35, "genres": {"Classical": 3, "Jazz": 2, "Electronic": 1}, "moods": {"Focus": 3}}},
        ],
    },
    {
        "title": "Pick your drink",
        "options": [
            {"label": "Iced coffee — caffeinated and ready",   "w": {"energy": 0.75, "valence": 0.65, "genres": {"Pop": 2, "Hip-Hop": 2}, "moods": {"Energetic": 2, "Happy": 1}}},
            {"label": "Hot tea — slow morning, gentle",         "w": {"energy": 0.25, "valence": 0.55, "genres": {"Indie": 2, "Classical": 2, "Jazz": 1}, "moods": {"Chill": 2, "Focus": 1}}},
            {"label": "Cocktail — it's the weekend",            "w": {"energy": 0.85, "valence": 0.70, "genres": {"Electronic": 3, "Pop": 2, "R&B": 1}, "moods": {"Energetic": 2}}},
            {"label": "Just water — locked in, focused",        "w": {"energy": 0.20, "valence": 0.40, "genres": {"Classical": 2, "Jazz": 2, "Indie": 1}, "moods": {"Focus": 3}}},
        ],
    },
    {
        "title": "Your texting style is…",
        "options": [
            {"label": "lol same all lowercase — vibes only",                  "w": {"energy": 0.55, "valence": 0.65, "genres": {"Indie": 2, "Pop": 2}, "moods": {"Chill": 2, "Happy": 1}}},
            {"label": "Perfect grammar. With periods.",                       "w": {"energy": 0.30, "valence": 0.45, "genres": {"Classical": 2, "Jazz": 2, "Indie": 1}, "moods": {"Focus": 3}}},
            {"label": "Voice memos, mostly — talking is faster",              "w": {"energy": 0.85, "valence": 0.75, "genres": {"Hip-Hop": 3, "Pop": 2, "Rock": 1}, "moods": {"Energetic": 3, "Happy": 1}}},
            {"label": "17-paragraph essays — feelings need full context",     "w": {"energy": 0.45, "valence": 0.30, "genres": {"Indie": 3, "R&B": 2, "Classical": 1}, "moods": {"Sad": 2, "Chill": 1}}},
        ],
    },
    {
        "title": "What is the weather inside your head right now?",
        "options": [
            {"label": "Sunny — everything's clicking",     "w": {"energy": 0.75, "valence": 0.95, "genres": {"Pop": 2, "Indie": 1}, "moods": {"Happy": 3}}},
            {"label": "Cloudy — vibes, but soft",          "w": {"energy": 0.45, "valence": 0.50, "genres": {"Indie": 2, "R&B": 2}, "moods": {"Chill": 3}}},
            {"label": "Stormy — big mood, lots of energy", "w": {"energy": 0.90, "valence": 0.40, "genres": {"Rock": 3, "Hip-Hop": 2, "Electronic": 1}, "moods": {"Energetic": 3}}},
            {"label": "Rainy — in my feelings",            "w": {"energy": 0.30, "valence": 0.15, "genres": {"Indie": 2, "R&B": 2, "Classical": 1}, "moods": {"Sad": 3}}},
        ],
    },
    {
        "title": "At a party, you're usually…",
        "options": [
            {"label": "On the dance floor — losing earrings to the rhythm",       "w": {"energy": 0.95, "valence": 0.85, "genres": {"Electronic": 3, "Pop": 2, "Hip-Hop": 2}, "moods": {"Energetic": 3, "Happy": 2}}},
            {"label": "Deep in the kitchen — life-changing chats with strangers", "w": {"energy": 0.40, "valence": 0.55, "genres": {"Indie": 2, "R&B": 2, "Jazz": 2}, "moods": {"Chill": 3}}},
            {"label": "On aux duty — DJ unprovoked, no skips allowed",            "w": {"energy": 0.75, "valence": 0.70, "genres": {"Hip-Hop": 3, "Electronic": 2, "Pop": 2}, "moods": {"Energetic": 2, "Happy": 1}}},
            {"label": "Already left — bed always wins, no notes",                 "w": {"energy": 0.25, "valence": 0.35, "genres": {"Indie": 2, "Classical": 2, "R&B": 1}, "moods": {"Chill": 1, "Sad": 2, "Focus": 1}}},
        ],
    },
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
