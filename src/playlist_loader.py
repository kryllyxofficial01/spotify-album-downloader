import spotipy
from spotipy.oauth2 import SpotifyOAuth

from track_entry import TrackEntry

from constants import Constants

class PlaylistLoader:
    def __init__(self):
        self.spotify = spotipy.Spotify(
            auth_manager = SpotifyOAuth(
                client_id = Constants.CLIENT_ID,
                client_secret = Constants.CLIENT_SECRET,
                redirect_uri = Constants.REDIRECT_URI
            )
        )

        self.limit = 100
        self.offset = 0

        print(f"Authenticator ID: {self.spotify.current_user()['id']}")

    def load(self, playlist_id: str) -> list[TrackEntry]:
        playlist = self.spotify.playlist(playlist_id)
        print(f"Playlist Owner ID: {playlist['owner']['id']}\n")

        tracks: list[TrackEntry] = []

        while True:
            playlist_item_data = self.spotify.playlist_items(
                playlist_id = playlist_id,
                limit = self.limit,
                offset = self.offset
            )

            if not playlist_item_data["items"]:
                break

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

            self.offset += self.limit

        return tracks