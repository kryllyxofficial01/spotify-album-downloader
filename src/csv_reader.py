import pandas

from slskd_api import SlskdClient

class CSVReader:
    def __init__(self, filepath):
        self.filepath = filepath

        self.client = SlskdClient()

        self.data = {}

    def load(self):
        self.data = pandas.read_csv(
            self.filepath,
            usecols = ["Track Name", "Album Name", "Artist Name(s)"]
        )

        self.track_titles = self.data["Track Name"].values.tolist()
        self.track_albums = self.data["Album Name"].values.tolist()
        self.track_artists = self.data["Track Name"].values.tolist()