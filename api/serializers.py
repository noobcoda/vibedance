#translates the python code into json response
#these serializers are literally what you see when inputting stuff at the beginning

from rest_framework import serializers
from .models import Room, User 

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room 
        fields = ('id','code','host','guest_can_pause','votes_to_skip','created_at','host_name')

# we send a post request (usually when we create something new)
#post requests require a payload
#this serializer makes sure the payload is valid and fits with correct fields to make a room
class CreateRoomSerializer(serializers.ModelSerializer):
    #this will literally show a json format to the user, asking for inputs of guest can pause and votes to skip
    class Meta:
        model = Room 
        fields = ('guest_can_pause','votes_to_skip','host_name')
        #here the fields we want to check are guest_can_pause and votes_to_skip

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('room','username')

class UpdateRoomSerializer(serializers.ModelSerializer):
    code = serializers.CharField(validators=[])
    class Meta:
        model = Room
        fields = ('guest_can_pause','votes_to_skip','code')