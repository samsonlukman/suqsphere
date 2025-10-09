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
            

            # 🔔 Send push to ALL devices of recipient
            device_tokens = DeviceToken.objects.filter(user=recipient)
            for dt in device_tokens:
                send_push(dt.token, "🔔 Notification", message, data={'notification_id': notification.id})

            return notification
