from django.apps import apps
from network.models import Notification, DeviceToken
from network.notifications.utils import send_push  # ✅ Ensure this is your Expo push utility


class NotificationService:
    @staticmethod
    def create(recipient, sender=None, notification_type='system', message='', metadata=None):
        """
        Create a notification and send a push to all recipient devices.
        """
        if not recipient:
            print("⚠️ Notification not sent — recipient missing.")
            return None

        if recipient == sender:
            print("ℹ️ Skipping self-notification.")
            return None

        metadata = metadata or {}

        # ✅ Create and save notification
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            message=message,
            metadata=metadata
        )

        # 🔔 Send push notifications to all devices of the recipient
        device_tokens = DeviceToken.objects.filter(user=recipient)
        if not device_tokens.exists():
            print(f"ℹ️ No device tokens found for user {recipient}.")
            return notification

        for dt in device_tokens:
            try:
                send_push(
                    token=dt.token,
                    title=f"📢 New {notification_type.capitalize()}!",
                    message=message,
                    data={
                        "notification_id": notification.id,
                        "type": notification_type,
                        "sender_id": sender.id if sender else None,
                        "post_id": metadata.get("post_id"),
                        "product_id": metadata.get("product_id"),
                        "order_id": metadata.get("order_id"),
                    },
                )
                print(f"✅ Push sent to {recipient.username} ({dt.token[:20]}...)")
            except Exception as e:
                print(f"❌ Error sending push to {recipient.username}: {e}")

        return notification
