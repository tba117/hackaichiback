from django.db import models
import hashlib
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import (BaseUserManager,
                                        AbstractBaseUser,
                                        PermissionsMixin)
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField


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
    hobbys = models.JSONField(blank=True, null=True, default=list)
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
    

def in_30_days():
    return timezone.now() + timedelta(days=30)

class AccessToken(models.Model):
    # ひもづくユーザー
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # アクセストークン(max_lengthが40に設定されている理由は、トークンはsha1でハッシュ化した文字列を設定するため)
    token = models.CharField(max_length=40)
    # アクセス日時
    access_datetime = models.DateTimeField(default=in_30_days)

    def __str__(self):
        # メールアドレスとアクセス日時、トークンが見えるように設定
        dt = timezone.localtime(self.access_datetime).strftime("%Y/%m/%d %H:%M:%S")
        return self.user.user_id + '(' + dt + ') - ' + self.token

    @staticmethod
    def create(user: User):
        # ユーザの既存のトークンを取得
        if AccessToken.objects.filter(user=user).exists():
            # トークンがすでに存在している場合は削除
            AccessToken.objects.filter(user=user).delete()

        # トークン作成（UserID + Password + システム日付のハッシュ値とする）
        dt = timezone.now()
        token_str = user.user_id + user.password + dt.strftime('%Y%m%d%H%M%S%f')
        hash = hashlib.sha1(token_str.encode('utf-8')).hexdigest()

        # トークンをDBに追加
        token = AccessToken.objects.create(
            user=user,
            token=hash,
            access_datetime=dt)

        return token
    

# 投稿モデル
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 投稿者の情報　CASCADE:参照先が消えたら投稿も消える
    text = models.TextField(blank=True)  # テキスト投稿
    image = models.ImageField(upload_to='images/', null=True, blank=True)  # 画像投稿
    created_at = models.DateTimeField(auto_now_add=True)  # 投稿日時

    def __str__(self):
        return f'{self.user.username}({self.id}): {self.text[:30]}'