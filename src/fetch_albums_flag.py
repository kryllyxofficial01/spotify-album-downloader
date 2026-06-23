import subprocess
import sys
import random
import string

from pathlib import Path

if len(sys.argv) < 3:
    print(f"Usage: {sys.argv[0]} <playlist url> <destination>")
    sys.exit(-1)

SPOTDL_OUTPUT_FORMAT = "flac"
SPOTDL_NAMING_SCHEME = "{album} - {artist}/{track-number} - {title}.{output-ext}"

playlist_url = sys.argv[1]
output_directory = sys.argv[2]

if not Path(output_directory).exists():
    print(f"Unable to find output directory: {output_directory}")
    sys.exit(-1)

custom_id = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

failed_albums_file = f"failed_{custom_id}.txt"

spotdl_download_command = [
    "spotdl",
    "download",
    playlist_url,
    "--format", SPOTDL_OUTPUT_FORMAT,
    "--output", f"{output_directory}/{SPOTDL_NAMING_SCHEME}",
    "--save-errors", failed_albums_file,
    "--threads", "4",
    "--log-level", "DEBUG"
]

print("Downloading albums (this may take a while)...")

subprocess.run(spotdl_download_command)