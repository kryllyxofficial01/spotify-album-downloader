import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Ensure registry environment variable is set
REGISTRY_URL = "https://raw.githubusercontent.com/spotiflacapp/SpotiFLAC-Extension/main/registry.json"
os.environ["SPOTIFLAC_REGISTRIES"] = os.getenv("SPOTIFLAC_REGISTRIES", REGISTRY_URL)

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from SpotiFLAC import SpotiFLAC
from SpotiFLAC.extensions import ExtensionManager

# Auto-install/sync extensions on launch
def ensure_extensions():
    mgr = ExtensionManager()
    try:
        installed_exts = mgr.list_installed()
    except Exception:
        installed_exts = []

    installed_ids = {
        ext.id if hasattr(ext, 'id') else ext.get('id') if isinstance(ext, dict) else str(ext)
        for ext in installed_exts
    } if installed_exts else set()

    required = ["spotify-web", "tidal-web", "qobuz-web", "deezer", "amazon"]
    missing = [ext for ext in required if ext not in installed_ids]

    if missing:
        print(f"Installing missing extensions: {missing}...")
        mgr.fetch_registry()
        for ext in missing:
            try:
                mgr.install(ext)
                print(f"Successfully installed {ext}")
            except Exception as e:
                print(f"Failed to install {ext}: {e}")

ensure_extensions()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="playlist-read-private playlist-read-collaborative"
))

playlist_id = "2MZnjwbVsu63BJDwwVTYQk"
output_directory = r"M:\JellyfinContent\Music (media-sync)"

results = sp.playlist_items(playlist_id)
album_urls = set()

while results:
    if isinstance(results, dict) and 'items' in results:
        entries = results['items']
        if isinstance(entries, dict) and 'items' in entries:
            entries = entries['items']
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
        results = sp.next(results)
    else:
        results = None

print(f"\nFound {len(album_urls)} unique albums across the playlist.\n")

def process_album(album_url):
    SpotiFLAC(
        url=album_url,
        output_dir=output_directory,
        services=["deezer", "qobuz-web", "amazon", "tidal-web"],
        filename_format="{album}/{track} - {title}"
    )

async def main():
    album_list = list(album_urls)
    failed_albums = []
    loop = asyncio.get_running_loop()

    for i, album_url in enumerate(album_list, start=1):
        print(f"[{i}/{len(album_list)}] Processing album: {album_url}")
        try:
            await loop.run_in_executor(None, process_album, album_url)
        except Exception as e:
            print(f"[ERROR] Failed to process {album_url}: {e}")
            failed_albums.append(album_url)

    if failed_albums:
        with open("failed_downloads.txt", "w", encoding="utf-8") as f:
            for url in failed_albums:
                f.write(f"{url}\n")
        print(f"\nSaved {len(failed_albums)} failed album URLs to failed_downloads.txt")

if __name__ == "__main__":
    asyncio.run(main())