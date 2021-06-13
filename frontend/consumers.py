from channels.generic.websocket import AsyncWebsocketConsumer
import json 
#resources: https://www.youtube.com/watch?v=F4nwRQPXD8w&list=PLOLrQ9Pn6cazStWmb0DpaNgFz_RzKawo8
class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        #enabling web socket activity/ setting up connection
        #look at routing page
        self.room_code = self.scope['url_route']['kwargs']['roomCode']
        #now we want to group users, allowing us to broadcast messages
        await self.channel_layer.group_add(
            self.room_code,
            self.channel_name
        )
        #the channel_name contains a pointer to the channel layer instance and the channel name that'll reach the consumer

        #during handshake protocol, needs to accept connection first, before sending messages
        await self.accept()
        
    async def disconnect(self, close_code):
        #we just discard the group
        await self.channel_layer.group_discard(
            self.room_code,
            self.channel_name
        )
    
    #recieve the message of consumer from the web socket,
    #send the message to the room group, recieve the message from the room group,
    #send the message to the web socket

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        #if you look at chatroom.html, in chatSocket.send part, we called the message 'message'

        await self.channel_layer.group_send(
            self.room_code,
            {
               'type': 'chat_message',
               'message' : message, 
            }
        )

    async def chatroom_message(self,event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message':message,
        }))