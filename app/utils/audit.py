from flask import request
from flask_login import current_user
from app.extensions import db
from app.models.user import AuditLog

def log_audit(action, module, description, user_id=None, ip_address=None):
    """
    Record an action in the system audit log.
    """
    try:
        if user_id is None and current_user and current_user.is_authenticated:
            user_id = current_user.id

        if ip_address is None and request:
            ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)

        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            module=module,
            description=description,
            ip_address=ip_address
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Non-blocking audit log failure
        print(f"Error logging audit: {e}")
