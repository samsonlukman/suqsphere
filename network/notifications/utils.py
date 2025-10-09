# notifications/utils.py
import requests

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"


# ============================================================
# 📱 Push Notification Helper
# ============================================================
def send_push(expo_token, title, body):
    """Send Expo push notification to a single device."""
    message = {
        "to": expo_token,
        "sound": "default",  # Device handles playback
        "title": title,
        "body": body,
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(EXPO_PUSH_URL, json=message, headers=headers)
        response.raise_for_status()
        print(f"✅ Push sent to {expo_token[:10]}...: {response.text}")
    except Exception as e:
        print(f"❌ Push error for token {expo_token}: {e}")
