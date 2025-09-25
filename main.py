import pandas as pd
import streamlit as st
import random
import os
import json
from mutagen import File as MutagenFile
from mutagen import File as MutagenFile
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
import requests

def fetch_artist_from_itunes(title: str):
    try:
        url = f"https://itunes.apple.com/search"
        params = {"term": title, "entity": "musicTrack", "limit": 1}
        response = requests.get(url, params=params)
        data = response.json()
        if data["resultCount"] > 0:
            return data["results"][0]["artistName"]
    except Exception as e:
        print("Artist lookup failed:", e)
    return "Unknown Artist"



def get_duration(save_path):
    ext = os.path.splitext(save_path)[1].lower()
    duration = "Unknown"

    try:
        if ext == ".mp3":
            audio = MP3(save_path)
            total_seconds = int(audio.info.length)
            duration = f"{total_seconds // 60}:{total_seconds % 60:02d}"

        elif ext == ".wav":
            audio = WAVE(save_path)
            total_seconds = int(audio.info.length)
            duration = f"{total_seconds // 60}:{total_seconds % 60:02d}"

        else:
            audio = MutagenFile(save_path)
            if audio and audio.info:
                total_seconds = int(audio.info.length)
                duration = f"{total_seconds // 60}:{total_seconds % 60:02d}"

    except Exception as e:
        print(f"Duration extraction failed: {e}")

    return duration

# ---------------- Song Class ----------------


from mutagen.mp3 import MP3
import os

class Song:
    def __init__(self, file_path, title=None, artist=None, duration=None):
        self.file_path = file_path

        # Title
        self.title = title or os.path.splitext(os.path.basename(file_path))[0]

        # Duration
        if duration:
            self.duration = duration
        else:
            try:
                audio = MP3(file_path)
                self.duration = round(audio.info.length, 2)
            except Exception:
                self.duration = "Unknown"

        # Artist (priority: passed value → metadata → Unknown)
        if artist and artist != "Unknown Artist":
            self.artist = artist
        else:
            try:
                audio = MP3(file_path)
                self.artist = audio.get("TPE1", ["Unknown Artist"])[0]
            except Exception:
                self.artist = "Unknown Artist"

    def __str__(self):
        return f"{self.title} - {self.artist}"





# ---------------- Playlist Class ----------------
class Playlist:
    def __init__(self):
        self.songs = []
        self.current_index = -1

    def add_song(self, song):
        self.songs.append(song)

    def remove_song(self, index):
        if 0 <= index < len(self.songs):
            self.songs.pop(index)
            if self.current_index >= len(self.songs):
                self.current_index = len(self.songs) - 1

    def get_current_song(self):
        if 0 <= self.current_index < len(self.songs):
            return self.songs[self.current_index]
        return None

    def next_song(self):
        if not self.songs:
            return None
        self.current_index = (self.current_index + 1) % len(self.songs)
        return self.get_current_song()

    def prev_song(self):
        if not self.songs:
            return None
        self.current_index = (self.current_index - 1) % len(self.songs)
        return self.get_current_song()

    def shuffle(self):
        random.shuffle(self.songs)
        self.current_index = -1


# ---------------- Streamlit App ----------------
st.set_page_config(page_title=" Music Playlist", layout="centered")


# --- Neon Mode CSS ---
neon_mode = """
<style>
/* Background */
body {
    background-image: url("https://images.unsplash.com/photo-1601042879364-f3947d3f9c16?fm=jpg&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8bmVvbiUyMGNpdHl8ZW58MHx8MHx8fDA%3D&ixlib=rb-4.1.0&q=60&w=3000");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    color: #f2f2f7; /* soft neutral white */
    font-family: "Orbitron", sans-serif;
}

/* Glass Effect Container */
.stApp {
    background: rgba(10, 10, 15, 0.55);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0px 0px 30px rgba(255, 20, 147, 0.4);
}

/* Titles */
h1 {
    color: #ff4da6; /* rose neon */
    text-shadow: 0px 0px 12px #ff4da6, 0px 0px 25px rgba(255, 128, 191, 0.8);
    text-align: center;
}
h2, h3 {
    color: #66ffe7; /* aqua neon */
    text-shadow: 0px 0px 10px #66ffe7, 0px 0px 18px rgba(102, 255, 231, 0.7);
}

/* Paragraph Text */
p, label, span {
    color: #e6e6eb;
    text-shadow: 0px 0px 4px rgba(255, 255, 255, 0.25);
}

/* Cyberpunk Buttons */
.stButton > button {
    background: linear-gradient(135deg, #ff4da6, #ff80bf);
    color: #fff;
    border: none;
    border-radius: 12px;
    font-weight: bold;
    padding: 10px 24px;
    font-size: 16px;
    box-shadow: 0px 0px 20px rgba(255, 128, 191, 0.6);
    text-shadow: 0px 0px 6px rgba(255, 255, 255, 0.7);
    transition: all 0.3s ease-in-out;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #66ffe7, #33ffcc);
    box-shadow: 0px 0px 25px rgba(102, 255, 231, 0.9);
    transform: scale(1.1);
}

/* Input Fields */
.stTextInput > div > div > input {
    background: rgba(20, 20, 30, 0.7);
    color: #f2f2f7;
    border-radius: 10px;
    border: 1px solid #ff80bf;
    padding: 8px;
    box-shadow: 0px 0px 10px rgba(255, 128, 191, 0.4);
}
.stTextInput > div > div > input:focus {
    border: 1px solid #66ffe7;
    box-shadow: 0px 0px 18px rgba(102, 255, 231, 0.7);
}

/* Selectbox & Dropdowns */
.stSelectbox > div > div {
    background: rgba(20, 20, 30, 0.75);
    color: #f2f2f7;
    border-radius: 10px;
    border: 1px solid #ff4da6;
    box-shadow: 0px 0px 12px rgba(255, 77, 166, 0.5);
}
</style>
"""
st.markdown(neon_mode, unsafe_allow_html=True)


