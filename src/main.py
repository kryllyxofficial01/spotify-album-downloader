import subprocess
import sys
import random
import string
import json

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

if len(sys.argv) < 3:
    print(
        f"""
        Insufficient arguments.

        Usage: {sys.argv[0]} <public Spotify playlist url> <path to destination>
        """
    )

    sys.exit(-1)

SPOTDL_OUTPUT_FORMAT = "flac"
SPOTDL_NAMING_SCHEME = "{album} - {artist}/{track-number} - {title}.{output-ext}"

MAX_CONCURRENT_DOWNLOADS = 3

def run_command(command: list[str]) -> str:
    target = command[2] if command[1] == "download" else " ".join(command)

    try:
        process = subprocess.run(command, capture_output=True, text=True, check=False)

        if process.returncode != 0: return f"failed: {target} ({process.stderr or process.stdout})"
        else: return f"success: {target}"

    except Exception as exception:
        return f"failed: {target} ({exception})"

def extract_album_ids(metadata_filepath: str) -> list[str]:
    if not Path(metadata_filepath).exists():
        print(f"Unable to find metadata file: {metadata_filepath}")
        sys.exit(-1)

    with open(metadata_filepath, "r", encoding="utf-8") as file:
        playlist_data = json.load(file)

    albums = set()

    for track in playlist_data:
        album_id = track.get("album_id")

        if album_id:
            albums.add(album_id)

    return list(albums)

def check_failed_albums(failed_albums_filepath: str) -> None:
    failed = Path(failed_albums_filepath)

    if failed.exists() and failed.stat().st_size > 0:
        with open(failed, "r", encoding="utf-8") as file:
            failed_data = file.readlines()

        print(f"Download result: {len(failed_data) - 1} tracks failed, see {failed.resolve()}")

    else:
       print("No errors, all albums downloaded")

def download_albums(album_ids: list[str], output_directory: str, failed_albums_filepath: str) -> None:
    commands = []

    for album_id in album_ids:
        album_url = f"https://open.spotify.com/album/{album_id}"

        spotdl_command = [
            "spotdl",
            "download",
            album_url,
            "--format", SPOTDL_OUTPUT_FORMAT,
            "--output", f"{output_directory}/{SPOTDL_NAMING_SCHEME}",
            "--save-errors", failed_albums_filepath,
            "--threads", "4"
        ]

        commands.append(spotdl_command)

    total_albums = len(commands)
    completed_albums = 0

    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_DOWNLOADS) as pool:
        futures = { pool.submit(run_command, command): command for command in commands }

        for future in as_completed(futures):
            completed_albums += 1

            percentage = int((completed_albums / total_albums) * 100)

            print(f"[{completed_albums}/{total_albums} ~ {percentage}%] {future.result()}")

def main():
    playlist_url = sys.argv[1]
    output_directory = sys.argv[2]

    if not Path(output_directory).exists():
        print(f"Unable to find output directory: {output_directory}")
        sys.exit(-1)

    custom_id = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    metadata_file = f"playlist_{custom_id}_metadata.spotdl"
    failed_albums_file = f"failed_{custom_id}.txt"

    print("Collecting playlist metadata (this may take a while)...")

    spotdl_save_command = [
        "spotdl",
        "save",
        playlist_url,
        "--save-file", metadata_file,
        "--log-level", "DEBUG"
    ]

    if subprocess.run(spotdl_save_command).returncode != 0:
        print("error: could not get playlist metadata")
        sys.exit(-1)

    album_ids = extract_album_ids(metadata_file)

    print("Downloading albums (this may take a while)...")

    download_albums(album_ids, output_directory, failed_albums_file)

    check_failed_albums(failed_albums_file)

if __name__ == "__main__":
    main()