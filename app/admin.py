from django.contrib import admin
from .models import User, Chat, ChatRoom

admin.site.register(User)
admin.site.register(Chat)
admin.site.register(ChatRoom)