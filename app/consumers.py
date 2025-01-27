# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom, Chat, User
from asgiref.sync import sync_to_async  # 追加

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']  # URLから取得したroom_nameを取得
        self.room_group_name = f'chat_{self.room_name}'  # グループ名を作成

        if not self.channel_layer:
            print("チャンネルレイヤーが設定されていません。")

        # チャットルームに参加
        await self.channel_layer.group_add(
            self.room_group_name,  # チャットルームを識別するグループ名
            self.channel_name  # 現在の WebSocket 接続のチャンネル名
        )

        await self.accept()

    async def disconnect(self, close_code):
        # チャットルームから離脱
        print('切断しました')
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # WebSocketからメッセージを受信
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = text_data_json['sender_id']

        # データベースに保存
        sender = await sync_to_async(User.objects.get)(id=sender_id)
        room, _ = await sync_to_async(ChatRoom.objects.get_or_create)(name=self.room_name)
        await sync_to_async(Chat.objects.create)(
            room=room,
            sender=sender,
            message=message
        )

        # メッセージをグループにブロードキャスト
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id,
            }
        )

    # グループからメッセージを受信
    async def chat_message(self, event):
        message = event['message']
        sender_id = event['sender_id']

        # WebSocketにメッセージを送信
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id,
        }))
