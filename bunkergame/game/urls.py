from django.urls import path

urlpatterns = [
    path('lobbys_list/', get_lobbys_list, name='lobbys_list'),
]