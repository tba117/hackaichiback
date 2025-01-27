from django.db.models import Prefetch
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from ..models import ChatRoom, Chat
from .serializer import ChatRoomSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from ..models import ChatRoom
from .serializer import ChatRoomSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_chat_room(request):
    """
    チャットルームを作成するAPI
    リクエストボディに対象ユーザーの `user_id` を含める必要があります。
    """
    try:
        # リクエストから対象ユーザーIDを取得
        target_user_id = request.data.get("user_id")
        if not target_user_id:
            return Response({"error": "対象ユーザーのIDが指定されていません"}, status=status.HTTP_400_BAD_REQUEST)

        # ログイン中のユーザーを取得
        current_user = request.user

        # 対象ユーザーを取得
        try:
            target_user = User.objects.get(user_id=target_user_id)
        except User.DoesNotExist:
            return Response({"error": "対象ユーザーが見つかりません"}, status=status.HTTP_404_NOT_FOUND)

        # ログイン中のユーザーと対象ユーザーの間のチャットルームが存在するか確認
        chat_room = ChatRoom.objects.filter(
            Q(users=current_user) & Q(users=target_user)
        ).distinct().first()

        if chat_room:
            # 既存のチャットルームが存在する場合、その情報を返す
            serializer = ChatRoomSerializer(chat_room)
            return Response({"message": "既存のチャットルームがあります", "chat_room": serializer.data}, status=status.HTTP_200_OK)

        # 新しいチャットルームを作成
        chat_room = ChatRoom.objects.create(
            name=f"chat_{min(current_user.user_id, target_user.user_id)}_{max(current_user.user_id, target_user.user_id)}"
        )
        chat_room.users.add(current_user, target_user)

        # チャットルームの情報を返す
        serializer = ChatRoomSerializer(chat_room)
        return Response({"message": "チャットルームを作成しました", "chat_room": serializer.data}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_chat_rooms(request):
    """
    現在ログイン中のユーザーが参加しているチャットルームを取得するAPI
    """
    try:
        # ログイン中のユーザーを取得
        current_user = request.user

        # ユーザーが参加しているチャットルームを取得
        chat_rooms = ChatRoom.objects.filter(users=current_user)

        # シリアライズ
        serializer = ChatRoomSerializer(chat_rooms, many=True)

        return Response({"chat_rooms": serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_history(request, room_id):
    try:
        # チャットルームの取得 (関連データを事前取得)
        chat_room = ChatRoom.objects.prefetch_related(
            Prefetch('messages', queryset=Chat.objects.order_by('-timestamp')),
            'users'
        ).get(id=room_id)

        # ユーザーがそのチャットルームのメンバーか確認
        if request.user not in chat_room.users.all():
            return Response({"error": "このチャットルームにアクセスする権限がありません"}, status=status.HTTP_403_FORBIDDEN)

        # シリアライズして返却
        serializer = ChatRoomSerializer(chat_room)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except ChatRoom.DoesNotExist:
        return Response({"error": "チャットルームが存在しません"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
