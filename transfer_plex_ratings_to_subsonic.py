import libsonic
from plexapi.server import PlexServer

# Plex settings
plex_url_with_port = 'http://PLEX_SERVER_IP:32400'
plex_token = 'PLEX_TOKEN'
plex_library_name = 'PLEX_LIBRARY_NAME'
plex_path_prefix = '/ROOT_PATH_OF_PLEX_LIBRARY/'

# Subsonic settings
subsonic_url = 'http://SUBSONIC_SERVER_IP'
subsonic_username = 'SUBSONIC_USERNAME'
subsonic_password = 'SUBSONIC_PASSWORD'
subsonic_port = 4040
subsonic_path_prefix = '/ROOT_PATH_OF_SUBSONIC_LIBRARY/'

# Map ratings from Plex's 10-based rating system to Subsonic's 5-based rating system
plexRatingToSubsonicRating = { 
    1: 1,
    2: 1,
    3: 2,
    4: 2,
    5: 3,
    6: 3,
    7: 4,
    8: 4,
    9: 5,
    10: 5
}

musicDict = {}
plex = PlexServer(plex_url_with_port, plex_token)
music = plex.library.section(plex_library_name)
subsonic = libsonic.Connection(subsonic_url, subsonic_username, subsonic_password, port=subsonic_port)

def populate_dictionary():
    print("Getting all indexes from subsonic server...")
    indexes = subsonic.getIndexes()

    for index in indexes['indexes']['index']:
       print("Reading songs from artists starting with " + index['name'] + "...  \r", end='')
       for artist in index['artist']:
            albums = subsonic.getArtist(artist['id'])
            for album in albums['artist']['album']:
                songs = subsonic.getAlbum(album['id'])
                for song in songs['album']['song']:
                    musicDict[song['path'][len(subsonic_path_prefix):]] = song['id']

def copy_ratings():
    print("")
    print("Getting all rated songs from Plex...")
    for track in music.all(libtype='track', filters={"userRating>>": 0}):
        if track.userRating is not None:
            path = track.locations[0][len(plex_path_prefix):]

            if not path in musicDict:
                continue

            newRating = plexRatingToSubsonicRating[track.userRating]
            print("Plex rating " + str(int(track.userRating)) + " to Subsonic rating " + str(newRating) + " for track: " + track.title)
            subsonic.setRating(musicDict[path], newRating)

populate_dictionary()
copy_ratings()
