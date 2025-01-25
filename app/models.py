from django.db import models
from django.contrib.auth.models import (BaseUserManager,
                                        AbstractBaseUser,
                                        PermissionsMixin)
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, user_id,  password, **extra_fields):
        """
        通常のユーザーを作成するためのメソッド
        """
        if not user_id:
            raise ValueError('ユーザーIDは必須です')
        user = self.model(user_id=user_id, **extra_fields)
        user.set_password(password) # パスワードをハッシュ化して保存
        user.save(using=self._db)
        return user
    
    def create_superuser(self, user_id, password=None, **extra_fields):
        """
        スーパーユーザー（管理者的な）を作成するためのメソッド
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('スーパーユーザーはis_staff=Trueにしなければいけません')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('スーパーユーザーはis_superuser=Trueにしなければなりません')
        
        return self.create_user(user_id, password, **extra_fields)


# ユーザーモデル
class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=128)
    username = models.CharField(max_length=50)
    self_introduction = models.CharField(max_length=200, blank=True)
    department = models.CharField(max_length=50, blank=True)
    skils = models.JSONField(blank=True, null=True, default=list)
    hobbys = models.JSONField(blank=True, null=True, default=list)  # 例: ["音楽", "映画", "読書"] のように配列形式で保存
    user_manual = models.TextField(blank=True)
    snsid = models.CharField(max_length=50, blank=True)
    matched_users = models.JSONField(default=list, blank=True)  # マッチングしたユーザーIDを保存
    current_match = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name='current_match_user')  # 現在のマッチング相手
    advice = models.JSONField(blank=True, null=True)
    is_active = models.BooleanField(default=True)  # アカウントが有効か
    is_staff = models.BooleanField(default=False)  # 管理画面にアクセス可能か

    objects = UserManager()

    USERNAME_FIELD = 'user_id'  # 認証時に使用するフィールド
    REQUIRED_FIELDS = []  # スーパーユーザー作成時に必要なフィールド

    def __str__(self):
        return self.user_id
    

# チャットモデル
# トークルームモデル
class ChatRoom(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)  # 任意のルーム名
    users = models.ManyToManyField(User, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    unread_count = models.JSONField(default=dict, blank=True)  # ユーザーごとの未読メッセージ数を管理

    def __str__(self):
        if self.name:
            return f"ChatRoom: {self.name}"
        return f"ChatRoom ({', '.join(user.user_id for user in self.users.all())})"


# チャットモデル
class Chat(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')  # どのトークルームか
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')  # メッセージ送信者
    message = models.TextField()  # メッセージ内容
    timestamp = models.DateTimeField(auto_now_add=True)  # メッセージ送信時間
    is_read = models.BooleanField(default=False)  # メッセージが既読かどうか

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'Room {self.room.id} - From {self.sender.user_id}: {self.message[:20]}'