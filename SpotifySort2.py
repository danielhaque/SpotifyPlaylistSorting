import spotipy
import spotipy.util as util
from datetime import datetime
from dateutil.relativedelta import relativedelta


# Authenticate with the Spotify API
username = 'USER ID'
scope = 'user-library-read playlist-modify-private playlist-modify-public'
client_id = 'CLIENT ID'
client_secret = 'CLIENT SECRET'
redirect_uri = 'http://localhost:8888/callback'
token = util.prompt_for_user_token(username, scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    playlists = {}
    # Create playlists for each semester if they don't already exist
    semesters = [ #Semesters based off of the UT Austin 2017-2021 schedule
        ('Fall 2017', '2017-08-01', '2017-12-31'),
        ('Spring 2018', '2018-01-01', '2018-05-31'),
        ('Summer 2018', '2018-06-01', '2018-08-31'),
        ('Fall 2018', '2018-09-01', '2018-12-31'),
        ('Spring 2019', '2019-01-01', '2019-05-31'),
        ('Summer 2019', '2019-06-01', '2019-08-31'),
        ('Fall 2019', '2019-09-01', '2019-12-31'),
        ('Spring 2020', '2020-01-01', '2020-05-31'),
        ('Summer 2020', '2020-06-01', '2020-08-31'),
        ('Fall 2020', '2020-09-01', '2020-12-31'),
        ('Spring 2021', '2021-01-01', '2021-05-31'),
        ('Summer 2021', '2021-06-01', '2021-08-31')
    ]
    for semester, start_date, end_date in semesters:
        # Check if playlist for semester already exists
        playlists_for_user = sp.user_playlists(username)['items']
        existing_playlist = next((p for p in playlists_for_user if p['name'] == semester), None)
        if existing_playlist:
            playlists[semester] = existing_playlist['id']
        else:
            # Create playlist if it doesn't exist
            playlist = sp.user_playlist_create(username, semester, public=False, description=semester)
            playlists[semester] = playlist['id']
    # Get all liked tracks
    tracks = sp.current_user_saved_tracks(limit=50)
    offset = 0
    while tracks['items'] and offset < 950:
        for item in tracks['items']:
            # Get the time the track was liked
            liked_at = datetime.strptime(item['added_at'], '%Y-%m-%dT%H:%M:%SZ')
            # Add the track to the appropriate semester playlist
            for semester, start_date, end_date in semesters:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                if liked_at >= start_date and liked_at <= end_date:
                    print(f"Adding {item['track']['name']} to {semester} playlist")
                    sp.user_playlist_add_tracks(username, playlists[semester], [item['track']['id']])
        offset += 50
        tracks = sp.current_user_saved_tracks(limit=50, offset=offset)
