import pytest
from app import create_app
from app.extensions import db
from app.models import Role, User, Department, Doctor, Room, Bed, Patient, Medicine, LabTest

@pytest.fixture(scope='session')
def app():
    """Create and configure a clean testing application instance."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def init_db(app):
    """Set up test database tables and basic roles and users."""
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Seed standard roles
        roles = {}
        for rname in ['Super Admin', 'Hospital Admin', 'Doctor', 'Nurse', 'Receptionist', 'Pharmacist', 'Lab Technician', 'Accountant']:
            r = Role(name=rname, description=f"{rname} test role")
            db.session.add(r)
            roles[rname] = r
        db.session.commit()

        # Seed Admin User
        admin_user = User(
            username='admin_test',
            email='admin@careplus.com',
            full_name='Admin User',
            role_id=roles['Super Admin'].id,
            password='Admin@123',
            is_active=True
        )
        db.session.add(admin_user)

        # Seed Doctor User
        doc_user = User(
            username='doctor_test',
            email='doctor@careplus.com',
            full_name='Dr. Test Physician',
            role_id=roles['Doctor'].id,
            password='Doctor@123',
            is_active=True
        )
        db.session.add(doc_user)

        # Seed Nurse User
        nurse_user = User(
            username='nurse_test',
            email='nurse@careplus.com',
            full_name='Nurse Test',
            role_id=roles['Nurse'].id,
            password='Nurse@123',
            is_active=True
        )
        db.session.add(nurse_user)

        # Seed Receptionist User
        reception_user = User(
            username='reception_test',
            email='reception@careplus.com',
            full_name='Receptionist Test',
            role_id=roles['Receptionist'].id,
            password='Reception@123',
            is_active=True
        )
        db.session.add(reception_user)

        # Seed Pharmacist User
        pharm_user = User(
            username='pharmacy_test',
            email='pharmacy@careplus.com',
            full_name='Pharmacist Test',
            role_id=roles['Pharmacist'].id,
            password='Pharmacy@123',
            is_active=True
        )
        db.session.add(pharm_user)

        # Seed Lab Tech User
        lab_user = User(
            username='lab_test',
            email='lab@careplus.com',
            full_name='Lab Tech Test',
            role_id=roles['Lab Technician'].id,
            password='Lab@123',
            is_active=True
        )
        db.session.add(lab_user)

        # Seed Accountant User
        acc_user = User(
            username='acc_test',
            email='accountant@careplus.com',
            full_name='Accountant Test',
            role_id=roles['Accountant'].id,
            password='Account@123',
            is_active=True
        )
        db.session.add(acc_user)

        # Seed Department
        dept = Department(
            name='Cardiology',
            code='CARD',
            head_doctor_name='Dr. Test Physician',
            phone='+1 555-0100',
            status='Active'
        )
        db.session.add(dept)
        db.session.flush()

        # Seed Doctor Profile
        doctor = Doctor(
            doctor_code='DOC-TEST-01',
            name='Dr. Test Physician',
            email='doctor@careplus.com',
            phone='+1 555-0101',
            department_id=dept.id,
            specialization='Cardiology',
            qualification='MD Cardiology',
            experience_years=10,
            consultation_fee=100.0,
            availability_status='Available',
            user_id=doc_user.id,
            status='Active'
        )
        db.session.add(doctor)

        # Seed Room & Bed
        room = Room(
            room_number='101',
            room_type='General Ward',
            floor='1st Floor',
            daily_charge=50.0,
            total_beds=2,
            status='Available'
        )
        db.session.add(room)
        db.session.flush()

        bed1 = Bed(bed_number='Bed A', room_id=room.id, status='Available')
        bed2 = Bed(bed_number='Bed B', room_id=room.id, status='Available')
        db.session.add_all([bed1, bed2])

        db.session.commit()
        yield db

def login_user(client, email, password):
    """Helper to log in a user during tests."""
    return client.post('/auth/login', data={
        'email': email,
        'password': password
    }, follow_redirects=True)
