import pandas as pd
import spotipy
import streamlit as st
from spotipy.oauth2 import SpotifyClientCredentials
from PIL import Image 

import polarplot
import songrecommender
import ipaddress
ipaddress.ip_address('192.168.0.1')


SPOTIPY_CLIENT_ID='cf628dfe177c45f2a19390ae069a517f'
SPOTIPY_CLIENT_SECRET='d2d9665a97e84ef29843e15a54fea121'

auth_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

st.header('MUZIK')

search_choices = ['Song/track','Artist','Album']
search_select = st.sidebar.selectbox("Your Serach Choice Please",search_choices)

search_keywords = st.text_input(search_select+"(Keyword search)")
button_clicked = st.button("Serach")

search_results = []
tracks = []
artists = []
albums = []

if search_keywords is not None and len(str(search_keywords)) > 0:
    if search_select == 'Song/track':
        st.write("Start Song/track Search")
        tracks = sp.search(q='track:'+search_keywords,type='track', limit=20)
        tracks_list = tracks['tracks']['items']
        if len(tracks_list) > 0:
            for track in tracks_list:
                #st.write(track['name'] + " - By - " + track['artists'][0]['name'])
                search_results.append(track['name'] + " - By - " + track['artists'][0]['name'])


    elif search_select == 'Artist':
        st.write("Start Artist Search")
        artists = sp.search(q='artist:'+search_keywords,type='artist', limit=20)
        artists_list = artists['artists']['items']
        if len(artists_list) > 0:
            for artist in artists_list:
                #st.write(artist['name'])
                search_results.append(artist['name'])

    if search_select == 'Album':
        st.write("Start Album Search")
        albums = sp.search(q='album:'+search_keywords,type='album', limit=20)
        albums_list = albums['albums']['items']
        if len(albums_list) > 0:
            for album in albums_list:
                #st.write(album['name'] + " - By - " + album['artists'][0]['name'])
                #print("Album ID: " + album['id'] + " / Artist ID - " + album['artists'][0]['id'])
                search_results.append(album['name'] + " - By - " + album['artists'][0]['name'])

select_album = None
select_artist = None
select_track = None
if search_select == 'Song/track':
    select_track = st.selectbox("Select your Song/track",search_results)
elif search_select == 'Artist':
    select_artist = st.selectbox("Select your Artist",search_results)
elif search_select == 'Album':
    select_album = st.selectbox("Select your Album",search_results)

if select_track is not None and len(tracks) > 0:
    tracks_list = tracks['tracks']['items']
    tracks_id = None
    if len(tracks_list) > 0:
        for track in tracks_list:
            str_temp = track['name'] + " - By - " + track['artists'][0]['name']
            if str_temp == select_track:
                track_id = track['id']
                track_album = track['album']['name']
                img_album = track['album']['images'][1]['url']
                st.write(track_id,track_album,img_album)
                songrecommender.save_album_image(img_album, track_id)
    selected_track_choice = None
    if track_id is not None:
        image = songrecommender.get_album_mage(track_id)
        st.image(image)
        track_choices = ['Song Features','Similar song Recommendations']
        selected_track_choice = st.sidebar.selectbox('Please select track choice: ',track_choices)
        if selected_track_choice == 'Song Features':
            track_features = sp.audio_features(track_id)
            df = pd.DataFrame(track_features,index=[0])
            df_features = df.loc[: ,['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence']]
            st.dataframe(df_features)
            polarplot.feature_plot(df_features)
        elif selected_track_choice == 'Similar song Recommendations':
            token = songrecommender.get_token(SPOTIPY_CLIENT_ID,SPOTIPY_CLIENT_SECRET)
            similar_song_json = songrecommender.get_track_recommendations(track_id,token)
            recommendation_list = similar_song_json['tracks']
            recommendation_list_df = pd.DataFrame(recommendation_list)
            st.dataframe(recommendation_list_df)
            recommendation_df = recommendation_list_df[['name', 'explicit', 'duration_ms', 'popularity']]
            #st.write("Recommandations...")
            songrecommender.song_recommendation_vis(recommendation_df)
        
    else:
        st.write("Please Select The Track from the List")

