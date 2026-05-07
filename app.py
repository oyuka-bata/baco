import streamlit as st
import pandas as pd
import sqlite3
import requests

# --- 1. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="BACO Station", page_icon="🎵", layout="centered")

# --- 2. DATA LOADING & CACHING ---
# Using st.cache_data prevents Streamlit from downloading the dataset on every interaction
@st.cache_data
def load_data():
    DB_NAME = "spotify_music.db"
    CSV_URL = "https://huggingface.co/datasets/sfiore/spotify-tracks-dataset/resolve/main/dataset.csv"
    
    # Download dataset
    songs = pd.read_csv(CSV_URL)

    # Clean column names
    songs.columns = [c.lower().strip() for c in songs.columns]

    # Keep only useful columns
    wanted_columns = [
        "track_name", "artists", "track_genre", "danceability", 
        "energy", "valence", "tempo", "acousticness", 
        "instrumentalness", "speechiness", "liveness", "popularity"
    ]

    existing_columns = [c for c in wanted_columns if c in songs.columns]
    songs = songs[existing_columns].dropna()

    # Save to SQLite database
    conn = sqlite3.connect(DB_NAME)
    songs.to_sql("spotify_tracks", conn, if_exists="replace", index=False)

    # Load back from SQL (backend retrieval simulation)
    songs = pd.read_sql_query(
        "SELECT * FROM spotify_tracks LIMIT 50000", conn
    )
    conn.close()

    # Rename columns for consistency
    songs = songs.rename(columns={
        "track_name": "name",
        "artists": "artist",
        "track_genre": "genre"
    })

    # Function to assign mood to each song based on energy and valence
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

    # Apply the mood assignment
    songs["mood"] = songs.apply(assign_mood_to_song, axis=1)
    return songs

# --- 3. QUIZ DATA ---
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

# --- 4. LOGIC FUNCTIONS ---
def aggregate_profile(answers):
    energy_sum = 0.0
    valence_sum = 0.0
    weight_sum = 0
    genres = {}
    moods = {}

    for qi, ai in answers.items():
        opt = quiz[qi]["options"][ai]
        w = opt["w"]
        energy_sum  += w["energy"]
        valence_sum += w["valence"]
        weight_sum  += 1
        for g, v in w["genres"].items():
            genres[g] = genres.get(g, 0) + v
        for m, v in w["moods"].items():
            moods[m] = moods.get(m, 0) + v

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
    return profile, scored.iloc[0], scored.head(k)

def pick_persona(profile):
    e = profile["target_energy"]
    v = profile["target_valence"]

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
    except Exception as e:
        return None

# --- 5. UI HTML RENDERERS ---
def render_persona_card(name, persona_title, persona_desc, profile):
    top_mood  = max(profile["moods"].items(),  key=lambda kv: kv[1])[0] if profile["moods"]  else "Chill"
    top_genre = max(profile["genres"].items(), key=lambda kv: kv[1])[0] if profile["genres"] else "Pop"
    return f"""
    <div style="padding:22px;border-radius:14px;background:linear-gradient(135deg,#163826 0%,#1a2030 60%,#2b1d3a 100%);color:#eceff4;text-align:center;margin:14px 0;">
      <p style="color:#6ee7a7;font-size:0.78rem;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;margin:0 0 6px 0;">
        {name}'s vibe
      </p>
      <h2 style="margin:4px 0 8px 0;font-size:1.7rem;">{persona_title}</h2>
      <p style="margin:0 0 14px 0;color:#cbd5e1;">{persona_desc}</p>
      <div>
        <span style="padding:4px 12px;border-radius:999px;background:rgba(29,185,84,0.15);border:1px solid rgba(110,231,167,0.4);color:#6ee7a7;font-size:0.78rem;font-weight:600;margin:0 4px;">Mood · {top_mood}</span>
        <span style="padding:4px 12px;border-radius:999px;background:rgba(29,185,84,0.15);border:1px solid rgba(110,231,167,0.4);color:#6ee7a7;font-size:0.78rem;font-weight:600;margin:0 4px;">Genre · {top_genre}</span>
        <span style="padding:4px 12px;border-radius:999px;background:rgba(255,255,255,0.06);border:1px solid #2a2f3a;color:#cbd5e1;font-size:0.78rem;font-weight:600;margin:0 4px;">Energy {profile['target_energy']:.2f}</span>
        <span style="padding:4px 12px;border-radius:999px;background:rgba(255,255,255,0.06);border:1px solid #2a2f3a;color:#cbd5e1;font-size:0.78rem;font-weight:600;margin:0 4px;">Valence {profile['target_valence']:.2f}</span>
      </div>
    </div>
    """

