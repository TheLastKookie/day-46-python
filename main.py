import requests
import spotipy
import os
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup

'''
Not perfect by any means. Not 100% accurate with finding the right tracks. Sometimes finds remix or Kidz Bop 
version which isn't what I wanted. I think there is a lot of room for improvement in that regards. Maybe 
checking the artist, the title track and year of your desired song against the one the api gets back and if
it doesn't all match, try a different set of search queries. I noticed that some songs had the title given on
Billboard, but then on Spotify there was extra stuff attached to the title like if it came from a movie or
something so that could have been the cause for the wrong song being chosen by the api.
'''

BILLBOARD_URL = "https://www.billboard.com/charts/hot-100/"
SPOTIPY_CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.environ.get("SPOTIPY_REDIRECT_URI")

scope = "playlist-modify-public"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI, scope=scope))

user_id = sp.current_user()["id"]

target_date = input("Which year do you want to travel back to? Type the date in the format YYYY-MM-DD: ")

new_playlist = sp.user_playlist_create(user=user_id, name=f"{target_date} Billboard 100")
playlist_id = new_playlist["id"]

response = requests.get(url=f"{BILLBOARD_URL}{target_date}")
billboard_webpage = response.text

songs_to_add = []
soup = BeautifulSoup(billboard_webpage, "html.parser")
all_songs = soup.find_all(name="div", class_="o-chart-results-list-row-container")
for n in range(100):
    print(n)
    title = all_songs[n].find(name="h3").getText()
    artist = all_songs[n].find(name="h3").findNext("span").getText()
    try:
        track = sp.search(q=f"track:{title} year:{target_date.split('-')[0]}")
    except spotipy.SpotifyException:
        print(f"{title} by {artist} not found on Spotify.")
    else:
        try:
            track_uri = track["tracks"]["items"][0]["uri"]
        except IndexError:
            print(f"{title} by {artist} not found on Spotify.")
        else:
            songs_to_add.append(track_uri)

sp.playlist_add_items(playlist_id=playlist_id, items=songs_to_add)
