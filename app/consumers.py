# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom, Chat, User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']  # URLから取得したroom_nameを取得
        self.room_group_name = f'chat_{self.room_name}'  # グループ名を作成

        print('接続しました1')
        print('room_name', self.room_name)
        print('room_group_name', self.room_group_name)

        # チャットルームに参加
        await self.channel_layer.group_add(
            self.room_group_name,  # チャットルームを識別するグループ名
            self.channel_name  # 現在の WebSocket 接続のチャンネル名
        )

        print('接続しました2')
        print('room_group_name',self.room_group_name)
        print('channel_name', self.channel_name)

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
        sender = await User.objects.get(id=sender_id)
        room = await ChatRoom.objects.get(name=self.room_name)
        await Chat.objects.create(
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
