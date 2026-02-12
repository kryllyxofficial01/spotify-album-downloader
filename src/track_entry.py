class TrackEntry:
    track_name: str
    track_artist: str
    track_album: str

    def __init__(self, track_name: str, track_artist: str, track_album: str):
        self.track_name = track_name
        self.track_artist = track_artist
        self.track_album = track_album