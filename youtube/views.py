from django.shortcuts import render
from rest_framework.views import APIView
from django.http import HttpResponse,JsonResponse
from .credentials import API_KEY
import requests 
from api.models import Room 
from rest_framework.response import Response
from rest_framework import status

class getDance(APIView):
    def post(self,request,format=None):
        r = requests.get('https://www.googleapis.com/youtube/v3/search',params={
            'part':'snippet',
            'maxResults': 1,
            'q': '%s %s dance practise'%(request.data.get('artist'),request.data.get('title')),
            'key': API_KEY,
            'type':'video',
        })

        #before we get the url, we need the video id.

        result = r.json()['items'][0]

        videoId = result['id']['videoId']

        video = requests.get('https://www.googleapis.com/youtube/v3/videos', params={
            'key':API_KEY,
            'part':'snippet',
            'id':videoId,
        })

        first_vid = video.json()['items'][0]
        
        data = {
            'title': first_vid['snippet']['title'],
            'id': first_vid['id'],
            'url': 'https://www.youtube.com/watch?v=%s'%(videoId),
            'thumbnail': first_vid['snippet']['thumbnails']['high']['url']          
        }

        return JsonResponse(data,status=status.HTTP_200_OK)