from celery import shared_task

@shared_task
def test_notification_task():
    print("🔥 Celery task executed successfully!")
    return "done"

@shared_task
def send_ai_daily_notifications():
    print("🔥 send_ai_daily_notifications running")
    return "done"
