
"""
This code makes a Spotify playlist from a combination of Spotify data and user input.
First, the user's favorite genre is found. Then their favorite artists in that genre are found.
The user selects an artist of their choice and then a song from that artist.
Next, the user searches another artist outside of their favorite genre and selects another song.
The data from the two selections are used to make song recommendations.
These recommendations are then added to a playlist on Spotify.
"""

# Libraries used in the final code.
import os
import sys
import spotipy
import spotipy.util as util
from statistics import mode, StatisticsError
import time

"""
Data from the Spotify API is outputted in JSON. 
These libraries were solely used to figure out how to access data in JSON format.
For that reason, they are not called in the final code.
"""
# import json
# from json.decoder import JSONDecodeError
# print(json.dumps(VARIABLE, sort_keys=True, indent=4))


# AUTHORIZATION FLOW FOR SPOTIFY API

# Get username
username = sys.argv[1]

# Permits Spotify API to access users' favorite music and make changes to users' profile.
scope = 'user-top-read, playlist-modify-public, playlist-modify-private'

# Erase cache and prompt for user permission
try:
    token = util.prompt_for_user_token(username, scope)
except:
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username, scope)

# Create spotify_object that calls spotipy library
spotify_object = spotipy.Spotify(auth=token)


# POST-AUTHORIZATION CODE


def main():
    intro()
    main_genre = find_main_genre()
    top_artists_in_main_genre = find_top_artists_in_main_genre(main_genre)
    main_artist = select_artist_in_main_genre(top_artists_in_main_genre)
    user_song1 = select_song_from_main_artist(main_artist)
    artist_id = find_artist(main_genre)
    user_song2 = find_user_song2(artist_id)
    user_song_list = [user_song1, user_song2]
    average_audio_data = extract_audio_data(user_song_list)
    rec_songs = get_song_recs(average_audio_data, user_song_list)
    playlist_id = create_playlist()
    add_recs_to_playlist(rec_songs, playlist_id)


def intro():
    print()
    print("It's time to make you a NEW & FRESH playlist! Let's start off by finding your favorite genre.")
    time.sleep(3)
    print("Running diagnostics...")


# Find the most occurring genre from the genres of the user's top 20 artists
def find_main_genre():
    list_top_genres = []
    for artist in range(20):
        genres_for_top_artists = (spotify_object.current_user_top_artists(20, 0))['items'][artist]['genres']
        num_of_genres = len(genres_for_top_artists)
        for genre in range(num_of_genres):
            top_genre_for_artist = genres_for_top_artists[genre]
            list_top_genres.append(top_genre_for_artist)
    try:
        main_genre = mode(list_top_genres)
    except StatisticsError:
        print()
        main_genre = input("Not enough user information. Please enter your favorite genre: ")
    print()
    print("Your favorite genre is: " + main_genre + "!")
    time.sleep(2)
    return main_genre


# Search through the top 20 artists and only print the artists that align with the main genre
def find_top_artists_in_main_genre(main_genre):
    print("Obtaining more user-specific data...")
    list_top_artists_in_genre = []
    for artist in range(20):
        top_artist = (spotify_object.current_user_top_artists(20, 0))['items'][artist]['name']
        genres_for_top_artists = (spotify_object.current_user_top_artists(20, 0))['items'][artist]['genres']
        num_of_genres = len(genres_for_top_artists)
        for genre in range(num_of_genres):
            top_genre_for_artist = genres_for_top_artists[genre]
            if top_genre_for_artist == main_genre:
                list_top_artists_in_genre.append(top_artist)
    print()
    print("Here's your favorite artist(s) in the " + main_genre + " genre:")
    print()
    time.sleep(2)
    num_of_top_artists_in_main_genre = len(list_top_artists_in_genre)
    for top_artist in range(num_of_top_artists_in_main_genre):
        top_artist_in_genre = list_top_artists_in_genre[top_artist]
        print(str(top_artist + 1) + ": " + top_artist_in_genre)
        time.sleep(.75)
    return list_top_artists_in_genre


