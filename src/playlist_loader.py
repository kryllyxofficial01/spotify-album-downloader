import spotipy
from spotipy.oauth2 import SpotifyOAuth

from track_entry import TrackEntry

from constants import Constants

class PlaylistLoader:
    spotify: spotipy.Spotify
    scope: str = "playlist-read-private"

    def __init__(self):
        self.spotify = spotipy.Spotify(
            auth_manager = SpotifyOAuth(
                client_id = Constants.CLIENT_ID,
                client_secret = Constants.CLIENT_SECRET,
                redirect_uri = Constants.REDIRECT_URI,
                scope = self.scope
            )
        )

    def load(self, playlist_id: str) -> list[TrackEntry]:
        playlist_item_data = self.spotify.playlist_items(
            playlist_id,
            limit = 100
        )

        tracks: list[TrackEntry] = []

        while playlist_item_data:
            for item in playlist_item_data["items"]:
                track = item["track"]

                if track:
                    tracks.append(
                        TrackEntry(
                            track_name = track["name"],
                            track_artist = ", ".join(artist["name"] for artist in track["artists"]),
                            track_album = track["album"]["name"]
                        )
                    )

            if playlist_item_data["next"]:
                playlist_item_data = self.spotify.next(playlist_item_data)
            else:
                playlist_item_data = None

        return tracks
