from rest_framework import serializers
from ..models import ChatRoom, Chat
from ..Account.serializers import UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

# メッセージシリアライザ
class ChatSerializer(serializers.ModelSerializer):
    sender = UserSerializer()  # メッセージ送信者の詳細を含める

    class Meta:
        model = Chat
        fields = ['id', 'sender', 'message', 'timestamp', 'is_read']


# チャットルームシリアライザ
class ChatRoomSerializer(serializers.ModelSerializer):
    messages = ChatSerializer(many=True, read_only=True)  # 関連メッセージを含める
    users = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'users', 'messages', 'created_at', 'unread_count']

    
    def get_users(self, obj):
        from ..Account.serializers import UserSerializer  # ローカルインポート
        return UserSerializer(obj.users.all(), many=True).data