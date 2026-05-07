import streamlit as st
import pandas as pd
import sqlite3
import requests
from pathlib import Path

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="BACO Station",
    page_icon="🎵",
    layout="centered"
)

# =========================================================
# STYLING
# =========================================================

st.markdown("""
<style>
.main {
    background-color: #0f1117;
    color: white;
}

.stButton>button {
    background: linear-gradient(90deg,#1db954,#1ed760);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.7rem 1.2rem;
    font-weight: bold;
}

.song-card {
    background: #181a22;
    padding: 18px;
    border-radius: 16px;
    margin-bottom: 16px;
    border: 1px solid #2a2f3a;
}

.persona-card {
    background: linear-gradient(135deg,#163826 0%,#1a2030 60%,#2b1d3a 100%);
    padding: 22px;
    border-radius: 18px;
    margin-bottom: 18px;
}

.badge {
    display:inline-block;
    padding:6px 12px;
    border-radius:999px;
    margin:4px;
    font-size:0.8rem;
    background:#232733;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# DATA LOADING
# =========================================================

DB_NAME = "spotify_music.db"
CSV_URL = "https://huggingface.co/datasets/sfiore/spotify-tracks-dataset/resolve/main/dataset.csv"

@st.cache_data
def load_data():

    songs = pd.read_csv(CSV_URL)

    songs.columns = [c.lower().strip() for c in songs.columns]

    wanted_columns = [
        "track_name",
        "artists",
        "track_genre",
        "danceability",
        "energy",
        "valence",
        "tempo",
        "acousticness",
        "instrumentalness",
        "speechiness",
        "liveness",
        "popularity"
    ]

    existing_columns = [c for c in wanted_columns if c in songs.columns]

    songs = songs[existing_columns].dropna()

    conn = sqlite3.connect(DB_NAME)

    songs.to_sql(
        "spotify_tracks",
        conn,
        if_exists="replace",
        index=False
    )

    songs = pd.read_sql_query(
        "SELECT * FROM spotify_tracks LIMIT 50000",
        conn
    )

    songs = songs.rename(columns={
        "track_name": "name",
        "artists": "artist",
        "track_genre": "genre"
    })

    return songs

songs = load_data()

# =========================================================
# MOOD ASSIGNMENT
# =========================================================

def assign_mood_to_song(row):

    e = row["energy"]
    v = row["valence"]

    if e >= 0.78 and v >= 0.78:
        return "Energetic"

    if e >= 0.65 and v >= 0.55:
        return "Happy"

    if e >= 0.65 and v < 0.55:
        return "Energetic"

    if e < 0.40 and v < 0.40:
        return "Sad"

    if e < 0.40:
        return "Focus"

    if v < 0.40:
        return "Sad"

    if e >= 0.45 and v >= 0.65:
        return "Chill"

    if e < 0.45 and v >= 0.55:
        return "Happy"

    return "Chill"

songs["mood"] = songs.apply(assign_mood_to_song, axis=1)

# =========================================================
# QUIZ DATA
# =========================================================

quiz = [
    {
        "title": "Which Hogwarts house feels most like you?",
        "options": [
            {
                "label": "Gryffindor",
                "w": {
                    "energy": 0.85,
                    "valence": 0.70,
                    "genres": {"rock": 3, "pop": 2},
                    "moods": {"Energetic": 3}
                }
            },
            {
                "label": "Slytherin",
                "w": {
                    "energy": 0.70,
                    "valence": 0.30,
                    "genres": {"hip-hop": 3},
                    "moods": {"Chill": 2}
                }
            },
            {
                "label": "Ravenclaw",
                "w": {
                    "energy": 0.30,
                    "valence": 0.40,
                    "genres": {"classical": 3},
                    "moods": {"Focus": 3}
                }
            },
            {
                "label": "Hufflepuff",
                "w": {
                    "energy": 0.45,
                    "valence": 0.85,
                    "genres": {"pop": 2},
                    "moods": {"Happy": 3}
                }
            }
        ]
    },

    {
        "title": "Pick your current aesthetic",
        "options": [
            {
                "label": "Cottagecore",
                "w": {
                    "energy": 0.35,
                    "valence": 0.75,
                    "genres": {"indie": 3},
                    "moods": {"Chill": 2}
                }
            },
            {
                "label": "Dark Academia",
                "w": {
                    "energy": 0.25,
                    "valence": 0.30,
                    "genres": {"classical": 3},
                    "moods": {"Sad": 2}
                }
            },
            {
                "label": "Y2K",
                "w": {
                    "energy": 0.90,
                    "valence": 0.90,
                    "genres": {"pop": 3},
                    "moods": {"Energetic": 3}
                }
            }
        ]
    }
]

# =========================================================
# PROFILE AGGREGATION
# =========================================================

def aggregate_profile(answers):

    energy_sum = 0
    valence_sum = 0
    count = 0

    genres = {}
    moods = {}

    for q_index, answer_index in answers.items():

        option = quiz[q_index]["options"][answer_index]
        w = option["w"]

        energy_sum += w["energy"]
        valence_sum += w["valence"]
        count += 1

        for g, v in w["genres"].items():
            genres[g] = genres.get(g, 0) + v

        for m, v in w["moods"].items():
            moods[m] = moods.get(m, 0) + v

    return {
        "target_energy": energy_sum / count,
        "target_valence": valence_sum / count,
        "genres": genres,
        "moods": moods
    }

# =========================================================
# SONG SCORING
# =========================================================

def score_song(row, profile):

    energy_dist = abs(row["energy"] - profile["target_energy"])
    valence_dist = abs(row["valence"] - profile["target_valence"])

    genre_bonus = profile["genres"].get(
        str(row["genre"]).lower(),
        0
    ) * 0.08

    mood_bonus = profile["moods"].get(
        row["mood"],
        0
    ) * 0.07

    popularity_bonus = row["popularity"] / 100

    return (
        -(energy_dist + valence_dist)
        + genre_bonus
        + mood_bonus
        + popularity_bonus
    )

# =========================================================
# RECOMMENDATION ENGINE
# =========================================================

def recommend(answers, songs_df, k=6):

    profile = aggregate_profile(answers)

    scored = songs_df.copy()

    scored["match_score"] = scored.apply(
        lambda row: score_song(row, profile),
        axis=1
    )

    scored = scored.sort_values(
        "match_score",
        ascending=False
    )

    return profile, scored.head(k)

# =========================================================
# ITUNES API
# =========================================================

def fetch_song_meta(name, artist):

    try:

        response = requests.get(
            "https://itunes.apple.com/search",
            params={
                "term": f"{name} {artist}",
                "media": "music",
                "limit": 1
            },
            timeout=5
        )

        results = response.json().get("results", [])

        if not results:
            return None

        item = results[0]

        cover = item.get("artworkUrl100", "")

        if cover:
            cover = cover.replace(
                "100x100bb",
                "600x600bb"
            )

        return {
            "cover": cover,
            "preview": item.get("previewUrl")
        }

    except:
        return None

# =========================================================
# HEADER
# =========================================================

st.title("🎵 BACO Station")
st.caption("Discover songs that match your personality.")

name = st.text_input("Your name")

# =========================================================
# QUIZ UI
# =========================================================

answers = {}

for i, question in enumerate(quiz):

    labels = [
        option["label"]
        for option in question["options"]
    ]

    choice = st.radio(
        question["title"],
        labels,
        key=i
    )

    selected_index = labels.index(choice)

    answers[i] = selected_index

# =========================================================
# GENERATE RECOMMENDATIONS
# =========================================================

if st.button("Get My Vibe"):

    with st.spinner("Building your playlist..."):

        profile, playlist = recommend(
            answers,
            songs
        )

        top_song = playlist.iloc[0]

        meta = fetch_song_meta(
            top_song["name"],
            top_song["artist"]
        )

        st.markdown(f"""
        <div class="persona-card">
            <h2>{name if name else "Your"} vibe</h2>

            <div class="badge">
                Energy: {profile["target_energy"]:.2f}
            </div>

            <div class="badge">
                Valence: {profile["target_valence"]:.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("✨ Your Top Match")

        col1, col2 = st.columns([1, 2])

        with col1:

            if meta and meta["cover"]:
                st.image(meta["cover"])

        with col2:

            st.markdown(f"""
            ### {top_song["name"]}

            **Artist:** {top_song["artist"]}

            **Genre:** {top_song["genre"]}

            **Mood:** {top_song["mood"]}
            """)

            if meta and meta["preview"]:
                st.audio(meta["preview"])

        st.subheader("🎧 Recommended Playlist")

        display_cols = [
            "name",
            "artist",
            "genre",
            "mood",
            "energy",
            "valence",
            "tempo",
            "popularity"
        ]

        st.dataframe(
            playlist[display_cols],
            use_container_width=True
        )
