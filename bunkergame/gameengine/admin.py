from django.contrib import admin
from .models import GameEngine, GameUser

admin.site.register([GameEngine, GameUser])
