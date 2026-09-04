from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange
from app.extensions import db
from app.models.admission import Room, Bed, Admission
from app.utils.audit import log_audit
from app.utils.decorators import roles_required

rooms_beds_bp = Blueprint('rooms_beds', __name__, url_prefix='/rooms')

class RoomForm(FlaskForm):
    room_number = StringField('Room / Ward Number (e.g. 101, ICU-1)', validators=[DataRequired(), Length(max=20)])
    room_type = SelectField('Ward / Room Classification', choices=[
        ('General Ward', 'General Ward'),
        ('Semi Private', 'Semi Private Room'),
        ('Private', 'Private Deluxe Suite'),
        ('ICU', 'Intensive Care Unit (ICU)'),
        ('Emergency', 'Emergency / Triage Ward')
    ], validators=[DataRequired()])
    floor = SelectField('Floor Location', choices=[
        ('Ground Floor', 'Ground Floor'),
        ('1st Floor', '1st Floor'),
        ('2nd Floor', '2nd Floor'),
        ('3rd Floor', '3rd Floor'),
        ('4th Floor (ICU)', '4th Floor (ICU & Critical Care)')
    ], default='1st Floor')
    daily_charge = FloatField('Standard Daily Stay Charge (₹)', default=1000.0, validators=[NumberRange(min=0.0)])
    total_beds = IntegerField('Number of Beds to Initialize', default=1, validators=[NumberRange(min=1, max=20)])
    submit = SubmitField('Create Room')

class BedAddForm(FlaskForm):
    bed_number = StringField('Bed Label (e.g. Bed A, Bed 101-3)', validators=[DataRequired(), Length(max=20)])
    submit = SubmitField('Add Bed to Room')

@rooms_beds_bp.route('/')
@login_required
def index():
    rooms = Room.query.order_by(Room.floor.asc(), Room.room_number.asc()).all()
    total_beds = Bed.query.count()
    available_beds = Bed.query.filter_by(status='Available').count()
    occupied_beds = Bed.query.filter_by(status='Occupied').count()
    maintenance_beds = Bed.query.filter_by(status='Maintenance').count()
    reserved_beds = Bed.query.filter_by(status='Reserved').count()

    return render_template(
        'rooms_beds/index.html',
        rooms=rooms,
        total_beds=total_beds,
        available_beds=available_beds,
        occupied_beds=occupied_beds,
        maintenance_beds=maintenance_beds,
        reserved_beds=reserved_beds
    )

@rooms_beds_bp.route('/new', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin')
def create_room():
    form = RoomForm()
    if form.validate_on_submit():
        if Room.query.filter_by(room_number=form.room_number.data.strip()).first():
            flash('A room with this room number already exists.', 'danger')
            return render_template('rooms_beds/room_form.html', form=form, title='Add Hospital Room / Ward')

        room = Room(
            room_number=form.room_number.data.strip(),
            room_type=form.room_type.data,
            floor=form.floor.data,
            daily_charge=form.daily_charge.data or 0.0,
            total_beds=form.total_beds.data or 1,
            status='Available'
        )
        db.session.add(room)
        db.session.flush()

        # Initialize Beds automatically
        num_beds = form.total_beds.data or 1
        for i in range(1, num_beds + 1):
            letter = chr(64 + i) if num_beds <= 26 else str(i)
            bed = Bed(
                bed_number=f"Bed {letter}",
                room_id=room.id,
                status='Available'
            )
            db.session.add(bed)

        db.session.commit()
        log_audit('CREATE_ROOM', 'Room Management', f"Created Room {room.room_number} with {num_beds} beds.")
        flash(f"Room '{room.room_number}' and {num_beds} beds initialized successfully.", 'success')
        return redirect(url_for('rooms_beds.index'))

    return render_template('rooms_beds/room_form.html', form=form, title='Add Hospital Room / Ward')

@rooms_beds_bp.route('/<int:room_id>/add-bed', methods=['POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin')
def add_bed(room_id):
    room = Room.query.get_or_404(room_id)
    bed_name = request.form.get('bed_number', '').strip()
    if not bed_name:
        count = room.beds.count() + 1
        bed_name = f"Bed {chr(64 + count) if count <= 26 else count}"

    bed = Bed(bed_number=bed_name, room_id=room.id, status='Available')
    room.total_beds += 1
    db.session.add(bed)
    db.session.commit()

    log_audit('ADD_BED', 'Room Management', f"Added {bed.bed_number} to Room {room.room_number}.")
    flash(f"{bed.bed_number} added to Room {room.room_number}.", 'success')
    return redirect(url_for('rooms_beds.index'))

@rooms_beds_bp.route('/beds/<int:bed_id>/status', methods=['POST'])
@login_required
@roles_required('Super Admin', 'Hospital Admin', 'Nurse')
def update_bed_status(bed_id):
    bed = Bed.query.get_or_404(bed_id)
    new_status = request.form.get('status')

    if bed.status == 'Occupied' and new_status != 'Occupied':
        flash('Cannot change status of an occupied bed directly. Please discharge or transfer the inpatient.', 'danger')
        return redirect(url_for('rooms_beds.index'))

    if new_status in ['Available', 'Reserved', 'Maintenance']:
        bed.status = new_status
        db.session.commit()
        log_audit('UPDATE_BED_STATUS', 'Room Management', f"Changed status of Bed {bed.bed_number} (Room {bed.room.room_number}) to {new_status}.")
        flash(f"Bed {bed.bed_number} status changed to {new_status}.", 'info')

    return redirect(url_for('rooms_beds.index'))
