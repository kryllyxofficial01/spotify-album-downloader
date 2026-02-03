import sys

import json
import csv

from pathlib import Path

if len(sys.argv) < 3:
    print("Format: python album_extract.py <path to Spotify data> <playlist name>")
    sys.exit(-1)

data = Path(sys.argv[1], "Playlist1.json")
output_data = "spotify_albums.csv"

rows = []

with open(data, encoding="utf-8") as playlist1_file:
    playlist1_json = json.load(playlist1_file)

    playlists_full_data = playlist1_json["playlists"]

    playlist_name = sys.argv[2]

    playlist_data = next((item for item in playlists_full_data if item["name"] == playlist_name), None)

    if playlist_data:
        album_count = 0

        for track in playlist_data["items"]:
            if track["track"]:
                print(f"Loading track '{track['track']['trackName']}' ...")

                track_album = track["track"]["albumName"]
                track_artist = track["track"]["artistName"]

                album_entry = {
                    "album": track_album,
                    "artist": track_artist
                }

                if album_entry not in rows:
                    rows.append({
                        "album": track_album,
                        "artist": track_artist
                    })

                    album_count += 1

        print(f"\nLoaded {album_count} albums")

    else:
        print(f"No playlist found with the name '{playlist_name}'")

with open(output_data, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["album", "artist"]
    )

    writer.writeheader()
    writer.writerows(rows)