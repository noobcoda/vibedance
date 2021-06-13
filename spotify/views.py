from django.shortcuts import render, redirect
from .credentials import REDIRECT_URI, CLIENT_ID, CLIENT_SECRET
from django.http import HttpResponse,JsonResponse
from rest_framework.views import APIView
from requests import Request, post
from rest_framework import status
from rest_framework.response import Response
from .util import * 
from api.models import Room 
from .models import Vote

class AuthURL(APIView):
    #gets authorization access
    def get(self,request,format=None):
    #for spotify, scopes allow certain info from the user to be shared
        scopes = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'
        url = Request('GET', 'https://accounts.spotify.com/authorize', params={
            'scope': scopes,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID
        }).prepare().url
        #we're preparing the url, not sending request yet--we want frontend to request
        return Response({'url': url}, status=status.HTTP_200_OK)

#a callback for some info to be returned to

def spotify_callback(request,format=None):
    code = request.GET.get('code')
    error = request.GET.get('error')

    #send request back to access to get the access/refresh tokens of spotify
    response = post('https://accounts.spotify.com/api/token',data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri':REDIRECT_URI,
        'client_id':CLIENT_ID,
        'client_secret':CLIENT_SECRET,
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')
    error = response.get('error')

    if not request.session.exists(request.session.session_key):
        request.session.create()
    update_or_create_user_tokens(request.session.session_key,access_token,token_type,expires_in,refresh_token)
    #if we want to redirect to a different app, we put app_name:name of path (we set this up by ourselves - look at urls.py frontend)
    #but we want the home page, so we do :, and that will bring us to the right place already
    return redirect('frontend:home')

class IsAuthenticated(APIView):
    #just an endpoint we can hit to see if we are authenticated
    def get(self,request,format=None):
        is_authenticated = is_spotify_authenticated(self.request.session.session_key)
        return Response({'status':is_authenticated},status=status.HTTP_200_OK)

class CurrentSong(APIView):
    def get(self,request,format=None):
        room_code = self.request.session.get('room_code')

        #we also want the host of the room, because all of the users may request
        #info about the song (to show on their screen), but not all are hosts
        #we only use host info to get info abt song

        room = Room.objects.filter(code=room_code)
        if room.exists():
            room = room[0]
        else:
            return Response({},status=status.HTTP_404_NOT_FOUND)
        host = room.host #recall that in the table, we save our host as our session key
        endpoint = "player/currently_playing"

        #send a request to spotify
        response = execute_spotify_api_request(host,endpoint)

        if 'error' in response or 'item' not in response:
            #item only comes on if song is currently playing
            return Response({},status=status.HTTP_204_NO_CONTENT)
        
        item = response.get('item')
        #item now stores a dictionary
        duration = item.get('duration')
        progress = response.get('progress_ms')
        album_cover = item.get('album').get('images')[0].get('url')
        is_playing = response.get('is_playing')
        song_id = item.get('id')

        #if multiple artists are playing:
        artist_string = ''
        for i, artist in enumerate(item.get('artists')):
            if i > 0:
                artist_string += ','
            name = artist.get('name')
            artist_string += name 
        
        #creating our own object to send back to frontend
        votes = len(Vote.objects.filter(room=room,song_id=song_id))

        has_updated = self.update_room_song(room,song_id)
        
        data = {
            'title': item.get('name'),
            'artist': artist_string,
            'duration': duration,
            'time':progress,
            'image_url':album_cover,
            'is_playing':is_playing,
            'votes':votes,
            'votes_to_skip':room.votes_to_skip,
            'id':song_id,
            'updated':has_updated,
        }

        return Response(data,status=status.HTTP_200_OK)
    
    def update_room_song(self,room,song_id):
        current_song = room.current_song

        if song_id != current_song:
            room.current_song = song_id
            room.save(update_fields=['current_song'])
            #if updated, must delete the votes for prev song
            votes = Vote.objects.filter(room=room).delete() #use the instance of that room
            return True 
        return False 

#put used when modifying a singular resource which is part of a resources collection
class PauseSong(APIView):
    def put(self,response,format=None): #put as we're updating a value
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)
        if self.request.session.session_key == room.host or room.guest_can_pause:
            pause_song(room.host)
            return Response({},status=status.HTTP_204_NO_CONTENT)
        return Response({},status=status.HTTP_403_FORBIDDEN)

#post used as we're changing something
class SkipSong(APIView):
    def post(self,request,format=None):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)[0]
        votes_to_skip = room.votes_to_skip
        votes = Vote.objects.filter(room=room,song_id=room.current_song) #the current votes for that room
        #we add two parameters, to make sure we're not getting any votes that are old
        #in case there was an error before
        if self.request.session.session_key == room.host or len(votes)+1 >=votes_to_skip:
            #meets the requirements to skip the song.
            #before we skip song, we clear the votes (in case the update_song doesn't work)
            votes.delete()
            skip_song(room.host)
        else:
            vote = Vote(user=self.request.session.session_key,room=room,song_id=room.current_song)
            vote.save()
            #creates a new vote in database

        return Response({},status=status.HTTP_204_NO_CONTENT)
    
class PlaySong(APIView):
    def put(self, response, format=None):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)[0]
        if self.request.session.session_key == room.host or room.guest_can_pause:
            play_song(room.host)
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        return Response({}, status=status.HTTP_403_FORBIDDEN)