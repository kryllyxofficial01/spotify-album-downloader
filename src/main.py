import os
import sys

import asyncio

from dotenv import load_dotenv

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <playlist ID> <output directory>")

    sys.exit(1)

load_dotenv()

REGISTRY_URL = "https://raw.githubusercontent.com/spotiflacapp/SpotiFLAC-Extension/main/registry.json"
os.environ["SPOTIFLAC_REGISTRIES"] = os.getenv("SPOTIFLAC_REGISTRIES", REGISTRY_URL)

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from SpotiFLAC import SpotiFLAC
from SpotiFLAC.extensions import ExtensionManager

EXTENSIONS = ["spotify-web", "tidal-web", "qobuz-web", "deezer", "amazon"]

def ensure_extensions():
    extension_manager = ExtensionManager()

    try:
        installed = extension_manager.list_installed()
    except Exception:
        installed = []

    installed_ids = {
        extension.id if hasattr(extension, 'id') else extension.get('id') if isinstance(extension, dict) else str(extension) for extension in installed
    } if installed else set()

    required = EXTENSIONS
    missing = [ext for ext in required if ext not in installed_ids]

    if missing:
        print(f"Installing missing extensions: {missing}")

        extension_manager.fetch_registry()

        for extension in missing:
            try:
                extension_manager.install(extension)

                print(f"Successfully installed {extension}")

            except Exception as exception:
                print(f"Failed to install {extension}: {exception}")

                sys.exit(-1)

ensure_extensions()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id = CLIENT_ID,
    client_secret = CLIENT_SECRET,
    redirect_uri = REDIRECT_URI,
    scope = "playlist-read-private playlist-read-collaborative"
))

playlist_id = sys.argv[1]
output_directory = sys.argv[2]

results = spotify.playlist_items(playlist_id)

album_urls = set()

while results:
    if isinstance(results, dict) and 'items' in results:
        entries = results['items']
    else:
        entries = []

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        track = entry.get('item') or entry.get('track')

        if track and isinstance(track, dict):
            album = track.get('album')

            if album and 'external_urls' in album:
                album_url = album['external_urls'].get('spotify')

                if album_url:
                    album_urls.add(album_url)

    if isinstance(results, dict) and results.get('next'):
        results = spotify.next(results)
    else:
        results = None

print(f"\nFound {len(album_urls)} unique albums across the playlist.\n")

def process_target(album_url):
    try:
        SpotiFLAC(
            url = album_url,
            output_dir = output_directory,
            services = EXTENSIONS,
            filename_format = "{album} - {artist}/{track} {title}"
        )

        return True

    except Exception as exception:
        print(f"[ERROR] Engine failure on {album_url}: {exception}")

        return False

async def main():
    album_list = list(album_urls)

    failed_urls = set()

    loop = asyncio.get_running_loop()

    print("=== PASS 1: Downloading Albums ===")

    for i, album_url in enumerate(album_list, start=1):
        print(f"[{i}/{len(album_list)}] Processing album: {album_url}")

        success = await loop.run_in_executor(None, process_target, album_url)

        if not success:
            failed_urls.add(album_url)

    if failed_urls:
        print(f"\n=== PASS 2: Retrying {len(failed_urls)} Failed Item(s) ===")

        still_failed = set()

        for i, retry_url in enumerate(list(failed_urls), start=1):
            print(f"[Retry {i}/{len(failed_urls)}] Attempting: {retry_url}")

            success = await loop.run_in_executor(None, process_target, retry_url)

            if not success:
                still_failed.add(retry_url)

                print(f"[FAILED AGAIN] Could not fetch: {retry_url}")

            else:
                print(f"[RECOVERED] Successfully downloaded: {retry_url}")

        failed_urls = still_failed

    failed_file = "failed_downloads.txt"

    if failed_urls:
        with open(failed_file, "w", encoding="utf-8") as f:
            for url in sorted(failed_urls):
                f.write(f"{url}\n")

        print(f"\nFinished with errors. Saved {len(failed_urls)} unresolved item URL(s) to '{failed_file}'.")

    else:
        if os.path.exists(failed_file):
            os.remove(failed_file)

        print("\nAll albums and tracks processed successfully!")

if __name__ == "__main__":
    asyncio.run(main())