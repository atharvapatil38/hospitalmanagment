from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.extensions import db
from app.models.user import HospitalSetting
from app.forms.settings_forms import HospitalSettingForm
from app.utils.audit import log_audit
from app.utils.decorators import roles_required

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin')
def index():
    form = HospitalSettingForm()

    if request.method == 'GET':
        form.hospital_name.data = HospitalSetting.get_setting('hospital_name', 'CarePlus Multispeciality Hospital')
        form.hospital_email.data = HospitalSetting.get_setting('hospital_email', 'contact@careplus.com')
        form.hospital_phone.data = HospitalSetting.get_setting('hospital_phone', '+1 (800) 555-CARE')
        form.hospital_address.data = HospitalSetting.get_setting('hospital_address', '742 Evergreen Healthcare Blvd, Medical District')
        form.hospital_currency.data = HospitalSetting.get_setting('hospital_currency', '₹')
        form.default_tax_rate.data = float(HospitalSetting.get_setting('default_tax_rate', '5.0') or 5.0)
        form.appointment_duration.data = int(HospitalSetting.get_setting('appointment_duration', '30') or 30)
        form.invoice_footer_note.data = HospitalSetting.get_setting('invoice_footer_note', 'Thank you for choosing CarePlus Hospital. For queries, contact our billing desk.')

    if form.validate_on_submit():
        HospitalSetting.set_setting('hospital_name', form.hospital_name.data.strip(), 'Official Hospital Name')
        HospitalSetting.set_setting('hospital_email', form.hospital_email.data.strip(), 'Contact Email')
        HospitalSetting.set_setting('hospital_phone', form.hospital_phone.data.strip(), 'Helpline Phone')
        HospitalSetting.set_setting('hospital_address', form.hospital_address.data.strip(), 'Physical Address')
        HospitalSetting.set_setting('hospital_currency', form.hospital_currency.data.strip(), 'Currency Symbol')
        HospitalSetting.set_setting('default_tax_rate', str(form.default_tax_rate.data), 'Default Tax Percentage')
        HospitalSetting.set_setting('appointment_duration', str(form.appointment_duration.data), 'Appointment Duration')
        HospitalSetting.set_setting('invoice_footer_note', form.invoice_footer_note.data.strip() if form.invoice_footer_note.data else '', 'Invoice Footer Note')

        log_audit('UPDATE_SETTINGS', 'System Settings', "Updated hospital profile and billing configuration.")
        flash('Hospital system settings saved successfully.', 'success')
        return redirect(url_for('settings.index'))

    return render_template('settings/index.html', form=form)
