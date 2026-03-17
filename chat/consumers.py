"""WebSocket consumer for real-time chat."""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'chat_message')

        if message_type == 'chat_message':
            message = await self.save_message(data)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'id': str(message['id']),
                        'sender_id': str(message['sender_id']),
                        'sender_name': message['sender_name'],
                        'content': message['content'],
                        'message_type': message['message_type'],
                        'file_url': message['file_url'],
                        'created_at': message['created_at'],
                    }
                }
            )
        elif message_type == 'read_receipt':
            await self.mark_read(data.get('message_id'))
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'read_receipt',
                    'message_id': data.get('message_id'),
                    'user_id': str(self.scope['user'].id),
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
        }))

    async def read_receipt(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
        }))

    @database_sync_to_async
    def save_message(self, data):
        from .models import Message, ChatRoom
        user = self.scope['user']
        msg = Message.objects.create(
            room_id=self.room_id,
            sender=user,
            content=data.get('content', ''),
            message_type=data.get('message_type', 'text'),
            file_url=data.get('file_url', ''),
        )
        ChatRoom.objects.filter(id=self.room_id).update(last_message_at=timezone.now())
        return {
            'id': msg.id,
            'sender_id': user.id,
            'sender_name': user.displayName or user.username,
            'content': msg.content,
            'message_type': msg.message_type,
            'file_url': msg.file_url,
            'created_at': msg.created_at.isoformat(),
        }

    @database_sync_to_async
    def mark_read(self, message_id):
        from .models import MessageRead
        user = self.scope['user']
        MessageRead.objects.get_or_create(message_id=message_id, user=user)
