# network/notifications/utils.py
import requests

def send_push(token, title, message, data=None):
    """
    Sends a push notification via the Expo Push API.
    """
    payload = {
        "to": token,
        "sound": "default",
        "title": title,
        "body": message,
        "data": data or {},
        "priority": "high",
    }

    try:
        response = requests.post(
            "https://exp.host/--/api/v2/push/send",
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        print(f"✅ Push sent successfully to {token[:20]}...")
    except requests.RequestException as e:
        print(f"❌ Failed to send push: {e}")




"""
import requests
from project4.celery import app  # import your celery instance

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"


# ============================================================
# 📱 Celery Task for Push Notification
# ============================================================
@app.task(bind=True, max_retries=3, default_retry_delay=5)
def send_push_task(self, expo_token, title, body, data=None):
    #Send Expo push notification asynchronously via Celery
    message = {
        "to": expo_token,
        "sound": "default",
        "title": title,
        "body": body,
        "data": data or {},
    }
    headers = {"Content-Type": "application/json"}

    try:
        print(f"📩 Sending push to {expo_token} with title '{title}'")
        response = requests.post(EXPO_PUSH_URL, json=message, headers=headers)
        response.raise_for_status()
        print(f"✅ Push sent to {expo_token[:10]}...: {response.text}")
    except Exception as exc:
        print(f"❌ Push error for token {expo_token}: {exc}")
        raise self.retry(exc=exc)  # Retry if fails

"""