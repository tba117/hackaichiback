from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK
from django.contrib.auth import login, get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, LoginSerializer, UserUpdateSerializer
from ..models import AccessToken

User = get_user_model()

# 新規登録
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # ここでcreate_userが呼ばれる

            # ユーザー登録後にログインさせるための処理
            login(request, user)

            # JWTトークンを生成
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # トークンとユーザー情報を返す
            return Response({
                'detail': "アカウント登録が成功しました。",
                'error': 0,
                'refresh': str(refresh),  # リフレッシュトークン
                'access': access_token,   # アクセストークン
                'user_id': user.user_id   # ユーザーID
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    

# ログイン
class LoginView(APIView):  #ログイン
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            refresh = RefreshToken.for_user(user)  # JWTトークンを生成
            return Response({
                'detail': "ログインが成功しました。",
                'error': 0,
                'refresh': str(refresh),  # リフレッシュトークン
                'access': str(refresh.access_token),  # アクセストークン
                'user_id': user.user_id
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    

# ユーザの詳細取得
class UserDetailView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    def get(self, request, user_id):
        # ユーザー情報の取得
        user = User.objects.filter(user_id=user_id).first()

        if not user:
            # ユーザーが存在しない場合
            return Response({'message': "ユーザーが見つかりません"}, status=404)
        
        response_data = {
            "message": f"{user.user_id}の詳細",
            "user": {
                "user_id": user.user_id,
                "username": user.username,
                "self_introduction": user.self_introduction,
                "department": user.department,
                "skils": user.skils,
                "hobbys": user.hobbys,
                "user_manual": user.user_manual,
                "snsid": user.snsid
            }
        }

        return Response(response_data, status=200)
    

# ユーザー情報更新
class UserUpdateView(APIView):
    # ユーザー認証が必要
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_exempt)
    def patch(self, request):
        # ログインしているユーザーのみが自分の情報を更新できる
        user = request.user  # ログイン中のユーザー情報を取得

        if not user:
            # ユーザーが存在しない場合
            return Response({'message': 'ユーザーが見つかりません'}, status=404)
        
        serializer = UserUpdateSerializer(user, data=request.data, partial=True) # partial=True: すべてのフィールドが送信されなくても更新可
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "message": "ユーザーの更新成功",
                "user": {
                    "user_id": user.user_id,
                    "username": user.username,
                    "self_introduction": user.self_introduction,
                    "department": user.department,
                    "skils": user.skils,
                    "hobbys": user.hobbys,
                    "user_manual": user.user_manual,
                    "snsid": user.snsid,
                }
            }
            return Response(response_data, status=200)
        else:
            return Response({'message': 'ユーザー情報更新失敗', 'errors': serializer.errors}, status=400)


# アカウント削除
class CloseAccountView(APIView):
    # ユーザー認証が必要
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id):
        try:
            user = User.objects.filter(user_id=user_id).first()
            user.delete()
        except User.DoesNotExist:
            return Response({'message': 'ユーザーが見つかりません'}, status=404)
        
        return Response({'message': 'アカウントを削除しました'}, status=200)