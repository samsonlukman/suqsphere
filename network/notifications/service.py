from network.models import Notification, DeviceToken
from network.notifications.utils import send_push  # ✅ this is your Celery task

from django.apps import apps


class NotificationService:
    @staticmethod
    def create(recipient, sender=None, notification_type='system', message='', metadata=None):
        Notification = apps.get_model("network", "Notification")
        if recipient and recipient != sender:
            notification = Notification.objects.create(
                recipient=recipient,
                sender=sender,
                notification_type=notification_type,
                message=message,
                metadata=metadata or {}
            )

            # 🔔 This line schedules the background Expo push
            token_obj = getattr(recipient, "device_token", None)
            if token_obj and token_obj.token:
                send_push.delay(token_obj.token, "🔔 Notification", message)

            return notification