def render_top_pick_card(top, meta):
    cover_html = ""
    if meta and meta.get("cover"):
        cover_html = f'<img src="{meta["cover"]}" alt="album cover" style="width:160px;height:160px;border-radius:12px;display:block;margin:0 auto 14px;box-shadow:0 8px 22px rgba(0,0,0,0.35);" />'
    return f"""
    <div style="padding:22px;border:1px solid #2a2f3a;border-radius:14px;background:#1a1d24;color:#eceff4;text-align:center;margin:14px 0;">
      <p style="color:#1ed760;font-size:0.78rem;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;margin:0 0 8px 0;">Your top pick</p>
      {cover_html}
      <h3 style="margin:0 0 4px 0;font-size:1.4rem;color:white;">{top['name']}</h3>
      <p style="margin:0 0 12px 0;color:#9ca3af;">by {top['artist']}</p>
      <div>
        <span style="padding:4px 12px;border-radius:999px;background:rgba(29,185,84,0.10);border:1px solid rgba(110,231,167,0.4);color:#6ee7a7;font-size:0.78rem;font-weight:600;margin:0 4px;">{top['genre']}</span>
        <span style="padding:4px 12px;border-radius:999px;background:rgba(29,185,84,0.10);border:1px solid rgba(110,231,167,0.4);color:#6ee7a7;font-size:0.78rem;font-weight:600;margin:0 4px;">{top['mood']}</span>
        <span style="padding:4px 12px;border-radius:999px;background:rgba(255,255,255,0.06);border:1px solid #2a2f3a;color:#cbd5e1;font-size:0.78rem;font-weight:600;margin:0 4px;">Energy {top['energy']:.2f}</span>
        <span style="padding:4px 12px;border-radius:999px;background:rgba(255,255,255,0.06);border:1px solid #2a2f3a;color:#cbd5e1;font-size:0.78rem;font-weight:600;margin:0 4px;">{int(top['tempo'])} BPM</span>
      </div>
    </div>
    """

def build_explanation(top, profile):
    return (
        f"<p style='color:#cbd5e1; font-size:1rem;'><b>Why this one?</b> Your vibe profile averaged out to "
        f"<b>energy {profile['target_energy']:.2f}</b> and <b>valence {profile['target_valence']:.2f}</b>. "
        f"<b>{top['name']}</b> by <b>{top['artist']}</b> sits at energy {top['energy']:.2f} / valence {top['valence']:.2f}, "
        f"with a genre and mood that match your top picks ({top['genre']} · {top['mood']}). "
        f"It also has a popularity of {int(top['popularity'])}/100, which is the tiebreaker.</p>"
    )


# --- 6. MAIN STREAMLIT APP ---
st.markdown("""
<div style="padding:18px 22px;border-radius:12px;background:linear-gradient(120deg,#1db954 0%,#1ed760 50%,#14833b 100%);color:white;margin-bottom:20px;">
  <h2 style="margin:0; color:white;">BACO Station</h2>
  <p style="margin:4px 0 0 0;">Pick your mood, your genre, your energy — get songs that match.</p>
</div>
""", unsafe_allow_html=True)

# Load data into memory
songs_df = load_data()

# Render Form
with st.form(key='vibe_quiz'):
    name_input = st.text_input("Name:", placeholder="Type your name")
    
    user_selections = []
    for i, q in enumerate(quiz):
        labels = ["—"] + [opt["label"] for opt in q["options"]]
        ans = st.selectbox(f"**{q['title']}**", labels, key=f"q_{i}")
        user_selections.append(ans)
        
    submit_button = st.form_submit_button(label='Get my vibe 🎧')

# Process Results
if submit_button:
    name = name_input.strip() if name_input.strip() else "Friend"
    
    # Map back selections to indexes
    answers = {}
    for i, ans in enumerate(user_selections):
        if ans != "—":
            labels = [opt["label"] for opt in quiz[i]["options"]]
            answers[i] = labels.index(ans)

    if not answers:
        st.error("Please answer at least one question, then click **Get my vibe** again.")
    else:
        with st.spinner('Curating your vibe...'):
            profile, top, playlist = recommend(answers, songs_df)
            persona_title, persona_desc = pick_persona(profile)
            meta = fetch_song_meta(top["name"], top["artist"])

        # Display UI
        st.markdown(render_persona_card(name, persona_title, persona_desc, profile), unsafe_allow_html=True)
        st.markdown(render_top_pick_card(top, meta), unsafe_allow_html=True)
        st.markdown(build_explanation(top, profile), unsafe_allow_html=True)

        if meta and meta.get("preview"):
            st.markdown("<p style='color:#eceff4;'><b>30-second preview:</b></p>", unsafe_allow_html=True)
            st.audio(meta["preview"], format="audio/mp4")
        else:
            st.markdown("<p style='color:#888;'><i>(Audio preview not available for this song.)</i></p>", unsafe_allow_html=True)

        st.markdown(f"<br><p style='color:#eceff4; font-size:1.1rem;'><b>Your BACO Station playlist ({len(playlist)} tracks):</b></p>", unsafe_allow_html=True)
        nice_cols = ["name", "artist", "genre", "mood", "energy", "valence", "tempo", "popularity"]
        st.dataframe(playlist[nice_cols].reset_index(drop=True), use_container_width=True)
