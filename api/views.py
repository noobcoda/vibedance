#TIP: With sessions, you can actually store information relevant to each user/session

from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from rest_framework import generics, status
from .serializers import RoomSerializer, UserSerializer, CreateRoomSerializer, UpdateRoomSerializer
from .models import Room, User
from rest_framework.views import APIView
from rest_framework.response import Response

# Views interact with your database.
#location on webserver we're going to
#this is what we actually see 

class RoomView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class UserView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CreateUserView(APIView):
    serializer_class = UserSerializer

    def post(self,request,format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            username = serializer.data.get('username')
            room_id = serializer.data.get('room')
            room_instance = Room.objects.filter(id=room_id).first()
            if not serializer.is_valid():
                print (serializer.errors)
            #only add user if user does not already exist
            queryset = User.objects.filter(username=username,room=room_instance)
            if not queryset.exists():
                user = User(username=username,room=room_instance)
                user.save()
                return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
            
        return Response({'Room Not Found': 'Invalid Inputs'},status=status.HTTP_404_NOT_FOUND)
    
#apiview allows us to override some methods, like post and stuff
class CreateRoomView(APIView):
    serializer_class = CreateRoomSerializer
    #this line will literally show a json format to the user, asking for inputs of guest can pause and votes to skip
    #inputs then stored in the database 
    def post(self,request,format=None):
        #1) get access to the session id (each user has a different session)

        #to do this, check if the user has a current session with our web server
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        
        serializer = self.serializer_class(data=request.data)
        #this means the serializer will take all our data, serialize it and make it into a nice python format
        #then we can check if the data sent was valid

        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip') 
            host_name = serializer.data.get('host_name')
            host = self.request.session.session_key
        
            #now creating the room--but bear in mind users already in a session
            #for these ppl, we just update the room for them
            #first check if the host is already in another session

            queryset = Room.objects.filter(host=host)
            #because potentially we have two different room codes (one comes from an existing room, the other a new room),
            #we have to update the session's data in both the if and else.
            #here the self.request.session['room_code'] line is for the host, as they're the one who created the room
            
            self.request.session['name'] = host_name
            
            if queryset.exists():
                #update as there's an existing room
                room = queryset[0]
                room.guest_can_pause = guest_can_pause
                room.votes_to_skip = votes_to_skip
                room.host_name = host_name
                room.save(update_fields=['guest_can_pause','votes_to_skip'])
                self.request.session['room_code'] = room.code 
                return Response(RoomSerializer(room).data,status=status.HTTP_200_OK)
            else:
                #create new room
                room = Room(host=host, guest_can_pause=guest_can_pause, votes_to_skip=votes_to_skip, host_name=host_name)
                room.save()
                self.request.session['room_code'] = room.code 
                #now we want to send them back the exact room. By using a serializer!
                return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)
        
        return Response({'Bad Request': 'Invalid data...'}, status=status.HTTP_400_BAD_REQUEST)
    
class GetRoomView(APIView):
    serializer_class = RoomSerializer
    #when we call this view, we must pass a parameter called 'code'
    lookup_url_kwarg = 'code'

    def get(self,request,format=None):
        #getting what the code is 
        code = request.GET.get(self.lookup_url_kwarg)
        #.GET gets data from the request, the .get gets the parameter we sent it
        
        if code != None:
            room = Room.objects.filter(code=code)
            if len(room) > 0:
                data = RoomSerializer(room[0]).data 
                #we serialize the room and get the data of it
                #serializing it just means we can get the data from the fields in that serializer class
                data['is_host'] = (self.request.session.session_key == room[0].host)
                return Response(data, status=status.HTTP_200_OK)
            return Response({'Room Not Found': 'Invalid Room Code'},status=status.HTTP_404_NOT_FOUND)
        return Response({'Bad Request': 'Code parameter not found'},status=status.HTTP_400_BAD_REQUEST)

class GetUsersInRoomView(APIView):
    serializer_class = UserSerializer
    lookup_url_kwarg = 'code'

    def get(self,request,format=None):
        listOfUsers = []
        code = request.GET.get(self.lookup_url_kwarg)
        if code!=None:
            users = User.objects.filter(room__code=code)#all users with that room code. #do this method as foreign key is used
            if users.exists():
                for u in users.all():
                    listOfUsers.append(u.username)
            data = {
                'userList': listOfUsers,
                'totalAmount': len(users)
                }
            return JsonResponse(data,status=status.HTTP_200_OK)
        return Response({'Bad Request': 'Code parameter not found'},status=status.HTTP_400_BAD_REQUEST)

class JoinRoom(APIView):
    #using a post request, because we're posting that we're joining a room
    def post(self, request, format=None):
        #first check if user has an active session. if none, we create one for them
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
    
        #for post requests, we can just use .data, instead of .GET
        code = request.data.get('code')

        if code != None:
            room_result = Room.objects.filter(code=code)
            if len(room_result) > 0:
                room = room_result[0]
                #now to tell backend that the user (the session) is in this current room. We make a new variable called 'room_code'
                self.request.session['room_code'] = code #see tip line 1
                #therefore if a user accidentally closes the tab, but still in session, they will go back to that room
                return Response({'Message': 'Room successfully joined'},status=status.HTTP_200_OK)
            return Response({'Bad Request': 'Invalid room code'},status=status.HTTP_400_BAD_REQUEST)
        return Response({'Bad Request': 'Invalid post data, did not find such room'},status=status.HTTP_400_BAD_REQUEST)
    
class UserInRoom(APIView):
    #dont need to do the class_Serializer = blah because we don't need that api screen thing
    #send a get request to the endpoint, ask to see if user already in session
    def get(self,request,format=None):
        #make sure we have a session
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        #using python dictionary
        data = {
            'code': self.request.session.get('room_code') #see line 109
        }
        #if we're not in a room, we return 'none'
        return JsonResponse(data, status=status.HTTP_200_OK)

class LeaveRoom(APIView):
    #post request, because we're changing/ updating server
    def post(self,request,format=None):
        if 'room_code' in self.request.session:
            self.request.session.pop('room_code')
            #check if user is host; if user is host, whole room deleted
            id = self.request.session.session_key
            room_results = Room.objects.filter(host=id)
            if len(room_results) > 0:
                #a host
                room = room_results[0]
                room.delete()
        return Response({'Message':'Success'}, status=status.HTTP_200_OK)

class UpdateView(APIView):
    serializer_class = UpdateRoomSerializer
    
    #patch used for changes
    def patch(self,request,format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        #passing our data to the serializer to check if it's valid
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            code = serializer.data.get('code')

            queryset = Room.objects.filter(code=code)
            if not queryset.exists():
                return Response({'msg': 'Room not found'},status=status.HTTP_404_NOT_FOUND)
            else:
                room = queryset[0]
                #want to make sure only the host can update it
                user_id = self.request.session.session_key
                if room.host != user_id:
                    return Response({'msg':'You are not the host'},status=status.HTTP_403_FORBIDDEN)
                room.guest_can_pause = guest_can_pause 
                room.votes_to_skip = votes_to_skip 
                room.save(update_fields=['guest_can_pause','votes_to_skip'])
                return Response(RoomSerializer(room).data,status=status.HTTP_200_OK)

        return Response({'Bad Request': 'Invalid Data...'},status=status.HTTP_400_BAD_REQUEST)
