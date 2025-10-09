from celery import shared_task
import requests
from network.models import DeviceToken
import openai
from django.contrib.auth import get_user_model
from .service import NotificationService
from network.models import User

@shared_task
def test_push_notification(user_id):
    user = User.objects.get(id=user_id)
    token_obj = getattr(user, "device_token", None)
    if not token_obj:
        print("❌ No device token for user.")
        return

    expo_token = token_obj.token
    message = {
        "to": expo_token,
        "sound": "default",
        "title": "🔥 Push Test",
        "body": "This is a test push from the backend!",
    }

    response = requests.post("https://exp.host/--/api/v2/push/send", json=message)
    print("✅ Push sent:", response.text)

@shared_task
def send_ai_daily_notifications():
    users = User.objects.all()
    for user in users:
        prompt = f"Write a short motivational or reflective message for {user.username} about productivity, peace, or balance in life."

        try:
            response = openai.ChatCompletion.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
            )
            ai_message = response.choices[0].message["content"]

            NotificationService.create(
                recipient=user,
                notification_type='ai_daily',
                message=ai_message
            )

        except Exception as e:
            print(f"Error sending AI daily notification to {user.username}: {e}")