st.title(" Music Playlist")
if not os.path.exists("songs"):
    os.makedirs("songs")

# Store Playlist in session_state (so it doesn't reset on every click)
if "playlist" not in st.session_state:
    st.session_state.playlist = Playlist()
if "status" not in st.session_state:
    st.session_state.status = "No song playing"

playlist = st.session_state.playlist


#     Load data info from songs.json 
metadata_file = "songs/songs.json"
if os.path.exists(metadata_file) and not playlist.songs:
    with open(metadata_file, "r") as f:
        songs_data = json.load(f)
    for song_info in songs_data:
        loaded_song = Song(
            file_path=song_info["file_path"],
            title=song_info.get("title"),
            artist=song_info.get("artist"),
            duration=song_info.get("duration")
            )
        playlist.add_song(loaded_song)


# -------- Add Song Form --------


st.subheader("➕ Add a New Song")
with st.form("add_song_form"):
    file = st.file_uploader("Upload song file (MP3/WAV)", type=["mp3", "wav"])
    submitted = st.form_submit_button("Add Song")

if submitted:
    if file:
        save_path = os.path.join("songs", file.name)
        with open(save_path, "wb") as f:
            f.write(file.getbuffer())

        # ---- Extract metadata automatically using mutagen ----
        audio = MutagenFile(save_path, easy=True)

        title = audio.get("title", [os.path.splitext(file.name)[0]])[0]
        artist = audio.get("artist", ["Unknown Artist"])[0]
        if artist == "Unknown Artist":
            artist = fetch_artist_from_itunes(title)


        # duration in seconds
        duration = get_duration(save_path)


        
        # Create Song object (with fetched metadata)
        new_song = Song(
            file_path=save_path,
            title=title,
            artist=artist,
            duration=duration
            )
        playlist.add_song(new_song)


        # Save metadata in songs.json
        if os.path.exists(metadata_file):
            with open(metadata_file, "r") as f:
                songs_data = json.load(f)
        else:
            songs_data = []

        songs_data.append({
            "title": title,
            "artist": artist,
            "duration": duration,
            "file_path": save_path
        })

        with open(metadata_file, "w") as f:
            json.dump(songs_data, f, indent=4)

        st.success(f"Added: {new_song} (saved to {save_path})")
    else:
        st.warning("Please upload a song file!")


# -------- Playlist Display --------
st.subheader("📃 Playlist")
if playlist.songs:
    # Convert playlist songs into a DataFrame
    df = pd.DataFrame([{
        "Select": False,
        "Title": song.title,
        "Artist": song.artist,
        "Duration": song.duration
    } for song in playlist.songs])

    edited_df = st.data_editor(
        df,
        hide_index=True,
        num_rows="fixed",
        use_container_width=True,
        column_config={
            "Select": st.column_config.CheckboxColumn("✅ Select"),
            "Title": "🎶 Title",
            "Artist": "👤 Artist",
            "Duration": "⏱ Duration"
        },
        disabled=["Title", "Artist", "Duration"],
    )

    # Get indices of selected songs
    selected_indices = edited_df.index[edited_df["Select"] == True].tolist()

    if st.button("❌ Remove Selected Songs", use_container_width=True):
        if selected_indices:
            metadata_file = "songs/songs.json"
            if os.path.exists(metadata_file):
                with open(metadata_file, "r") as f:
                    songs_data = json.load(f)
            else:
                songs_data = []

            for idx in sorted(selected_indices, reverse=True):
                removed_song = playlist.songs[idx]
                playlist.remove_song(idx)
                songs_data = [s for s in songs_data if s["file_path"] != removed_song.file_path]

                if os.path.exists(removed_song.file_path):
                    os.remove(removed_song.file_path)

            with open(metadata_file, "w") as f:
                json.dump(songs_data, f, indent=4)

            st.success("Selected songs removed successfully!")
            st.rerun()
        else:
            st.warning("No song selected to remove.")
else:
    st.info("No songs in the playlist yet.")



# -------- Controls --------
st.subheader("▶️ Controls")
col1, col2, col3, col4 = st.columns(4)

if col1.button("⏮️ Previous"):
    song = playlist.prev_song()
    st.session_state.status = f"Now Playing: {song}" if song else "Playlist is empty"

if col2.button("⏭️ Next"):
    song = playlist.next_song()
    st.session_state.status = f"Now Playing: {song}" if song else "Playlist is empty"

if col3.button("🔀 Shuffle Playlist"):
    if playlist.songs:
        playlist.shuffle()
        song = playlist.next_song()
        st.session_state.status = f"Now Playing (Shuffled): {song}"
    else:
        st.warning("Add some songs first.")



if col4.button("❌ Clear Playlist"):
    # delete all files
    for song in playlist.songs:
        if song.file_path and os.path.exists(song.file_path):
            os.remove(song.file_path)

    # reset playlist + metadata
    playlist.songs.clear()
    with open(metadata_file, "w") as f:
        json.dump([], f)

    st.session_state.status = "Playlist cleared!"
    st.rerun()


# -------- Status --------
st.subheader("📢 Status")
current_song = playlist.get_current_song()
if current_song and current_song.file_path:
    file_ext = os.path.splitext(current_song.file_path)[1].lower()
    audio_format = "audio/wav" if file_ext == ".wav" else "audio/mp3"
    st.write(f"🎶 Now Playing {current_song}")
    st.audio(current_song.file_path, format=audio_format)
else:
    st.write(st.session_state.status)

