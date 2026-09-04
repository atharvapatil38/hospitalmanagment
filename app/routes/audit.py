from flask import Blueprint, render_template, request
from flask_login import login_required
from app.models.user import AuditLog, User
from app.utils.decorators import roles_required

audit_bp = Blueprint('audit', __name__, url_prefix='/audit-logs')

@audit_bp.route('/')
@login_required
@roles_required('Super Admin')
def index():
    page = request.args.get('page', 1, type=int)
    module_filter = request.args.get('module', '', type=str)
    action_filter = request.args.get('action', '', type=str)
    search = request.args.get('search', '', type=str).strip()

    query = AuditLog.query
    if module_filter:
        query = query.filter(AuditLog.module == module_filter)
    if action_filter:
        query = query.filter(AuditLog.action == action_filter)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (AuditLog.description.ilike(search_fmt)) |
            (AuditLog.action.ilike(search_fmt)) |
            (AuditLog.module.ilike(search_fmt)) |
            (AuditLog.ip_address.ilike(search_fmt))
        )

    logs = query.order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    
    modules = [r[0] for r in AuditLog.query.with_entities(AuditLog.module).distinct().all() if r[0]]
    actions = [r[0] for r in AuditLog.query.with_entities(AuditLog.action).distinct().all() if r[0]]

    return render_template(
        'audit/index.html',
        logs=logs,
        modules=modules,
        actions=actions,
        module_filter=module_filter,
        action_filter=action_filter,
        search=search
    )
