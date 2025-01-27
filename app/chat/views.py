from django.db.models import Prefetch
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from ..models import ChatRoom, Chat
from .serializer import ChatRoomSerializer


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
