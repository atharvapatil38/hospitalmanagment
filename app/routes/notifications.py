from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import Notification

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')

@notifications_bp.route('/')
@login_required
def index():
    notifications = Notification.query.filter(
        (Notification.user_id == current_user.id) |
        (Notification.target_role == current_user.role_name) |
        (Notification.target_role == None)
    ).order_by(Notification.created_at.desc()).all()

    return render_template('notifications/index.html', notifications=notifications)

@notifications_bp.route('/<int:notif_id>/mark-read', methods=['POST'])
@login_required
def mark_read(notif_id):
    notif = Notification.query.get_or_404(notif_id)
    notif.is_read = True
    db.session.commit()
    return redirect(request.referrer or url_for('notifications.index'))

@notifications_bp.route('/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    Notification.query.filter(
        (Notification.user_id == current_user.id) |
        (Notification.target_role == current_user.role_name)
    ).update({'is_read': True})
    db.session.commit()
    flash('All notifications marked as read.', 'info')
    return redirect(request.referrer or url_for('notifications.index'))

@notifications_bp.route('/unread-count')
@login_required
def unread_count():
    count = Notification.query.filter(
        ((Notification.user_id == current_user.id) |
        (Notification.target_role == current_user.role_name)),
        Notification.is_read == False
    ).count()
    return jsonify({'count': count})
