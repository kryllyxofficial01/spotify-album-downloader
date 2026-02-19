import sys

# from playlist_loader import PlaylistLoader

# if len(sys.argv) < 2:
#     print(f"Usage: python {__file__} <playlist id>")

#     sys.exit(-1)

# loader = PlaylistLoader()

# tracks = loader.load(sys.argv[1])

# print(track.track_name for track in tracks)

from csv_reader import CSVReader

if len(sys.argv) < 2:
    print(f"Usage: python {__file__} <path to CSV file>")

reader = CSVReader(sys.argv[1])

reader.load()