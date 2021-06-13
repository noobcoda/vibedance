from django.urls import path
from .views import getDance

urlpatterns = [
    path('get-dance',getDance.as_view()),
]