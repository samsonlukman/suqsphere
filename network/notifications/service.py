from network.models import Notification

class NotificationService:
    @staticmethod
    def create(recipient, sender=None, notification_type='system', message='', metadata=None):
        if recipient and recipient != sender:
            return Notification.objects.create(
                recipient=recipient,
                sender=sender,
                notification_type=notification_type,
                message=message,
                metadata=metadata or {}
            )

    @staticmethod
    def mark_as_read(notification_id, user):
        Notification.objects.filter(id=notification_id, recipient=user).update(is_read=True)
