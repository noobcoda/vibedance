from django.db import models
import random
import string  

#creating unique code
def generate_unique_code():
    while True:
        newC = ''.join(random.choices(string.ascii_uppercase,k=8))
        if Room.objects.filter(code=newC).count() == 0:
            break
    return newC

class Room(models.Model):
    code = models.CharField(max_length=8,default=generate_unique_code,unique=True)
    host = models.CharField(max_length=50,unique=True)
    guest_can_pause = models.BooleanField(null=False,default=False)
    votes_to_skip = models.IntegerField(null=False,default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    host_name = models.CharField(max_length=20,null=False,default="host")
    current_song = models.CharField(max_length=50, null=True)

class User(models.Model):
    username = models.CharField(max_length=20, unique=False)
    room = models.ForeignKey(Room,on_delete=models.CASCADE)
