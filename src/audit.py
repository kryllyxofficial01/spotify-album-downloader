import os
import sys

from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

if len(sys.argv) != 3:
    print(f"Usage: python {sys.argv[0]} <playlist ID> <output directory>")

    sys.exit(1)

playlist_id = sys.argv[1]
output_directory = sys.argv[2]

import spotipy
from spotipy.oauth2 import SpotifyOAuth

spotify = spotipy.Spotify(auth_manager = SpotifyOAuth(
    client_id = CLIENT_ID,
    client_secret = CLIENT_SECRET,
    redirect_uri = REDIRECT_URI,
    scope = "playlist-read-private playlist-read-collaborative"
))

print("Fetching tracks from Spotify playlist")

results = spotify.playlist_items(playlist_id)

spotify_tracks = []

while results:
    items = results.get('items', [])

    for entry in items:
        if not isinstance(entry, dict):
            continue

        track = entry.get('item') or entry.get('track')

        if track and isinstance(track, dict):
            track_name = track.get('name')

            artists = ", ".join([artist['name'] for artist in track.get('artists', [])])

            album = track.get('album', {})
            album_name = album.get('name')
            album_url = album.get('external_urls', {}).get('spotify')

            spotify_tracks.append({
                "track_name": track_name,
                "artist_name": artists,
                "album_name": album_name,
                "album_url": album_url
            })

    if results.get('next'):
        results = spotify.next(results)
    else:
        results = None

print(f"Total tracks found in Spotify playlist: {len(spotify_tracks)}")

local_files = set()

if os.path.exists(output_directory):
    for root, dirs, files in os.walk(output_directory):
        for file in files:
            if file.lower().endswith(('.flac', '.mp3', '.m4a', '.opus')):
                local_files.add(file.lower())

                local_files.add(os.path.basename(root).lower())

missing_albums = set()

missing_tracks_count = 0

print("\n--- Auditing Local Library against Spotify ---")
for track in spotify_tracks:
    track_name = track["track_name"]
    track_artist = track["artist_name"]

    album_name = track["album_name"]
    album_url = track["album_url"]

    safe_chars = lambda s: "".join(c for c in s if c not in '<>:"/\\|?*').strip()
    expected_folder = f"{safe_chars(album_name)} - {safe_chars(track_artist)}".lower()
    expected_file_snippet = safe_chars(track_name).lower()

    folder_exists = any(expected_folder in folder for folder in local_files) or os.path.exists(os.path.join(output_directory, f"{safe_chars(album_name)} - {safe_chars(track_artist)}"))

    if not folder_exists:
        missing_tracks_count += 1

        if album_url:
            missing_albums.add(album_url)

        print(f"[MISSING ALBUM/TRACK] {album_name} - {track_artist} :: {track_name}")

print(f"\nAudit complete. Missing tracks: {missing_tracks_count}")

print(f"Unique missing album URLs to fetch: {len(missing_albums)}")

failed_file = "failed_downloads.txt"

if missing_albums:
    with open(failed_file, "w", encoding="utf-8") as file:
        for url in sorted(missing_albums):
            file.write(f"{url}\n")

    print(f"Saved missing album URLs to '{failed_file}'. You can feed this back into your downloader script.")

else:
    if os.path.exists(failed_file):
        os.remove(failed_file)

    print("Everything from the playlist is present locally!")