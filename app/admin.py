from django.contrib import admin
from .models import User, Chat, ChatRoom

admin.site.register(User, ChatRoom, Chat)