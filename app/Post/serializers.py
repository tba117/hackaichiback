from rest_framework import serializers
from ..models import Post

class PostSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.user_id')  # userのIDを出力専用で追加

    class Meta:
        model = Post
        fields = ['user', 'text', 'image', 'created_at']
        read_only_fields = ['user', 'created_at']
        extra_kwargs = {
            'text': {'allow_blank': True},  # テキストが空でも許可
            'image': {'required': False}    # 画像がなくても許可
        }

    def validate(self, data):
        if not data.get('text') and not data.get('image'):
            raise serializers.ValidationError('投稿内容がありません')
        return data