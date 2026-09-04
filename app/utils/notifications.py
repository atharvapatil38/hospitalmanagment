from app.extensions import db
from app.models.user import Notification

def create_notification(title, message, user_id=None, target_role=None, link=None, notification_type='info'):
    """
    Create a notification for a specific user or an entire role.
    """
    try:
        notif = Notification(
            user_id=user_id,
            target_role=target_role,
            title=title,
            message=message,
            link=link,
            notification_type=notification_type
        )
        db.session.add(notif)
        db.session.commit()
        return notif
    except Exception as e:
        db.session.rollback()
        print(f"Error creating notification: {e}")
        return None
