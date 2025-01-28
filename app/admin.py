from django.contrib import admin
from django.db import transaction
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from .models import User, Chat, ChatRoom

# UserAdminのカスタマイズ
class UserAdmin(admin.ModelAdmin):
    def delete_queryset(self, request, queryset):
        """
        ユーザーを削除する際に関連するトークンも削除します。
        """
        with transaction.atomic():
            for user in queryset:
                # 関連するトークンを削除
                OutstandingToken.objects.filter(user=user).delete()
            # ユーザーを削除
            super().delete_queryset(request, queryset)

# モデルの登録
admin.site.register(User, UserAdmin)
admin.site.register(Chat)
admin.site.register(ChatRoom)
