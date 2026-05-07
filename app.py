import streamlit as st
import pandas as pd
import sqlite3
import requests
import time

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="BACO Station", page_icon="🎵", layout="centered")

# --- 2. CUSTOM SPOTIFY-LIKE CSS INJECTION ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,400;0,500;1,400&display=swap');

.stApp {
    background-color: #0a0c0f;
    color: #f0f2f5;
    font-family: 'DM Sans', sans-serif;
}

header { visibility: hidden; }

h1, h2, h3, .stMarkdown p strong {
    font-family: 'Syne', sans-serif;
    color: #ffffff;
}

div[data-baseweb="select"] > div, 
div[data-baseweb="input"] > div {
    background-color: #111318 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 8px;
    color: #f0f2f5 !important;
}

div[data-baseweb="select"] > div:focus-within, 
div[data-baseweb="input"] > div:focus-within {
    border-color: #1db954 !important;
}

div.stButton > button {
    background-color: #1db954;
    color: #000000;
    border: none;
    border-radius: 999px;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    padding: 0.5rem 2rem;
    transition: transform 0.15s, background 0.15s;
    width: 100%;
    margin-top: 20px;
}

div.stButton > button:hover {
    background-color: #1ed760;
    color: #000000;
}

.hero-title { font-family: 'Syne', sans-serif; font-size: 4rem; font-weight: 800; line-height: 0.95; margin-bottom: 10px; text-align: center; }
.hero-title span { color: #1db954; }
.hero-sub { color: #9aa3b2; text-align: center; font-size: 1.1rem; margin-bottom: 40px; font-weight: 300;}

.persona-card {
    background: #111318;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 36px;
    margin-bottom: 20px;
    text-align: center;
    background: linear-gradient(135deg, rgba(29,185,84,0.08) 0%, rgba(29,185,84,0.02) 50%, rgba(80,50,120,0.06) 100%);
}
.persona-badge { font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #1db954; margin-bottom: 10px; }
.persona-name { font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800; margin-bottom: 10px; letter-spacing: -0.02em; }
.persona-desc { color: #9aa3b2; font-size: 0.95rem; margin: 0 auto 20px; font-style: italic; }

.tag-row { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
.tag { padding: 5px 14px; border-radius: 999px; font-size: 0.78rem; font-weight: 600; }
.tag-green { background: rgba(29,185,84,0.12); border: 1px solid rgba(29,185,84,0.35); color: #6ee7a7; }
.tag-gray { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.13); color: #9aa3b2; }

.top-pick-card {
    background: #111318;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 28px;
    margin-bottom: 20px;
    display: flex;
    gap: 24px;
    align-items: flex-start;
}
.album-cover { width: 140px; height: 140px; border-radius: 10px; object-fit: cover; flex-shrink: 0; background: #1f2430; }
.top-pick-info { flex: 1; }
.top-pick-eyebrow { font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #1db954; margin-bottom: 8px; }
.top-pick-name { font-family: 'Syne', sans-serif; font-size: 1.5rem; font-weight: 700; margin-bottom: 4px; line-height: 1.2; }
.top-pick-artist { color: #9aa3b2; margin-bottom: 16px; font-size: 0.95rem; }
.audio-player audio { width: 100%; filter: invert(1) hue-rotate(180deg); margin-top: 15px; }

.explanation-box {
    background: #111318;
    border: 1px solid rgba(255,255,255,0.07);
    border-left: 3px solid #1db954;
    border-radius: 8px;
    padding: 18px 20px;
    margin-bottom: 20px;
    font-size: 0.9rem;
    color: #9aa3b2;
    line-height: 1.7;
}

.playlist-header { font-family: 'Syne', sans-serif; font-size: 1rem; font-weight: 700; margin-bottom: 12px; margin-top: 30px; display: flex; align-items: center; gap: 10px; }
.playlist-count { font-size: 0.75rem; background: #1f2430; border: 1px solid rgba(255,255,255,0.13); color: #9aa3b2; padding: 3px 10px; border-radius: 999px; font-family: 'DM Sans', sans-serif; font-weight: 500; }

.playlist-track { display: flex; align-items: center; gap: 14px; padding: 14px 18px; border-radius: 8px; border: 1px solid transparent; transition: background 0.15s; }
.playlist-track:hover { background: #111318; border-color: rgba(255,255,255,0.07); }
.track-num { width: 22px; font-size: 0.8rem; color: #5c6578; text-align: center; flex-shrink: 0; }
.track-info { flex: 1; min-width: 0; }
.track-name { font-weight: 500; font-size: 0.93rem; color: #f0f2f5; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.track-artist { font-size: 0.8rem; color: #5c6578; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.track-tag { font-size: 0.72rem; padding: 3px 9px; border-radius: 999px; background: #1f2430; color: #5c6578; border: 1px solid rgba(255,255,255,0.07); margin-left: 5px;}
</style>
""", unsafe_allow_html=True)

# --- 3. DATA LOADING & CACHING ---
@st.cache_data
def load_data():
    DB_NAME = "spotify_music.db"
    CSV_URL = "https://huggingface.co/datasets/sfiore/spotify-tracks-dataset/resolve/main/dataset.csv"
    
    songs = pd.read_csv(CSV_URL)
    songs.columns = [c.lower().strip() for c in songs.columns]

    wanted_columns = [
        "track_name", "artists", "track_genre", "danceability", 
        "energy", "valence", "tempo", "acousticness", 
        "instrumentalness", "speechiness", "liveness", "popularity"
    ]
    existing_columns = [c for c in wanted_columns if c in songs.columns]
    songs = songs[existing_columns].dropna()

    conn = sqlite3.connect(DB_NAME)
    songs.to_sql("spotify_tracks", conn, if_exists="replace", index=False)
    songs = pd.read_sql_query("SELECT * FROM spotify_tracks LIMIT 50000", conn)
    conn.close()

    songs = songs.rename(columns={"track_name": "name", "artists": "artist", "track_genre": "genre"})

    def assign_mood_to_song(row):
        e = row["energy"]
        v = row["valence"]
        if e >= 0.78 and v >= 0.78: return "Energetic"
        if e >= 0.65 and v >= 0.55: return "Happy"
        if e >= 0.65 and v < 0.55: return "Energetic"
        if e < 0.40 and v < 0.40: return "Sad"
        if e < 0.40: return "Focus"
        if v < 0.40: return "Sad"
        if e >= 0.45 and v >= 0.65: return "Chill"
        if e < 0.45 and v >= 0.55: return "Happy"
        return "Chill"

    songs["mood"] = songs.apply(assign_mood_to_song, axis=1)
    return songs

# --- 4. QUIZ DATA ---
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
            {"label": "Paris — slow mornings, cafés, jazz",             "w": {"energy": 0.40, "valence": 0.60, "genres": {"Jazz": 3, "Indie": 2, "Classical": 2}, "moods": {"Chill": 3, "Happy": 1}}},
            {"label": "Tokyo — neon, vending machines, 7-Elevens",      "w": {"energy": 0.85, "valence": 0.65, "genres": {"Electronic": 3, "Pop": 2, "Hip-Hop": 2}, "moods": {"Energetic": 3}}},
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
            {"label": "Hot tea — slow morning, gentle",        "w": {"energy": 0.25, "valence": 0.55, "genres": {"Indie": 2, "Classical": 2, "Jazz": 1}, "moods": {"Chill": 2, "Focus": 1}}},
            {"label": "Cocktail — it's the weekend",             "w": {"energy": 0.85, "valence": 0.70, "genres": {"Electronic": 3, "Pop": 2, "R&B": 1}, "moods": {"Energetic": 2}}},
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

# --- 5. LOGIC FUNCTIONS ---
def aggregate_profile(answers):
    energy_sum, valence_sum, weight_sum = 0.0, 0.0, 0
    genres, moods = {}, {}

    for qi, ai in answers.items():
        opt = quiz[qi]["options"][ai]
        w = opt["w"]
        energy_sum  += w["energy"]
        valence_sum += w["valence"]
        weight_sum  += 1
        for g, v in w["genres"].items(): genres[g] = genres.get(g, 0) + v
        for m, v in w["moods"].items(): moods[m] = moods.get(m, 0) + v

    return {
        "target_energy":  energy_sum  / weight_sum if weight_sum else 0.5,
        "target_valence": valence_sum / weight_sum if weight_sum else 0.5,
        "genres": genres,
        "moods":  moods,
    }

def score_song(row, profile):
    energy_dist  = abs(row["energy"]  - profile["target_energy"])
    valence_dist = abs(row["valence"] - profile["target_valence"])
    genre_bonus  = profile["genres"].get(row["genre"], 0) * 0.08
    mood_bonus   = profile["moods"].get(row["mood"],  0) * 0.07
    pop_bonus    = row["popularity"] / 100.0
    return -(energy_dist + valence_dist) + genre_bonus + mood_bonus + pop_bonus

def recommend(answers, songs_df, k=6):
    profile = aggregate_profile(answers)
    scored  = songs_df.copy()  
    scored["match_score"] = scored.apply(lambda r: score_song(r, profile), axis=1)
    scored = scored.sort_values("match_score", ascending=False)
    scored = scored.drop_duplicates(subset=["name", "artist"])
    top_pick = scored.iloc[0]
    playlist = scored.iloc[1:k+1]
    return profile, top_pick, playlist
def pick_persona(profile):
    e, v = profile["target_energy"], profile["target_valence"]
    if e >= 0.78 and v >= 0.78: return ("The Disco Heart", "Pure joy at full volume. You'd dance in an empty parking lot if the song hit.")
    if e >= 0.65 and v >= 0.55: return ("The Main-Character Anthem", "High energy, high serotonin. You walk into rooms like there's a soundtrack playing.")
    if e >= 0.65 and v < 0.55: return ("The Midnight Hype", "Loud, sharp, a little dark — your playlist hits like 1am in a cab.")
    if e >= 0.45 and v >= 0.65: return ("The Golden Hour", "Warm, sun-through-the-trees energy. Walks home with a small smile.")
    if e < 0.45 and v >= 0.55: return ("The Sunset Daydreamer", "Soft, warm, daydream energy. Headphones in, eyes on the sky.")
    if e < 0.40 and v < 0.40: return ("The Rainy-Window Romantic", "In your feelings, in the best way. A movie scene about you, scored just right.")
    if e < 0.40: return ("The Library Loft", "Focused, quiet, thinking ten thoughts at once. Music as the background of your brain.")
    if v < 0.40: return ("The Slow Burn", "Brooding without being heavy. The friend people call when they need to vent.")
    return ("The Easy Drift", "Steady mood, easy tempo. Your playlist just works for everything.")

def fetch_song_meta(name, artist, timeout=5):
    try:
        resp = requests.get(
            "https://itunes.apple.com/search",
            params={"term": f"{name} {artist}", "media": "music", "entity": "song", "limit": 1},
            timeout=timeout,
        )
        resp.raise_for_status()
        items = resp.json().get("results", [])
        if not items: return None
        item = items[0]
        cover = item.get("artworkUrl100", "")
        if cover: cover = cover.replace("100x100bb", "600x600bb")
        return {"cover": cover or None, "preview": item.get("previewUrl") or None}
    except Exception:
        return None

# --- 6. UI HTML GENERATORS (Indentation removed to prevent Markdown code block rendering) ---
def render_results(name, persona_title, persona_desc, profile, top, meta, playlist):
    top_mood  = max(profile["moods"].items(),  key=lambda kv: kv[1])[0] if profile["moods"]  else "Chill"
    top_genre = max(profile["genres"].items(), key=lambda kv: kv[1])[0] if profile["genres"] else "Pop"
    
    # Notice: NO leading spaces before the HTML tags so Streamlit doesn't turn it into a Code Block!
    persona_html = f"""<div class="persona-card">
<div class="persona-badge">{name}'s vibe</div>
<div class="persona-name">{persona_title}</div>
<div class="persona-desc">{persona_desc}</div>
<div class="tag-row">
<span class="tag tag-green">Mood · {top_mood}</span>
<span class="tag tag-green">Genre · {top_genre}</span>
<span class="tag tag-gray">Energy {profile['target_energy']:.2f}</span>
<span class="tag tag-gray">Valence {profile['target_valence']:.2f}</span>
</div>
</div>"""

    cover_html = f'<img src="{meta["cover"]}" class="album-cover" />' if (meta and meta.get("cover")) else '<div class="album-cover" style="display:flex;align-items:center;justify-content:center;font-size:3rem;">🎵</div>'
    preview_html = f'<div class="audio-player"><audio controls src="{meta["preview"]}"></audio></div>' if (meta and meta.get("preview")) else '<div style="margin-top:15px; color:#5c6578; font-size:0.85rem; font-style:italic;">Preview not available for this track.</div>'

    top_pick_html = f"""<div class="top-pick-card">
{cover_html}
<div class="top-pick-info">
<div class="top-pick-eyebrow">Your top pick</div>
<div class="top-pick-name">{top['name']}</div>
<div class="top-pick-artist">by {top['artist']}</div>
<div class="tag-row" style="justify-content:flex-start">
<span class="tag tag-green">{top['genre']}</span>
<span class="tag tag-green">{top['mood']}</span>
<span class="tag tag-gray">Energy {top['energy']:.2f}</span>
<span class="tag tag-gray">{int(top['tempo'])} BPM</span>
</div>
{preview_html}
</div>
</div>"""

    explanation_html = f"""<div class="explanation-box">
<strong>Why this one?</strong> Your vibe profile averaged to energy {profile['target_energy']:.2f} and valence {profile['target_valence']:.2f}.
<strong>{top['name']}</strong> by <strong>{top['artist']}</strong> sits at energy {top['energy']:.2f} / valence {top['valence']:.2f},
with a matching genre ({top['genre']}) and mood ({top['mood']}). Popularity score: {int(top['popularity'])}/100.
</div>"""

    track_rows_html = ""
    for i, track in playlist.iterrows():
        track_rows_html += f"""<div class="playlist-track">
<div class="track-num">{i + 1}</div>
<div class="track-info">
<div class="track-name">{track['name']}</div>
<div class="track-artist">{track['artist']}</div>
</div>
<div class="track-meta">
<span class="track-tag">{track['mood']}</span>
<span class="track-tag">{int(track['tempo'])} BPM</span>
</div>
</div>"""

    playlist_html = f"""<div>
<div class="playlist-header">
Your BACO Station playlist
<span class="playlist-count">{len(playlist)} tracks</span>
</div>
{track_rows_html}
</div>"""

    return persona_html + top_pick_html + explanation_html + playlist_html


# --- 7. MAIN APP LAYOUT ---
st.markdown('<div class="hero-title">BACO<br><span>Station</span></div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Answer 9 vibe questions. Get a song that actually fits your energy — with album art and a 30-second preview.</div>', unsafe_allow_html=True)

songs_df = load_data()

with st.form(key='vibe_quiz'):
    name_input = st.text_input("Your Name:", placeholder="Enter your name...")
    
    user_selections = []
    for i, q in enumerate(quiz):
        st.markdown(f"**Question {i+1} of {len(quiz)}:** {q['title']}")
        labels = ["—"] + [opt["label"] for opt in q["options"]]
        ans = st.selectbox("", labels, key=f"q_{i}", label_visibility="collapsed")
        user_selections.append(ans)
        st.write("") # small spacing
        
    submit_button = st.form_submit_button(label='Get my vibe')

if submit_button:
    name = name_input.strip() if name_input.strip() else "Friend"
    answers = {}
    
    for i, ans in enumerate(user_selections):
        if ans != "—":
            labels = [opt["label"] for opt in quiz[i]["options"]]
            answers[i] = labels.index(ans)

    if not answers:
        st.error("Please answer at least one question to get your vibe.")
    else:
        # 1. Create a placeholder for our animation
        animation_placeholder = st.empty()
        
        # 2. Inject the CSS and HTML for the floating notes
        animation_placeholder.markdown("""
        <style>
        .floating-notes {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            pointer-events: none; z-index: 9999; overflow: hidden;
        }
        .f-note {
            position: absolute; bottom: -10%;
            animation: floatUp 2s ease-in infinite;
        }
        /* Green Notes */
        .f-note:nth-child(1) { left: 15%; animation-duration: 2.5s; font-size: 3rem; color: #1db954; }
        .f-note:nth-child(3) { left: 55%; animation-duration: 3s; animation-delay: 0.3s; font-size: 4rem; color: #1db954; }
        .f-note:nth-child(5) { left: 85%; animation-duration: 2.8s; animation-delay: 0.6s; font-size: 3.5rem; color: #1db954; }
        
        /* Black Notes (with green glow to be visible on dark background) */
        .f-note:nth-child(2) { left: 35%; animation-duration: 2.2s; animation-delay: 0.5s; font-size: 2.5rem; color: #000000; text-shadow: 0 0 6px #1db954; }
        .f-note:nth-child(4) { left: 75%; animation-duration: 2.6s; animation-delay: 0.2s; font-size: 3rem; color: #000000; text-shadow: 0 0 6px #1db954; }
        .f-note:nth-child(6) { left: 5%; animation-duration: 3.2s; animation-delay: 0.8s; font-size: 2rem; color: #000000; text-shadow: 0 0 6px #1db954; }

        @keyframes floatUp {
            0% { transform: translateY(0) rotate(-15deg); opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { transform: translateY(-110vh) rotate(25deg); opacity: 0; }
        }
        </style>
        <div class="floating-notes">
            <div class="f-note">🎵</div>
            <div class="f-note">🎶</div>
            <div class="f-note">🎵</div>
            <div class="f-note">🎶</div>
            <div class="f-note">🎵</div>
            <div class="f-note">🎶</div>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner('Scoring the dataset and fetching your vibe...'):
            time.sleep(2) 
            
            profile, top, playlist = recommend(answers, songs_df)
            playlist = playlist.reset_index(drop=True)
            persona_title, persona_desc = pick_persona(profile)
            meta = fetch_song_meta(top["name"], top["artist"])
        animation_placeholder.empty()
        final_html = render_results(name, persona_title, persona_desc, profile, top, meta, playlist)
        st.markdown(final_html, unsafe_allow_html=True)
