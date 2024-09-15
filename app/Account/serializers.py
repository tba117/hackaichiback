from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model

# カスタムユーザーモデルを使用している場合は、取得するユーザーモデルを指定する必要
User = get_user_model()

# 新規アカウント登録
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User  # modelsで定義したUserクラスをベースにする
        fields = ('user_id', 'password', 'username')  # 三つのフィールド入力
        extra_kwargs = {'password': {'write_only': True}}  # 入力時パスワード表示しない

    def create(self, validated_data):
        return User.objects.create_user(
            user_id=validated_data['user_id'],
            password=validated_data['password'],
            username=validated_data['username']
        )
        

# ログイン
class LoginSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=255, write_only=True)  
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        user_id = attrs.get('user_id')
        password = attrs.get('password')
        print(user_id, password)
        if user_id and password:
            # authenticate関数にはusernameとしてuser_idを渡さなければならない
            user = authenticate(request=self.context.get('request'), username=user_id, password=password)
            print(user)
            if not user:
                mag = '提供された認証情報ではログインできません。'
                raise serializers.ValidationError(mag, code='authorization')
        else:
            mag = 'user_idとpasswordを入力してください。'
            raise serializers.ValidationError(mag, code='authorization')
        
        # 認証が成功した場合、attrs 辞書に認証されたユーザーを追加
        attrs['user'] = user
        # attrs 辞書を戻り値として返す。これには、必要な認証情報や追加の検証後のデータが含まれる
        return attrs
            

# ユーザー情報更新
class UserUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30, allow_blank=True)
    self_introduction = serializers.CharField(max_length=300, allow_blank=True)
    department = serializers.CharField(max_length=30, allow_blank=True)
    skil = serializers.CharField(max_length=30, allow_blank=True)
    hobby = serializers.CharField(max_length=30, allow_blank=True)

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.self_introduction = validated_data.get('self_introduction', instance.self_introduction)
        instance.department = validated_data.get('department', instance.department)
        instance.skil = validated_data.get('skil', instance.skil)
        instance.hobby = validated_data.get('hobby', instance.hobby)
        instance.save()
        return instance