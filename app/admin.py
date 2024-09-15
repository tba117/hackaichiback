from django.contrib import admin
from .models import User, AccessToken, Post

admin.site.register(User)
admin.site.register(AccessToken)
admin.site.register(Post)