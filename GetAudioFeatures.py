from Auth import *
import requests
import json
from urllib.parse import urlencode
import numpy as np
import pandas as pd
from pandas import Series, DataFrame


class GetAudioFeatures:
    def __init__(self, top_artists, user):
        new_auth = Auth()
        self.access_token = new_auth.get_access_token()
        self.top_artists = top_artists
        self.user = user

    def get_artist(self, artist_name):

        search_endpoint = 'https://api.spotify.com/v1/search'
        search_headers = {'Authorization': 'Bearer ' + self.access_token,
                          'Accept': 'application/json',
                          'Content-Type': 'application/json'}
        search_data = {'q': artist_name, 'type': 'artist'}
        search_lookup_url = search_endpoint + '?' + urlencode(search_data)

        search_res = requests.get(
            search_lookup_url, headers=search_headers).json()
        return search_res['artists']['items'][0]['id']

    def get_artist_albums(self, id):
        artist_albums = []
        album_endpoint = f'https://api.spotify.com/v1/artists/{id}/albums'
        album_headers = {'Authorization': 'Bearer ' + self.access_token,
                         'Accept': 'application/json',
                         'Content-Type': 'application/json'}

        album_res = requests.get(album_endpoint, headers=album_headers).json()
        for album in album_res['items']:
            artist_albums.append(album['id'])
        return set(artist_albums)

    def get_album_tracks(self, album_id):
        tracks_list = []
        tracks_endpoint = f'https://api.spotify.com/v1/albums/{album_id}/tracks'
        tracks_headers = {'Authorization': 'Bearer ' + self.access_token,
                          'Accept': 'application/json',
                          'Content-Type': 'application/json'}
        tracks_res = requests.get(
            tracks_endpoint, headers=tracks_headers).json()

        for track in tracks_res['items']:
            tracks_list.append([track['id'], track['name'],
                                track['artists'][0]['name'], track['duration_ms']])

        df_new_tracks = DataFrame(tracks_list, columns=[
                                  'track_id', 'track_name', 'artist', 'duration_ms'])
        return df_new_tracks

    def get_audio_features(self, tracks_df):
        tr_list = list(tracks_df['track_id'])
        string = ''
        for i in tr_list:
            string = string + i + ','
        string = string[:-1]

        feats_endpoint = 'https://api.spotify.com/v1/audio-features'
        feats_headers = {'Authorization': 'Bearer ' + self.access_token,
                         'Accept': 'application/json',
                         'Content-Type': 'application/json'}
        feats_data = {'ids': string}
        feats_lookup_url = feats_endpoint + '?' + urlencode(feats_data)

        feats_res = requests.get(
            feats_lookup_url, headers=feats_headers).json()

        feats_list = []
        for feat in feats_res['audio_features']:
            feats_list.append([feat['id'], feat['acousticness'],
                               feat['danceability'], feat['energy'],
                               feat['liveness'], feat['speechiness'],
                               feat['instrumentalness'], feat['valence']])

        df_feats = DataFrame(feats_list, columns=['track_id', 'acousticness', 'danceability', 'energy', 'liveness',
                                                  'speechiness', 'instrumentalness', 'valence'])
        return df_feats

    def main(self):
        np.random.seed(10)
        self.artist_ids = []
        self.all_albums_ids = []
        self.all_tracks = DataFrame(columns=['track_id', 'track_name',
                                             'artist', 'duration_ms'])
        for artist in self.top_artists:
            new_id = self.get_artist(artist)
            self.artist_ids.append(new_id)

        for artist_id in self.artist_ids:
            new_albums = self.get_artist_albums(artist_id)
            self.all_albums_ids.extend(new_albums)

        for album_id in self.all_albums_ids:
            new_tracks_df = self.get_album_tracks(album_id)
            self.all_tracks = pd.concat(
                [self.all_tracks, new_tracks_df], ignore_index=True)
        self.all_tracks['user'] = self.user
        self.all_tracks.drop_duplicates(inplace=True)
        self.all_tracks = self.all_tracks.sample(
            frac=0.5)[:500].reset_index(drop=True)

        df1, df2, df3, df4, df5 = np.array_split(self.all_tracks, 5)
        tracks_batches = [df1, df2, df3, df4, df5]
        feats_dfs = []
        for df in tracks_batches:
            feats = self.get_audio_features(df)
            feats_dfs.append(feats)
        self.all_feats = pd.concat(feats_dfs, ignore_index=True)
        self.final_feats = pd.concat(
            [self.all_tracks, self.all_feats], axis=1, join="inner")
        return self.final_feats


if __name__ == '__main__':
    user1_top_artists = ['Ariana Grande', 'Billie Eilish',
                         'Shawn Mendes', 'Pritam', 'Westlife']
    user2_top_artists = ['Pritam', 'Amit Trivedi',
                         'Vishal-Shekhar', 'The Weeknd', 'Shankar Mahadevan']
    u1 = GetAudioFeatures(user1_top_artists, 'user1')
    u2 = GetAudioFeatures(user2_top_artists, 'user2')
    user1_feats = u1.main()
    user2_feats = u2.main()
    all_audio_feats = pd.concat([user1_feats, user2_feats], ignore_index=True)
    all_audio_feats = all_audio_feats.sample(frac=1).reset_index(drop=True)
    all_audio_feats.to_csv('audio_features.csv')
