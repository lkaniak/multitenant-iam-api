from notification_service import HttpNotificationAdapter, NotificationPort


def get_notifications() -> NotificationPort:
    return HttpNotificationAdapter.from_env()