# From the list of top artists in the main genre, the user selects one artist
def select_artist_in_main_genre(top_artists_in_main_genre):
    # Makes sure user input is an integer
    while True:
        try:
            print()
            artist_num = int(input("Pick an artist: "))
            break
        except ValueError:
            print("Please enter a number 1-" + str(len(top_artists_in_main_genre) + 1) + ".")
    artist_name = top_artists_in_main_genre[artist_num - 1]
    print()
    print("Retrieving " + artist_name + "'s catalog...")
    time.sleep(3)
    return artist_name


# The user selects one song from the main artist's top 10 songs
def select_song_from_main_artist(main_artist):
    artist_id = spotify_object.search(main_artist, limit=1, type="artist")['artists']['items'][0]['id']
    list_artist_top_tracks = []
    list_user_top_tracks = []
    print()
    print("Ok, here are " + main_artist + "'s most popular songs: ")
    print()
    time.sleep(2)
    # Print the top 10 tracks of selected artist
    for top_tracks in range(10):
        artist_top_track = spotify_object.artist_top_tracks(artist_id)['tracks'][top_tracks]['name']
        list_artist_top_tracks.append(artist_top_track)
        print(str(top_tracks+1) + ": " + artist_top_track)
        time.sleep(.75)
    time.sleep(2)
    print()
    print("Cross-referencing your top tracks with " + main_artist + "'s top tracks...")
    # Checks to see if any of the artist's top 10 tracks falls under one of the user's top 20 tracks
    for u_top_track in range(20):
        user_top_tracks = spotify_object.current_user_top_tracks()['items'][u_top_track]['name']
        list_user_top_tracks.append(user_top_tracks)
    for i in range(20):
        u_track = list_user_top_tracks[i]
        for e in range(10):
            a_track = list_artist_top_tracks[e]
            # If yes, then make that track the selected track.
            if u_track == a_track:
                print("Match found!")
                time.sleep(1)
                print("Adding " + a_track + " by " + main_artist + " to user database...")
                time.sleep(2)
                print("Add successful.")
                a_track_id = spotify_object.artist_top_tracks(artist_id)['tracks']['name' == a_track]['id']
                return a_track_id
    # If no, ask for user input
    while True:
        # Verifies input is an integer
        try:
            user_input_top_track = int(input("No matches found. Please select your favorite song from the list above: "))
            break
        except ValueError:
            print("Please enter a number 1-10.")
    top_track = list_artist_top_tracks[user_input_top_track - 1]
    time.sleep(1)
    print("Adding " + top_track + " by " + main_artist + " to user database...")
    time.sleep(2)
    print("Add successful.")
    top_track_id = spotify_object.artist_top_tracks(artist_id)['tracks'][user_input_top_track - 1]['id']
    return top_track_id


# Allows user to search for any artist
def find_artist(main_genre):
    time.sleep(2)
    print()
    user_artist_query = input("Ok, time to find another song DIFFERENT than your previous. Search for an artist outside the " + main_genre + " genre: ")
    found_user_artist = spotify_object.search(user_artist_query, limit=1, type="artist")['artists']['items'][0]['name']
    while True:
        while True:
            # Ensures user input is an integer
            try:
                confirm_user_artist = int(input("Did you search for " + found_user_artist + " (Y = 1 or N = 2)? "))
                break
            except ValueError:
                print("Please enter 1 or 2.")
        # Asks for user input until the user is satisfied with their search
        while confirm_user_artist == 2:
            print()
            user_artist_query = input(
                "Ok, time to find another song DIFFERENT than your previous. Search for an artist outside the " + main_genre + " genre: ")
            found_user_artist = spotify_object.search(user_artist_query, limit=1, type="artist")['artists']['items'][0][
                'name']
            confirm_user_artist = int(input("Did you search for " + found_user_artist + " (Y = 1 or N = 2)? "))
        found_user_artist_genre = spotify_object.search(user_artist_query, limit=1, type="artist")['artists']['items'][0]['genres']
        # Checks to see if the searched artist overlaps with the main genre output earlier in the code
        in_genre = 0
        for i in range(len(found_user_artist_genre)):
            # If there is overlap, the search starts over.
            if found_user_artist_genre[i] == main_genre:
                time.sleep(1)
                print("The artist selected falls under the " + main_genre + " genre. Try again.")
                in_genre += 1
                time.sleep(1)
        # Otherwise, continue with the searched artist
        if in_genre == 0:
            break
    artist_id = spotify_object.search(user_artist_query, limit=1, type="artist")['artists']['items'][0]['id']
    return artist_id


