from django.urls import path 
from .views import RoomView,UserView,CreateUserView,CreateRoomView,GetRoomView,JoinRoom, UserInRoom, GetUsersInRoomView, UpdateView, LeaveRoom
#calls main function
urlpatterns = [
    path('',RoomView.as_view()),
    path('user',UserView.as_view()),
    path('create-user',CreateUserView.as_view()),
    path('create-room',CreateRoomView.as_view()),
    path('get-room',GetRoomView.as_view()),
    path('join-room',JoinRoom.as_view()),
    path('user-in-room',UserInRoom.as_view()),
    path('get-users-in-room',GetUsersInRoomView.as_view()),
    path('leave-room',LeaveRoom.as_view()),
    path('update-room',UpdateView.as_view())
]