# network/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from .models import Message, Conversation
from django.shortcuts import get_object_or_404

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    # This is the critical fix. It accepts URL parameters and passes them up.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversation_id = None
        self.conversation_group_name = None

    async def connect(self):
        try:
            self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
            self.conversation_group_name = f"chat_{self.conversation_id}"
        except KeyError:
            print("WebSocket connection rejected: 'conversation_id' not found in URL parameters.")
            await self.close(code=4001)
            return

        # Join the room group
        await self.channel_layer.group_add(
            self.conversation_group_name,
            self.channel_name
        )

        if self.scope["user"].is_authenticated:
            await self.accept()
            print(f"WebSocket connected for user {self.scope['user'].username} to conversation {self.conversation_id}")
        else:
            print("WebSocket connection rejected: User is not authenticated")
            await self.close(code=4001)

    async def disconnect(self, close_code):
        print(f"WebSocket disconnected with code: {close_code}")
        await self.channel_layer.group_discard(
            self.conversation_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')

        if not message:
            return

        new_message = await self.save_message(self.scope['user'], message)

        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'chat.message',
                'id': new_message.id,
                'sender': {
                    'id': self.scope['user'].id,
                    'username': self.scope['user'].username,
                    'profile_pics': str(self.scope['user'].profile_pics) if self.scope['user'].profile_pics else None,
                },
                'content': message,
                'timestamp': new_message.timestamp.isoformat(),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def save_message(self, user, message):
        conversation = get_object_or_404(Conversation, id=self.conversation_id)
        return Message.objects.create(
            conversation=conversation,
            sender=user,
            content=message
        )