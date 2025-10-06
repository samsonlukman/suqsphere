import openai
from django.contrib.auth import get_user_model
from .service import NotificationService

User = get_user_model()

openai.api_key = "sk-06036320c8044af6a6a90dc976fdb9b3"
openai.base_url = "https://api.deepseek.com/v1"

from celery import shared_task

@shared_task
def test_notification_task():
    print("Celery task executed successfully!")

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

def haha(a):
    return a + 1