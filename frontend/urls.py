from django.urls import path
from .views import index

app_name = 'frontend'

urlpatterns = [
    path('',index,name="home"),
    path('join',index),
    path('create',index),
    path('main',index),
    path('start',index),
    path('watch',index),
    path('room/<str:roomCode>',index), #allows any string after room/
]