# Lists out top 10 songs from searched artist and the user selects one of these songs
def find_user_song2(artist_id):
    found_user_artist = spotify_object.artist(artist_id)['name']
    list_artist_top_tracks = []
    time.sleep(1)
    print()
    print("Here are " + found_user_artist + "'s most popular songs: ")
    print()
    time.sleep(1)
    for top_track in range(10):
        artist_top_track = spotify_object.artist_top_tracks(artist_id)['tracks'][top_track]['name']
        list_artist_top_tracks.append(artist_top_track)
        print(str(top_track + 1) + ": " + artist_top_track)
        time.sleep(.75)
    print()
    user_input_top_track = int(input("Please select your favorite song from the list above: "))
    top_track = list_artist_top_tracks[user_input_top_track - 1]
    time.sleep(1)
    print("Adding " + top_track + " by " + found_user_artist + " to user database...")
    time.sleep(2)
    print("Add successful.")
    top_track_id = spotify_object.artist_top_tracks(artist_id)['tracks'][user_input_top_track - 1]['id']
    return top_track_id


# From the chosen songs, audio feature data is collected and averaged to provide target values for song recs
def extract_audio_data(user_song_list):
    time.sleep(2)
    print()
    print("Extracting audio data for selections...")
    audio_feature_list = ['acousticness', 'danceability', 'energy', 'speechiness', 'tempo', 'valence']
    features_list1 = []
    features_list2 = []
    for song in range(len(user_song_list)):
        audio_features = spotify_object.audio_features(user_song_list)[song]
        for feature in range(len(audio_feature_list)):
            get_feature = audio_feature_list[feature]
            feature_value = audio_features[get_feature]
            if song == 0:
                features_list1.append(feature_value)
            if song == 1:
                features_list2.append(feature_value)
    features_list_avg = []
    for i in range(6):
        value1 = features_list1[i]
        value2 = features_list2[i]
        avg = (value1 + value2)/2
        features_list_avg.append(avg)
    return features_list_avg


# Using selected songs and target values for audio features, track recommendations are made
def get_song_recs(average_audio_data, user_song_list):
    time.sleep(2)
    print("Using data to discover similar tracks...")
    list_song_recs = []
    for i in range(20):
        spotify_song_rec = spotify_object.recommendations(seed_tracks=user_song_list, limit=20, target_acousticness=average_audio_data[0], target_danceability=average_audio_data[1], target_energy=average_audio_data[2], target_speechiness=average_audio_data[3], target_tempo=average_audio_data[4], target_valence=[5], min_popularity=40)['tracks'][i]['id']
        list_song_recs.append(spotify_song_rec)
    final_list_song_recs = list(set(list_song_recs))
    final_list_song_recs.extend(user_song_list)
    time.sleep(1)
    print("Complete.")
    return final_list_song_recs


def create_playlist():
    playlist_name = 'python playlist'
    playlist_description = 'Developed using the python coding language.'
    playlist_id = spotify_object.user_playlist_create(username, playlist_name, public=True, description=playlist_description)['id']
    time.sleep(2)
    print()
    print("Creating playlist...")
    return playlist_id


def add_recs_to_playlist(rec_songs, playlist_id):
    final_playlist = spotify_object.user_playlist_add_tracks(username, playlist_id, rec_songs)
    time.sleep(2)
    print("Playlist has been created on Spotify!")
    return final_playlist


if __name__ == '__main__':
    main()