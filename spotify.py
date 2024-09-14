import spotipy
from pprint import pprint
from more_itertools import chunked
from dotenv import load_dotenv
import os

# Used to load .env file that has client_id, secret, and username
load_dotenv()

cid = os.getenv("CLIENT_ID")
secret = os.getenv("CLIENT_SECRET")
username = os.getenv("USERNAME")

# token is used to authenticate user. It will open a webpage athe the redirect URI to sign into spotify with that username
token = spotipy.util.prompt_for_user_token(
    username=username,
    scope='playlist-modify-public', 
    client_id=cid, 
    client_secret=secret, 
    # TODO: Change the redirect URI to match the URI in your API account
    redirect_uri="http://localhost:8888/callback"
)
sp = spotipy.Spotify(auth=token)

# TODO: change this with your own playlist ID
playlist_id = '0ikfh6MfejhlDTb8T4nIjO'

# Creates a dictionary where the key is the decade and the value is a list of songs from that decade.
# That song list is actually a list of tuples, where the first value is the song name and the 
# second value is the track_id. This is done for debugging purposes and readability.
songs_by_decade = {}
offset_n = 0
tracks = sp.playlist_items(playlist_id)['items']
count = 0

# The while loop is done because the spotify API can only handle a certain number of songs in a playlist at once.
# This is what the offset parameter is for. It will loop, taking every 100 songs from the playlist until there 
# aren't any more songs, and then break.
while(tracks):

    tracks = sp.playlist_items(playlist_id, offset=offset_n)['items']
    for track in tracks:
        # The try except is specifically for if you have local files in a playlist. They don't have a spotify_id
        # or any album information, so they need to be filtered out. 
        try:
            count+=1
            track_date = track['track']['album']['release_date']
            # This if statement is added specifically for certain tracks or albums that I believe were removed from spotify,
            # but are still on some playlists. They will not play so this removes them from the track list
            if track_date[:3] + '0' == '0000':
                continue
            if track_date[:3] + '0' in songs_by_decade:
                songs_by_decade[track_date[:3] + '0'].append((track['track']['name'], track['track']['id']))
            else:
                songs_by_decade[track_date[:3] + '0'] = [(track['track']['name'], track['track']['id'])]
        except:
            print(f"Track {track['track']['name']} does not exist")
            continue
    offset_n+=100

# This list is used to write the links to created playlists to a text file.  
new_playlists = []


# This loop creates playlists by decades and adds the appropriate songs to them 
for decade in songs_by_decade:
    print(decade)
    tracks = []
    for song in songs_by_decade[decade]:
        tracks.append(song[1])
    print(f'num_tracks: {len(tracks)}')
    segments = 1

    # Spotify only lets you add 100 tracks to a playlist at once. I used the chunked function from more_itertools 
    # to split up my list of tracks into 50 song increments. Then I can iterate through them to add tracks to 
    # the playlist 50 tracks at a time.
    if len(tracks) > 50:
        segments = len(tracks) // 50
        if len(tracks) % 50 > 0:
            segments+=1
    tracks_chunked = list(chunked(tracks, segments))

    new_playlist_info = sp.user_playlist_create(username,"Nick's " + decade + 's')
    new_playlist_id = new_playlist_info['id']
    print(f'Playlist_id: {new_playlist_id}')
    print(new_playlist_info['external_urls']['spotify'])

    # Add the name of the newly created playlist and its url to a list to print later
    new_playlists.append((new_playlist_info['name'], new_playlist_info['external_urls']['spotify']))

    for chunk in tracks_chunked:
        sp.user_playlist_add_tracks(username, new_playlist_id, chunk)
    
    print('DONE')

# Write to a file that has the name of each playlist, along with a link to said playlist
with open("playlist_links.txt", 'w') as f:
    for line in new_playlists:
        f.write(f'{line[0]}:\n')
        f.write(f'{line[1]}\n')



# pprint(songs_by_decade)
# print(count)

# pprint(sp.user_playlist_create(username,'The 1990s')['id'])