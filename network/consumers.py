import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversation_id = None
        self.conversation_group_name = None
        self.User = get_user_model()

    async def connect(self):
        try:
            self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
            self.conversation_group_name = f"chat_{self.conversation_id}"
        except KeyError:
            print("❌ WebSocket rejected: 'conversation_id' missing in URL params.")
            await self.close(code=4001)
            return

        # Join chat group
        await self.channel_layer.group_add(
            self.conversation_group_name,
            self.channel_name
        )

        if self.scope["user"].is_authenticated:
            await self.accept()
            print(f"✅ WebSocket connected for {self.scope['user'].username} "
                  f"to conversation {self.conversation_id}")
        else:
            print("❌ WebSocket rejected: user not authenticated")
            await self.close(code=4001)

    async def disconnect(self, close_code):
        print(f"🔌 WebSocket disconnected (code {close_code})")
        await self.channel_layer.group_discard(
            self.conversation_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')

        if not message:
            print("⚠️ Empty message received, skipping.")
            return

        # Save message to DB
        new_message = await self.save_message(self.scope['user'], message)

        # Broadcast to group
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'chat_message',
                'id': new_message.id,
                'sender': {
                    'id': self.scope['user'].id,
                    'username': self.scope['user'].username,
                    'profile_pics': str(self.scope['user'].profile_pics)
                    if getattr(self.scope['user'], "profile_pics", None) else None,
                },
                'content': new_message.content,
                'timestamp': new_message.timestamp.isoformat(),
            }
        )

    async def chat_message(self, event):
        """Send message event to WebSocket"""
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def save_message(self, user, message):
        """Save message to database and trigger notification"""
        from .models import Message, Conversation
        from network.notifications.service import NotificationService

        conversation = get_object_or_404(Conversation, id=self.conversation_id)

        # Save the message
        new_message = Message.objects.create(
            conversation=conversation,
            sender=user,
            content=message
        )

        # Notify other participants
        other_participants = conversation.participants.exclude(id=user.id)
        for recipient in other_participants:
            NotificationService.create(
                recipient=recipient,
                sender=user,
                notification_type='message',
                message=f"{user.username} sent you a message: {message[:50]}",
                metadata={
                    'conversation_id': conversation.id,
                    'message_id': new_message.id,
                }
            )

        return new_message
