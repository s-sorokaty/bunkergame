from django.urls import path
from .views import get_lobbys_list 


urlpatterns = [
    path('lobbys_list/', get_lobbys_list, name='lobbys_list'),
]