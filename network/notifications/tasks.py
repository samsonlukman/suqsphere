from celery import shared_task
import requests
import openai
import os
from dotenv import load_dotenv
from datetime import timedelta
from django.utils import timezone
from network.models import User
from .service import NotificationService
from network.models import Product
from network.notifications.utils import send_push


load_dotenv()


# ============================================================
# 🌅 Daily AI Motivation Task
# ============================================================
@shared_task
def send_ai_motivation_notifications():
    """Send motivational AI messages to all users at 9 AM daily."""
    users = User.objects.all()
    for user in users:
        try:
            prompt = (
                f"Write a short, gentle motivational or reflective message for {user.username} "
                f"about productivity, peace, or balance in life from the Qur'an and Sunnah."
            )

            response = openai.ChatCompletion.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
            )
            ai_message = response.choices[0].message["content"].strip()

            # Save to Notification model
            NotificationService.create(
                recipient=user,
                notification_type="ai_daily",
                message=ai_message,
            )

            # Send Expo push (if device token exists)
            token_obj = getattr(user, "device_token", None)
            if token_obj and token_obj.token:
                send_push(token_obj.token, "🌅 Morning Motivation", ai_message)

        except Exception as e:
            print(f"⚠️ Error sending AI message to {user.username}: {e}")


# ============================================================
# 🛍️ Daily Market Update Task
# ============================================================
@shared_task
def send_market_update_notifications():
    """Send marketplace updates to all users at 12 PM daily."""
    users = User.objects.all()
    since = timezone.now() - timedelta(hours=24)
    recent_products = Product.objects.filter(created_at__gte=since).order_by("-created_at")[:5]

    for user in users:
        try:
            if recent_products.exists():
                product_titles = ", ".join([p.title for p in recent_products])
                market_msg = f"🛍️ See what other Muslims are selling today: {product_titles}."
            else:
                market_msg = "🛍️ Discover what Muslims are buying and selling around you today!"

            # Save to Notification model
            NotificationService.create(
                recipient=user,
                notification_type="daily_market_update",
                message=market_msg,
            )

            # Send Expo push (if device token exists)
            token_obj = getattr(user, "device_token", None)
            if token_obj and token_obj.token:
                send_push(token_obj.token, "🛍️ SuqSphere Market", market_msg)

        except Exception as e:
            print(f"⚠️ Error sending market update to {user.username}: {e}")
