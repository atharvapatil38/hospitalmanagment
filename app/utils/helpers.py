import csv
import io
from datetime import datetime, date
from flask import Response
from app.models.user import HospitalSetting

def get_hospital_setting(key, default=''):
    return HospitalSetting.get_setting(key, default)

def format_currency(value):
    currency = get_hospital_setting('hospital_currency', '₹')
    try:
        val = float(value or 0)
        return f"{currency}{val:,.2f}"
    except (ValueError, TypeError):
        return f"{currency}0.00"

def format_date(value, format='%b %d, %Y'):
    if not value:
        return 'N/A'
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            return value
    return value.strftime(format)

def format_datetime(value, format='%b %d, %Y %I:%M %p'):
    if not value:
        return 'N/A'
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value
    return value.strftime(format)

def status_badge_class(status):
    status_map = {
        'active': 'bg-success',
        'available': 'bg-success',
        'admitted': 'bg-primary',
        'discharged': 'bg-secondary',
        'completed': 'bg-success',
        'confirmed': 'bg-info text-dark',
        'scheduled': 'bg-warning text-dark',
        'cancelled': 'bg-danger',
        'no show': 'bg-dark',
        'occupied': 'bg-danger',
        'reserved': 'bg-warning text-dark',
        'maintenance': 'bg-secondary',
        'paid': 'bg-success',
        'partially paid': 'bg-warning text-dark',
        'unpaid': 'bg-danger',
        'pending': 'bg-warning text-dark',
        'requested': 'bg-info text-dark',
        'sample collected': 'bg-primary',
        'processing': 'bg-warning text-dark',
        'normal': 'bg-success',
        'high': 'bg-danger',
        'low': 'bg-warning text-dark',
        'critical': 'bg-danger',
        'low stock': 'bg-danger',
        'out of stock': 'bg-dark',
    }
    return status_map.get(str(status).lower(), 'bg-secondary')

def export_csv_response(filename, headers, rows):
    """
    Returns a downloadable CSV streaming Flask Response.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}.csv"}
    )
