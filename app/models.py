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
    is_active = models.BooleanField(default=True)  # アカウントが有効か
    is_staff = models.BooleanField(default=False)  # 管理画面にアクセス可能か

    objects = UserManager()

    USERNAME_FIELD = 'user_id'  # 認証時に使用するフィールド
    REQUIRED_FIELDS = []  # スーパーユーザー作成時に必要なフィールド

    def __str__(self):
        return self.user_id