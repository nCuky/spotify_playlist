from spotify_api_client import SpotifyAPIClient as spapi
import spotify_data_set as spdt
from datetime import datetime as dt
import pandas as pd
import log


# import pyspark as sk
# import seaborn as sns  # Plotting

class Logic:

    # region Utility Methods

    @staticmethod
    def get_token(token_path = None):
        if token_path is None:
            token_path = "token"
        token_file = open(token_path, "r")
        token_file_text = token_file.readlines()
        token_file.close()

        return token_file_text

    @staticmethod
    def find_playlist_in_list(playlist_items: list, playlist_name: str):
        """
        Finds a playlist by a given name.
        :return: Tracks' IDs of the found playlist, otherwise None
        """
        for plst in playlist_items:
            if plst['name'] == playlist_name:
                plst_tracks_id = plst['id']
                break

        return plst_tracks_id

    @staticmethod
    def get_tracks_ids(tracks_items: list):
        '''
        Returns the IDs of all tracks in a given list.
        param tracks_items: Track items (objects)
        :return:
        '''
        out = list()
        for trk in tracks_items:
            out.append(trk['track']['id'])

        return out

    @staticmethod
    def get_tracks_names(tracks_items: list):
        out = list()

        for trk in tracks_items:
            out.append(trk['track']['name'])

        return out

    @staticmethod
    def get_tracks_artists(tracks_items: list):
        out = list()

        for trk in tracks_items:
            curr_artists = dict()

            for i, artist in enumerate(trk['track']['artists']):
                # if artist['name'] == 'Henry Purcell':
                #     x = 1

                curr_artists['artist_' + str(i)] = trk['track']['artists'][i]['name']

            out.append(curr_artists)

        return out

    @staticmethod
    def write_df_to_file(df: pd.DataFrame, file_name: str) -> None:
        """
        Writes a given DataFrame to a file.
        :param df: DataFrame to write to a file.
        :param file_name: Name of the desired file to write (without preceding path).
        :return: None.
        """
        file_path = 'data/personal_data/prepared/' + file_name.format(dt.now().strftime("%Y-%m-%d_%H-%M-%S"))
        log.write(log.WRITING_FILE.format(file_path))
        df.to_csv(path_or_buf = file_path,
                  encoding = 'utf-8-sig',  # UTF-8, explicitly signed with a BOM at the start of the file
                  index = False)
        log.write(log.FILE_WRITTEN.format(file_path))

        # Writing to Excel doesn't work yet.

    # endregion Utility Methods

    def __init__(self):
        self.my_spapi = spapi(token = Logic.get_token())
        self.my_spdt: spdt.SpotifyDataSet = None

    def get_artist_audio_features_data(self, name: str):
        artist_id = self.my_spapi.find_artist(name).id
        tracks = self.my_spapi.artist_get_all_tracks(artist_id)
        tracks_ids = [track.id for track in tracks]
        tracks_features = self.my_spapi.get_tracks_audio_features(tracks_ids)

        pd.read_json()

        return tracks_features

    def calc_listen_data_by_key(self) -> None:
        '''
        Aggregates all listened tracks by key, and writes it as a csv file
        :return:
        '''
        self.my_spdt = spdt.SpotifyDataSet(aggr_level = spdt.SpotifyDataSet.AGG_LEVEL_TRACK)
        only_duration = self.my_spdt.get_tracks_listen_data().groupby(spdt.ColNames.SONG_KEY)[
            spdt.ColNames.MS_PLAYED].sum()

        my_results = self.my_spdt.get_tracks_listen_data().drop(columns = spdt.ColNames.MS_PLAYED).groupby(
            spdt.ColNames.SONG_KEY).mean().assign(
            duration_ms = only_duration)

        Logic.write_df_to_file(my_results, "listen_data_by_key.csv")

    def calc_listen_data_mean_key(self):
        '''
        Aggregates all listened tracks by mean key
        :return:
        '''
        self.my_spdt = spdt.SpotifyDataSet(aggr_level = spdt.SpotifyDataSet.AGG_LEVEL_TRACK)
        self.my_spdt.get_tracks_listen_data().groupby(spdt.ColNames.SONG_KEY).mean().to_csv("mean_by_key.csv")

    def collect_all_tracks_to_file(self):
        self.my_spdt = spdt.SpotifyDataSet(aggr_level = spdt.SpotifyDataSet.AGG_LEVEL_TRACK)

        # my_spdt.all_tracks_df
        track_data = self.my_spdt.get_tracks_listen_data()

        # Writing to CSV file:
        track_file_name = 'all_my_tracks_{0}.csv'

        Logic.write_df_to_file(track_data, track_file_name)

    def collect_unique_tracks_triplets_to_file(self):
        self.my_spdt = spdt.SpotifyDataSet(aggr_level = spdt.SpotifyDataSet.AGG_LEVEL_TRACK)

        known_tracks = self.my_spapi.determine_known_track_id(tracks = self.my_spdt.get_tracks_listen_data()[spdt.ColNames.TRACK_ID])


        # Writing to CSV file:
        track_file_name = 'unique_tracks_triplets_{0}.csv'

        Logic.write_df_to_file(known_tracks, track_file_name)

    def count_unique_tracks(tracks_df: pd.DataFrame) -> pd.DataFrame:
        tracks_count = tracks_df.groupby(spdt.SpotifyDataSet.TRACK_ID_COMBO_COL).size().reset_index(
            name = spdt.ColNames.TIMES_LISTENED)

        # another way, returning Series
        # tracks_count = tracks_df.value_counts(subset = spdt.SpotifyDataSet.TRACK_ID_COMBO_COL)

        return tracks_count
