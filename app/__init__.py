import os
from flask import Flask, render_template
from config import config
from app.extensions import db, login_manager, csrf
from app.utils.helpers import format_currency, format_date, format_datetime, status_badge_class, get_hospital_setting

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))

    # Ensure instance folder exists safely
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except (OSError, PermissionError):
        pass

    # Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register Custom Template Filters
    app.jinja_env.filters['currency'] = format_currency
    app.jinja_env.filters['format_date'] = format_date
    app.jinja_env.filters['format_datetime'] = format_datetime
    app.jinja_env.filters['status_badge'] = status_badge_class

    # Context Processors for Templates
    @app.context_processor
    def inject_global_vars():
        from flask_login import current_user
        from app.models.user import Notification
        
        unread_notifs = 0
        recent_notifs = []
        if current_user.is_authenticated:
            unread_notifs = Notification.query.filter(
                ((Notification.user_id == current_user.id) |
                (Notification.target_role == current_user.role_name)),
                Notification.is_read == False
            ).count()
            recent_notifs = Notification.query.filter(
                (Notification.user_id == current_user.id) |
                (Notification.target_role == current_user.role_name)
            ).order_by(Notification.created_at.desc()).limit(5).all()

        return {
            'hospital_name': get_hospital_setting('hospital_name', app.config.get('HOSPITAL_NAME', 'CarePlus Hospital')),
            'hospital_email': get_hospital_setting('hospital_email', app.config.get('HOSPITAL_EMAIL', 'contact@careplus.com')),
            'hospital_phone': get_hospital_setting('hospital_phone', app.config.get('HOSPITAL_PHONE', '+1 (800) 555-CARE')),
            'hospital_address': get_hospital_setting('hospital_address', app.config.get('HOSPITAL_ADDRESS', '742 Evergreen Healthcare Blvd')),
            'hospital_currency': get_hospital_setting('hospital_currency', app.config.get('HOSPITAL_CURRENCY', '₹')),
            'unread_notifications_count': unread_notifs,
            'recent_notifications': recent_notifs
        }

    # Register Blueprints
    from app.routes import (
        auth_bp, dashboard_bp, patients_bp, doctors_bp, departments_bp,
        appointments_bp, admissions_bp, rooms_beds_bp, medical_records_bp,
        prescriptions_bp, pharmacy_bp, laboratory_bp, billing_bp,
        inventory_bp, staff_bp, reports_bp, notifications_bp,
        settings_bp, audit_bp, api_bp
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(doctors_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(admissions_bp)
    app.register_blueprint(rooms_beds_bp)
    app.register_blueprint(medical_records_bp)
    app.register_blueprint(prescriptions_bp)
    app.register_blueprint(pharmacy_bp)
    app.register_blueprint(laboratory_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(api_bp)

    # Register Custom Error Handlers
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    return app