elif select_album is not None and len(albums) > 0:
    albums_list = albums['albums']['items']
    album_id = None
    album_uri = None
    album_name = None
    if len(albums_list) > 0:
            for album in albums_list:
                str_temp = album['name'] + " - By - " + album['artists'][0]['name']
                if select_album == str_temp:
                    album_id = album['id']
                    album_uri = album['uri']
                    album_name = album['name']
    if album_id is not None and album_uri is not None:
        st.write("Collecting all the tracks for the album :"+album_name)
        album_tracks = sp.album_tracks(album_id)
        df_album_tracks = pd.DataFrame(album_tracks['items'])
        #st.dataframe(df_album_tracks)
        df_tracks_min = df_album_tracks.loc[:,
                        ['id','name','duration_ms','explicit','preview_url']]
        #st.dataframe(df_album_tracks)
        
        for idx in df_tracks_min.index:
            with st.container():
                col1,col2,col3,col4 = st.columns((4,4,1,1))
                col11,col12 = st.columns((8,2))
                col1.write(df_tracks_min['id'][idx])
                col2.write(df_tracks_min['name'][idx])
                col3.write(df_tracks_min['duration_ms'][idx])
                col4.write(df_tracks_min['explicit'][idx])
                if df_tracks_min['preview_url'][idx] is not None:
                    col11.write(df_tracks_min['preview_url'][idx])
                    with col12:
                        st.audio(df_tracks_min['preview_url'][idx],format="audio/mp3")

if select_artist is not None and len(artists) > 0:
    artists = sp.search(q='artist:'+search_keywords,type='artist', limit=20)
    artists_list = artists['artists']['items']
    artist_id = None
    artist_uri = None
    select_artist_choice = None
    if len(artists_list) > 0:
        for artist in artists_list:
            if select_artist == artist['name']:
                artist_id = artist['id']
                artist_uri = artist['uri']

    if artist_id is not None:
        artist_choice = ['Albums','Top Songs']
        select_artist_choice = st.sidebar.selectbox('Select artist choice',artist_choice)
    
    if select_artist_choice is not None :
        if select_artist_choice == 'Albums':
            artist_uri = 'Spotify:artist:'+ artist_id
            album_result = sp.artist_albums(artist_uri,album_type='album')
            all_albums = album_result['items']
            col1,col2,col3 = st.columns((6,4,2))
            for album in all_albums:
                col1.write(album['name'])
                col2.write(album['release_date'])
                col3.write(album['total_tracks'])
        elif select_artist_choice == 'Top Songs':
            artist_uri = 'Spotify:artist:'+ artist_id
            top_song_results = sp.artist_top_tracks(artist_uri)
            for track in top_song_results['tracks']:
                with st.container():
                    col1,col2,col3,col4 = st.columns((4,4,2,2))
                    col11,col12 = st.columns((8,2))
                    col21,col22 = st.columns((6,6))
                    col31,col32 = st.columns((6,6))
                    col1.write(track['id'])
                    col2.write(track['name'])
                    if track['preview_url'] is not None:
                        col11.write(track['preview_url'])
                        with col12:
                            st.audio(track['preview_url'],format="audio/mp3")
                    with col3:
                        def feature_requested():
                            track_features = sp.audio_features(track['id'])
                            df = pd.DataFrame(track_features,index=[0])
                            df_features = df.loc[: ,['acousticness', 'danceability', 'energy', 
                                                     'instrumentalness', 'liveness', 'speechiness', 'valence']]
                            with col21:
                                st.dataframe(df_features)
                            with col31:
                                polarplot.feature_plot(df_features)
                        feature_button_state = st.button('Track Audio Features',key=track['id'],on_click=feature_requested)
                    with col4:
                        def similar_songs_requested():
                            token = songrecommender.get_token(SPOTIPY_CLIENT_ID,SPOTIPY_CLIENT_SECRET)
                            similar_song_json = songrecommender.get_track_recommendations(track['id'],token)
                            recommendation_list = similar_song_json['tracks']
                            recommendation_list_df = pd.DataFrame(recommendation_list)
                            recommendation_df = recommendation_list_df[['name', 'explicit', 'duration_ms', 'popularity']]
                            with col21:
                                st.dataframe(recommendation_list_df)
                            with col31:
                                songrecommender.song_recommendation_vis(recommendation_df)
                        similar_song_state = st.button('Similar Songs',key=track['name'],on_click=similar_songs_requested)
                    st.write('_____________')


