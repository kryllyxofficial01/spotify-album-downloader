import json
import csv

from pathlib import Path

data_directory = Path("") # todo: get the path to the extracted zip
output_data = "spotify_albums.csv"

rows = []

for json_file in data_directory.glob("*.json"):
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)

    except Exception:
        continue

    if isinstance(data, dict) and "tracks" in data:
        playlist_name = data.get("name", json_file.stem)

        for track in data["tracks"]:
            rows.append({
                "playlist": playlist_name,
                "track": track.get("trackName"),
                "artist": track.get("artistName"),
                "album": track.get("albumName")
            })

    elif isinstance(data, list):
        for track in data:
            if all(i in track for i in ("trackName", "albumName")):
                rows.append({
                    "playlist": "Library",
                    "track": track.get("trackName"),
                    "artist": track.get("artistName"),
                    "album": track.get("albumName")
                })

with open(output_data, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["playlist", "track", "artist", "album"]
    )

    writer.writeheader()
    writer.writerows(rows)