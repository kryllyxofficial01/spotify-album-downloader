import subprocess
import sys
import random
import string
import json

from pathlib import Path

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

def run_command(command: list[str]) -> None:
    print(f"Running command: {' '.join(command)}")

    try:
        process = subprocess.Popen(
            command,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT,
            text = True,
            bufsize = 1
        )

        for line in process.stdout:
            print(line, end="")

        process.wait()

        if process.returncode != 0:
            print(
                f"""
                  Error running command: {' '.join(command)}
                """
            )

            sys.exit(-1)

    except FileNotFoundError:
        print(
            f"""
                Unable to run command: {' '.join(command)}
            """
        )

        sys.exit(-1)

def extract_album_ids(metadata_file) -> list[str]:
    if not Path(metadata_file).exists():
        print(
            f"""
                Unable to find metadata file: {metadata_file}
            """
        )

        sys.exit(-1)

    with open(metadata_file, "r", encoding="utf-8") as file:
        playlist_data = json.load(file)

    albums = set()

    for track in playlist_data:
        albums.add(track["album_id"])

    return list(albums)

def check_failed_albums(failed_albums_file) -> None:
    failed = Path(failed_albums_file)

    if failed.exists() and failed.stat().st_size > 0:
        with open(failed, "r", encoding="utf-8") as file:
            failed_data = file.readlines()

        print(
            f"""
            Download result: {len(failed_data) - 1} tracks failed, see {failed.resolve()}
            """
        )

    else:
        print(
            """
            No issues, all files downloaded
            """
        )

def main():
    playlist_url = sys.argv[1]
    output_directory = sys.argv[2]

    if not Path(output_directory).exists():
        print(
            f"""
                Unable to find output directory: {output_directory}
            """
        )

        sys.exit(-1)

    custom_id = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    metadata_file = f"playlist_{custom_id}_metadata.spotdl"
    failed_albums_file = f"failed_{custom_id}.txt"

    spotdl_save_command = ["spotdl", "save", playlist_url, "--save-file", metadata_file]
    run_command(spotdl_save_command)

    album_ids = extract_album_ids(metadata_file)

    for album_id in album_ids:
        spotdl_download_command = [
            "spotdl",
            "https://open.spotify.com/album/" + album_id,
            "--format", SPOTDL_OUTPUT_FORMAT,
            "--output", f"{output_directory}/{SPOTDL_NAMING_SCHEME}",
            "--save-errors", failed_albums_file,
            "--print-errors"
        ]

        run_command(spotdl_download_command)

    check_failed_albums(failed_albums_file)

if __name__ == "__main__":
    main()