#just like for synchronous, there's urls and views.
#for asyn we use routing and consumers.

from django.urls import re_path 
from . import consumers 

#consumers are basically views here
websocket_urlpatterns = [
    re_path(r"^ws/room/(?P<roomCode>[^/]+)/chat", consumers.ChatRoomConsumer.as_asgi()),
]