import os
import random
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import db
from app.models import (
    Role, User, HospitalSetting, Department, Doctor, DoctorSchedule,
    Staff, Patient, Appointment, Room, Bed, Admission, DischargeSummary,
    MedicalRecord, Vitals, Prescription, PrescriptionItem, Medicine,
    MedicineBatch, PharmacySale, PharmacySaleItem, LabTest, LabOrder,
    LabResult, Invoice, InvoiceItem, Payment, InventoryItem,
    InventoryTransaction, AuditLog, Notification
)

def seed_database(target_app=None, drop_first=True):
    app = target_app or create_app(os.environ.get('FLASK_ENV', 'development'))
    with app.app_context():
        print("Creating all database tables...")
        if drop_first:
            db.drop_all()
        db.create_all()

        print("Seeding Hospital System Settings...")
        settings = [
            ('hospital_name', 'CarePlus Multispeciality Hospital', 'Official Hospital Name'),
            ('hospital_email', 'contact@careplus.com', 'Hospital Contact Email'),
            ('hospital_phone', '+1 (800) 555-CARE', 'Hospital Helpline Phone'),
            ('hospital_address', '742 Evergreen Healthcare Blvd, Medical District, NY 10001', 'Physical Hospital Address'),
            ('hospital_currency', '₹', 'Currency Symbol'),
            ('default_tax_rate', '5.0', 'Standard Tax Rate Percentage'),
            ('appointment_duration', '30', 'Standard Appointment Slot Duration in Minutes'),
            ('invoice_footer_note', 'Thank you for trusting CarePlus Hospital. In case of queries, please present this invoice at our billing counter.', 'Legal Terms Note')
        ]
        for key, val, desc in settings:
            HospitalSetting.set_setting(key, val, desc)

        print("Seeding Roles...")
        roles_data = [
            ('Super Admin', 'Full unrestricted access to system configurations, user accounts, and security logs.'),
            ('Hospital Admin', 'Operational management of departments, doctors, clinical staff, and inventory.'),
            ('Doctor', 'Clinical management, patient diagnosis, prescription issuance, and test requests.'),
            ('Nurse', 'Inpatient care, vitals monitoring, bed status tracking, and nursing observations.'),
            ('Receptionist', 'Patient registration, appointment scheduling, and front-desk admissions.'),
            ('Pharmacist', 'Medication dispensing, pharmacy catalog, and stock reordering management.'),
            ('Lab Technician', 'Diagnostic sample collection, processing, and laboratory result verification.'),
            ('Accountant', 'Invoicing, payment collections, financial statements, and accounts receivable.')
        ]
        role_objs = {}
        for r_name, r_desc in roles_data:
            role = Role(name=r_name, description=r_desc)
            db.session.add(role)
            role_objs[r_name] = role
        db.session.commit()

        print("Seeding Demo User Accounts...")
        users_data = [
            ('admin', 'admin@careplus.com', 'Admin@123', 'Dr. Alistair Sterling', '+1 (555) 001-0001', 'Super Admin'),
            ('hosp_admin', 'hospital.admin@careplus.com', 'Admin@123', 'Victoria Vance', '+1 (555) 001-0002', 'Hospital Admin'),
            ('doctor', 'doctor@careplus.com', 'Doctor@123', 'Dr. Arthur Conan', '+1 (555) 001-0003', 'Doctor'),
            ('nurse', 'nurse@careplus.com', 'Nurse@123', 'Nurse Sarah Jenkins', '+1 (555) 001-0004', 'Nurse'),
            ('reception', 'reception@careplus.com', 'Reception@123', 'Emily Watson', '+1 (555) 001-0005', 'Receptionist'),
            ('pharmacy', 'pharmacy@careplus.com', 'Pharmacy@123', 'David Miller', '+1 (555) 001-0006', 'Pharmacist'),
            ('lab', 'lab@careplus.com', 'Lab@123', 'Marcus Vance', '+1 (555) 001-0007', 'Lab Technician'),
            ('accountant', 'accountant@careplus.com', 'Account@123', 'Robert Thorne', '+1 (555) 001-0008', 'Accountant')
        ]
        user_objs = {}
        for uname, email, pwd, fname, ph, rname in users_data:
            u = User(
                username=uname,
                email=email,
                full_name=fname,
                phone=ph,
                role_id=role_objs[rname].id,
                password=pwd,
                is_active=True
            )
            db.session.add(u)
            user_objs[uname] = u
        db.session.commit()

        print("Seeding Departments...")
        dept_data = [
            ('Cardiology', 'CARD', 'Dr. Arthur Conan', 'Comprehensive cardiovascular medicine and cardiac care.'),
            ('Neurology', 'NEUR', 'Dr. Elena Rostova', 'Neurological disorders, stroke care, and neurophysiology.'),
            ('Orthopedics', 'ORTH', 'Dr. Harrison Wells', 'Bone, joint surgery, sports medicine, and rehabilitation.'),
            ('Pediatrics', 'PED', 'Dr. Maya Lin', 'Comprehensive infant, child, and adolescent healthcare.'),
            ('General Medicine', 'GMED', 'Dr. Gregory House', 'Internal medicine, chronic illness management, and diagnostics.'),
            ('Dermatology', 'DERM', 'Dr. Clara Oswald', 'Clinical dermatology, aesthetic care, and skin allergies.'),
            ('Gynecology & Obstetrics', 'GYN', 'Dr. Meredith Grey', 'Women health, prenatal care, and reproductive medicine.'),
            ('Emergency & Trauma', 'EMER', 'Dr. John Watson', '24/7 Level-1 trauma response, acute triage, and resuscitation.'),
            ('Radiology & Imaging', 'RAD', 'Dr. Stephen Strange', 'X-Ray, CT scans, Ultrasound, and MRI diagnostics.'),
            ('Pathology & Laboratory', 'PATH', 'Dr. Bruce Banner', 'Clinical biochemistry, hematology, and histopathology.')
        ]
        dept_objs = {}
        for dname, dcode, hod, ddesc in dept_data:
            d = Department(
                name=dname,
                code=dcode,
                head_doctor_name=hod,
                phone=f"+1 (555) 100-{random.randint(1000, 9999)}",
                description=ddesc,
                status='Active'
            )
            db.session.add(d)
            dept_objs[dname] = d
        db.session.commit()

        print("Seeding Doctors...")
        docs_data = [
            ('DOC-001', 'Dr. Arthur Conan', 'doctor@careplus.com', '+1 (555) 234-5678', 'Cardiology', 'Interventional Cardiology', 'MBBS, MD (Cardiology), FACC', 14, 120.0, 'Available', 'Room 201'),
            ('DOC-002', 'Dr. Elena Rostova', 'elena.rostova@careplus.com', '+1 (555) 234-5679', 'Neurology', 'Cognitive Neurology & Stroke', 'MD, PhD, FAAN', 12, 140.0, 'Available', 'Room 202'),
            ('DOC-003', 'Dr. Harrison Wells', 'harrison.wells@careplus.com', '+1 (555) 234-5680', 'Orthopedics', 'Joint Replacement & Arthroscopy', 'MS (Ortho), MCh, FRCS', 16, 110.0, 'Available', 'Room 203'),
            ('DOC-004', 'Dr. Maya Lin', 'maya.lin@careplus.com', '+1 (555) 234-5681', 'Pediatrics', 'Pediatric Pulmonology', 'MD (Pediatrics), DCH', 9, 85.0, 'Available', 'Room 204'),
            ('DOC-005', 'Dr. Gregory House', 'gregory.house@careplus.com', '+1 (555) 234-5682', 'General Medicine', 'Infectious Diseases & Nephrology', 'MD (Internal Med)', 20, 150.0, 'Busy', 'Room 205'),
            ('DOC-006', 'Dr. Clara Oswald', 'clara.oswald@careplus.com', '+1 (555) 234-5683', 'Dermatology', 'Dermatopathology & Laser', 'MD (Dermatology)', 8, 90.0, 'Available', 'Room 206'),
            ('DOC-007', 'Dr. Meredith Grey', 'meredith.grey@careplus.com', '+1 (555) 234-5684', 'Gynecology & Obstetrics', 'Maternal-Fetal Medicine', 'MS (OB/GYN), FACOG', 11, 100.0, 'Available', 'Room 207'),
            ('DOC-008', 'Dr. John Watson', 'john.watson@careplus.com', '+1 (555) 234-5685', 'Emergency & Trauma', 'Emergency Critical Care', 'MD (Emergency Med)', 15, 95.0, 'Available', 'ER-Consult-1'),
            ('DOC-009', 'Dr. Stephen Strange', 'stephen.strange@careplus.com', '+1 (555) 234-5686', 'Radiology & Imaging', 'Diagnostic Radiology & MRI', 'MD (Radiology), FRCR', 13, 130.0, 'Available', 'Rad-Suite-A'),
            ('DOC-010', 'Dr. Bruce Banner', 'bruce.banner@careplus.com', '+1 (555) 234-5687', 'Pathology & Laboratory', 'Clinical Pathology & Genetics', 'MD, PhD (Pathology)', 18, 105.0, 'Available', 'Lab-Office-1')
        ]
        doc_objs = []
        for dcode, dname, demail, dphone, deptname, spec, qual, exp, fee, av_st, rnum in docs_data:
            doc = Doctor(
                doctor_code=dcode,
                name=dname,
                email=demail,
                phone=dphone,
                department_id=dept_objs[deptname].id,
                specialization=spec,
                qualification=qual,
                experience_years=exp,
                consultation_fee=fee,
                availability_status=av_st,
                available_days='Mon,Tue,Wed,Thu,Fri',
                available_time_start='09:00',
                available_time_end='17:00',
                room_number=rnum,
                bio=f"{dname} is a senior specialist in {deptname} with over {exp} years of clinical expertise.",
                status='Active'
            )
            # Link user if matching email
            if demail == 'doctor@careplus.com':
                doc.user_id = user_objs['doctor'].id
            db.session.add(doc)
            doc_objs.append(doc)
        db.session.commit()

        print("Seeding Hospital Staff...")
        staff_data = [
            ('STF-001', 'Nurse Sarah Jenkins', 'nurse@careplus.com', '+1 (555) 300-0001', 'Nurse', 'General Medicine', 3800.0, 'B.Sc Nursing, Critical Care Certified'),
            ('STF-002', 'Nurse Rachel Green', 'rachel.green@careplus.com', '+1 (555) 300-0002', 'Nurse', 'Cardiology', 3900.0, 'B.Sc Nursing (Cardiac Care)'),
            ('STF-003', 'Emily Watson', 'reception@careplus.com', '+1 (555) 300-0003', 'Receptionist', 'General Medicine', 2900.0, 'B.A. Healthcare Administration'),
            ('STF-004', 'David Miller', 'pharmacy@careplus.com', '+1 (555) 300-0004', 'Pharmacist', 'General Medicine', 4200.0, 'Pharm.D, Registered Pharmacist'),
            ('STF-005', 'Marcus Vance', 'lab@careplus.com', '+1 (555) 300-0005', 'Lab Technician', 'Pathology & Laboratory', 3600.0, 'B.Sc Medical Lab Technology'),
            ('STF-006', 'Robert Thorne', 'accountant@careplus.com', '+1 (555) 300-0006', 'Accountant', 'General Medicine', 4500.0, 'CPA, Senior Financial Officer'),
            ('STF-007', 'Nurse Chloe Decker', 'chloe.decker@careplus.com', '+1 (555) 300-0007', 'Nurse', 'Emergency & Trauma', 4100.0, 'Emergency Trauma Nurse'),
            ('STF-008', 'Nurse James Wilson', 'james.wilson@careplus.com', '+1 (555) 300-0008', 'Nurse', 'Pediatrics', 3700.0, 'Pediatric Registered Nurse')
        ]
        for scode, sname, semail, sphone, srole, sdept, ssal, squal in staff_data:
            stf = Staff(
                staff_code=scode,
                name=sname,
                email=semail,
                phone=sphone,
                role_title=srole,
                department_id=dept_objs[sdept].id if sdept in dept_objs else None,
                joining_date=date(2023, 1, 15),
                salary=ssal,
                qualification=squal,
                status='Active'
            )
            db.session.add(stf)
        db.session.commit()

        print("Seeding Rooms & Beds...")
        rooms_data = [
            ('101', 'General Ward', '1st Floor', 60.0, 4),
            ('102', 'General Ward', '1st Floor', 60.0, 4),
            ('201', 'Semi Private', '2nd Floor', 120.0, 2),
            ('202', 'Semi Private', '2nd Floor', 120.0, 2),
            ('301', 'Private', '3rd Floor', 250.0, 1),
            ('302', 'Private', '3rd Floor', 250.0, 1),
            ('ICU-1', 'ICU', '4th Floor (ICU)', 500.0, 2),
            ('ICU-2', 'ICU', '4th Floor (ICU)', 500.0, 2),
            ('ER-1', 'Emergency', 'Ground Floor', 150.0, 3)
        ]
        room_objs = []
        bed_objs = []
        for rnum, rtype, floor, charge, num_beds in rooms_data:
            room = Room(
                room_number=rnum,
                room_type=rtype,
                floor=floor,
                daily_charge=charge,
                total_beds=num_beds,
                status='Available'
            )
            db.session.add(room)
            db.session.flush()
            room_objs.append(room)

            for i in range(1, num_beds + 1):
                letter = chr(64 + i) if num_beds > 1 else 'Single'
                bed = Bed(
                    bed_number=f"Bed {letter}" if num_beds > 1 else "Bed 1",
                    room_id=room.id,
                    status='Available'
                )
                db.session.add(bed)
                bed_objs.append(bed)
        db.session.commit()

        print("Seeding Diagnostic Lab Tests...")
        lab_tests_data = [
            ('LAB-001', 'Complete Blood Count (CBC)', 'Hematology', 35.0, '4.5 - 11.0', 'x10^3/uL', 'Blood', 12, 'Measures RBC, WBC, Hemoglobin, Hematocrit, and Platelets.'),
            ('LAB-002', 'Fasting Blood Glucose (FBG)', 'Biochemistry', 20.0, '70 - 99', 'mg/dL', 'Blood', 6, 'Primary diagnostic for diabetes mellitus and glycemic control.'),
            ('LAB-003', 'Lipid Panel Profile', 'Biochemistry', 45.0, '< 200 Total Cholesterol', 'mg/dL', 'Blood', 12, 'Comprehensive assessment of Total Cholesterol, HDL, LDL, and Triglycerides.'),
            ('LAB-004', 'Liver Function Panel (LFT)', 'Biochemistry', 55.0, 'ALT 7-56, AST 10-40', 'U/L', 'Blood', 18, 'Evaluation of hepatic enzymes, bilirubin, albumin, and total protein.'),
            ('LAB-005', 'Renal Function Panel (KFT/BUN)', 'Biochemistry', 50.0, 'Creatinine 0.7 - 1.3', 'mg/dL', 'Blood', 12, 'Assessment of serum creatinine, BUN, and glomerular filtration rate.'),
            ('LAB-006', 'Thyroid Stimulating Hormone (TSH)', 'Immunology', 40.0, '0.4 - 4.0', 'mIU/L', 'Blood', 24, 'Screening for hypothyroidism and hyperthyroidism.'),
            ('LAB-007', 'Urine Routine & Microscopy (Urinalysis)', 'Urine Analysis', 25.0, 'Clear, pH 5.0-8.0', 'pH', 'Urine', 6, 'Diagnostic screening for UTI, proteinuria, hematuria, and renal disease.'),
            ('LAB-008', 'Chest Radiograph (X-Ray PA View)', 'Radiology', 70.0, 'Clear lung fields, normal cardiothoracic ratio', '', 'X-Ray', 4, 'Standard thoracic radiograph for respiratory evaluation.'),
            ('LAB-009', 'Cardiac Troponin I (High Sensitivity)', 'Biochemistry', 65.0, '< 0.04', 'ng/mL', 'Blood', 2, 'Cardiac biomarker for acute myocardial infarction.'),
            ('LAB-010', 'HbA1c Glycated Hemoglobin', 'Biochemistry', 38.0, '< 5.7 (Normal), > 6.5 (Diabetes)', '%', 'Blood', 12, 'Assessment of 3-month glycemic history in diabetes.')
        ]
        lab_test_objs = []
        for tcode, tname, tcat, tprice, trange, tunit, tspec, tturn, tdesc in lab_tests_data:
            test = LabTest(
                test_code=tcode,
                test_name=tname,
                category=tcat,
                price=tprice,
                normal_range=trange,
                unit=tunit,
                sample_type=tspec,
                turnaround_hours=tturn,
                description=tdesc,
                status='Active'
            )
            db.session.add(test)
            lab_test_objs.append(test)
        db.session.commit()

        print("Seeding Pharmacy Medicines & Batches...")
        meds_data = [
            ('MED-0001', 'Augmentin 625', 'Amoxicillin + Clavulanic Acid', 'Tablet', 'GlaxoSmithKline', 'AUG-2026-01', 30, 8.50, 16.00, 150, 30),
            ('MED-0002', 'Paracetamol 500mg', 'Acetaminophen', 'Tablet', 'Sanofi', 'PCM-2026-44', 90, 0.20, 1.50, 500, 50),
            ('MED-0003', 'Lipitor 20mg', 'Atorvastatin Calcium', 'Tablet', 'Pfizer', 'LIP-2026-12', 60, 4.00, 9.50, 200, 40),
            ('MED-0004', 'Glucophage 500mg', 'Metformin HCl', 'Tablet', 'Merck', 'GLU-2026-08', 45, 0.80, 3.20, 350, 50),
            ('MED-0005', 'Norvasc 5mg', 'Amlodipine Besylate', 'Tablet', 'Pfizer', 'NOR-2026-21', 60, 1.20, 4.50, 180, 30),
            ('MED-0006', 'Pantocid 40mg', 'Pantoprazole Sodium', 'Tablet', 'Sun Pharma', 'PAN-2026-05', 30, 1.50, 5.00, 240, 40),
            ('MED-0007', 'Ventolin Evohaler', 'Salbutamol Inhaler', 'Inhaler', 'GlaxoSmithKline', 'VEN-2026-33', 180, 6.00, 14.50, 80, 20),
            ('MED-0008', 'Azithral 500', 'Azithromycin', 'Tablet', 'Alembic', 'AZI-2026-09', 30, 3.20, 8.00, 110, 25),
            ('MED-0009', 'Ceftriaxone 1g IV', 'Ceftriaxone Sodium', 'Injection', 'Novartis', 'CEF-2026-03', 120, 4.50, 12.00, 90, 25),
            ('MED-0010', 'Normal Saline 0.9% 500ml', 'Sodium Chloride 0.9%', 'IV Fluid', 'Baxter', 'NS-2026-88', 365, 0.90, 3.50, 300, 60),
            ('MED-0011', 'Ibuprofen 400mg', 'Ibuprofen', 'Tablet', 'Abbott', 'IBU-2026-15', 60, 0.40, 2.00, 400, 50),
            ('MED-0012', 'Allegra 120mg', 'Fexofenadine HCl', 'Tablet', 'Sanofi', 'ALL-2026-77', 45, 2.10, 6.50, 160, 30),
            ('MED-0013', 'Insulin Glargine (Lantus)', 'Insulin Glargine', 'Injection', 'Sanofi', 'INS-2026-90', 60, 18.00, 42.00, 45, 15),
            ('MED-0014', 'Combiflam', 'Ibuprofen + Paracetamol', 'Tablet', 'Sanofi', 'COM-2026-11', 40, 0.50, 2.20, 220, 30),
            ('MED-0015', 'Betadine 10% Solution', 'Povidone Iodine', 'Drops', 'Win-Medicare', 'BET-2026-02', 180, 2.00, 5.50, 85, 20),
            ('MED-0016', 'Amoxicillin 250mg', 'Amoxicillin Trihydrate', 'Capsule', 'GSK', 'AMX-2025-01', -30, 1.00, 3.00, 10, 20), # Expired & Low Stock demo
            ('MED-0017', 'Cough Syrup Benadryl', 'Diphenhydramine HCl', 'Syrup', 'J&J', 'BEN-2026-50', 90, 1.80, 4.50, 14, 20), # Low Stock demo
            ('MED-0018', 'Omeprazole 20mg', 'Omeprazole', 'Capsule', 'AstraZeneca', 'OME-2026-19', 60, 1.10, 3.80, 190, 30),
            ('MED-0019', 'Ciprofloxacin 500mg', 'Ciprofloxacin HCl', 'Tablet', 'Bayer', 'CIP-2026-62', 45, 2.50, 7.00, 130, 25),
            ('MED-0020', 'Dextrose 5% 500ml', 'Dextrose in Water', 'IV Fluid', 'Baxter', 'D5W-2026-04', 300, 1.10, 4.00, 175, 40)
        ]
        med_objs = []
        for mcode, mname, mgen, mcat, mman, mbatch, exp_days, pprice, sprice, qty, malert in meds_data:
            exp_date = date.today() + timedelta(days=exp_days)
            med = Medicine(
                medicine_code=mcode,
                name=mname,
                generic_name=mgen,
                category=mcat,
                manufacturer=mman,
                batch_number=mbatch,
                expiry_date=exp_date,
                purchase_price=pprice,
                selling_price=sprice,
                quantity_in_stock=qty,
                minimum_stock_alert=malert,
                supplier_name='Global Med Distribution Network',
                status='Active'
            )
            db.session.add(med)
            db.session.flush()

            batch = MedicineBatch(
                medicine_id=med.id,
                batch_number=mbatch,
                expiry_date=exp_date,
                quantity=qty,
                purchase_price=pprice,
                selling_price=sprice,
                received_date=date.today() - timedelta(days=15)
            )
            db.session.add(batch)
            med_objs.append(med)
        db.session.commit()

        print("Seeding General Hospital Supplies / Inventory...")
        inventory_data = [
            ('INV-ITM-001', 'Sterile Latex Examination Gloves (M)', 'PPE', 450, 'Boxes', 50, 'Central Logistics Depot', 'Ansell Healthcare', 4.50),
            ('INV-ITM-002', 'N95 Surgical Respirator Masks', 'PPE', 280, 'Boxes', 40, 'Central Logistics Depot', '3M Medical', 12.00),
            ('INV-ITM-003', 'Disposable Syringes 5ml with Needle', 'Consumables', 800, 'Units', 100, 'ER & Ward Storage', 'BD Medical', 0.25),
            ('INV-ITM-004', 'IV Cannula 20G (Pink)', 'Consumables', 320, 'Units', 50, 'Nursing Stations Depot', 'BD Venflon', 1.10),
            ('INV-ITM-005', 'Sterile Surgical Gauze Swabs 10x10cm', 'Surgical Supplies', 600, 'Packs', 80, 'OT Prep Ward', 'Johnson & Johnson', 0.80),
            ('INV-ITM-006', 'Surgical Sutures Vicryl 3-0', 'Surgical Supplies', 150, 'Packs', 30, 'Operation Theater Storage', 'Ethicon', 6.50),
            ('INV-ITM-007', 'Hand Rub Disinfectant Solution (500ml)', 'Cleaning Supplies', 120, 'Bottles', 25, 'Ward Sanitation Deck', 'Sterillium', 3.20),
            ('INV-ITM-008', 'ECG Disposable Electrodes (Pack of 50)', 'Diagnostic Tools', 85, 'Packs', 20, 'Cardiology Diagnostic Lab', 'Philips Healthcare', 7.50),
            ('INV-ITM-009', 'Digital Clinical Thermometer', 'Medical Equipment', 40, 'Units', 10, 'General Supply Store', 'Omron Healthcare', 15.00),
            ('INV-ITM-010', 'Suction Catheter 12 Fr', 'Consumables', 8, 'Units', 20, 'ICU Equipment Room', 'Medline Industries', 1.80) # Low stock
        ]
        for icode, iname, icat, iqty, iunit, imin, iloc, isup, iprice in inventory_data:
            item = InventoryItem(
                item_code=icode,
                name=iname,
                category=icat,
                quantity=iqty,
                unit=iunit,
                minimum_stock=imin,
                location=iloc,
                supplier_name=isup,
                unit_price=iprice,
                status='Low Stock' if iqty <= imin else 'Active'
            )
            db.session.add(item)
        db.session.commit()

        print("Seeding 5 Realistic Patients...")
        patient_records = [
            ('PAT-2026-0001', 'Jonathan', 'Miller', date(1978, 4, 12), 'Male', 'O+', '+1 (555) 789-0001', 'j.miller@example.com', '124 Maple Street, Apt 3B', 'New York', 'NY', '10002', 'Sarah Miller', '+1 (555) 789-0002', 'Spouse', 'Penicillin (Severe Hives)', 'Hypertension Grade 2', 'Previous appendectomy in 2015', 'Cardiology', doc_objs[0]),
            ('PAT-2026-0002', 'Eleanor', 'Rigby', date(1985, 9, 23), 'Female', 'A+', '+1 (555) 789-0003', 'e.rigby@example.com', '56 Abbey Road', 'White Plains', 'NY', '10601', 'Thomas Rigby', '+1 (555) 789-0004', 'Brother', 'None known', 'Type 2 Diabetes Mellitus', 'None reported', 'General Medicine', doc_objs[4]),
            ('PAT-2026-0003', 'Alexander', 'Pierce', date(1964, 11, 5), 'Male', 'B+', '+1 (555) 789-0005', 'a.pierce@example.com', '88 Sunset Boulevard', 'Yonkers', 'NY', '10701', 'Maria Pierce', '+1 (555) 789-0006', 'Spouse', 'Sulfa Drugs', 'Coronary Artery Disease, Hyperlipidemia', 'Stent placement 2021', 'Cardiology', doc_objs[0]),
            ('PAT-2026-0004', 'Sophia', 'Vargas', date(1996, 2, 18), 'Female', 'AB+', '+1 (555) 789-0007', 'sophia.v@example.com', '312 Oak Ridge Lane', 'Brooklyn', 'NY', '11201', 'Carlos Vargas', '+1 (555) 789-0008', 'Father', 'Aspirin', 'Mild Asthma', 'Tonsillectomy in childhood', 'Pediatrics', doc_objs[3]),
            ('PAT-2026-0005', 'David', 'Kowalski', date(1952, 7, 30), 'Male', 'O-', '+1 (555) 789-0009', 'd.kowalski@example.com', '405 Pine Street', 'Queens', 'NY', '11354', 'Anna Kowalski', '+1 (555) 789-0010', 'Daughter', 'Latex, Iodine contrast', 'Osteoarthritis, Chronic Kidney Disease Stage 2', 'Total Right Knee Arthroplasty 2019', 'Orthopedics', doc_objs[2])
        ]
        patient_objs = []
        for pid, fn, ln, dob_val, gen, bg, ph, em, addr, city, state, zip_c, ec_n, ec_p, ec_r, alg, cond, hist, dname, pdoc in patient_records:
            pat = Patient(
                patient_id=pid,
                first_name=fn,
                last_name=ln,
                dob=dob_val,
                gender=gen,
                blood_group=bg,
                phone=ph,
                email=em,
                address=addr,
                city=city,
                state=state,
                zip_code=zip_c,
                emergency_contact_name=ec_n,
                emergency_contact_phone=ec_p,
                emergency_contact_relation=ec_r,
                allergies=alg,
                existing_conditions=cond,
                medical_history=hist,
                department_id=dept_objs[dname].id if dname in dept_objs else None,
                primary_doctor_id=pdoc.id if pdoc else None,
                status='Active',
                registration_date=datetime.utcnow() - timedelta(days=random.randint(5, 120))
            )
            db.session.add(pat)
            patient_objs.append(pat)
        db.session.commit()

        print("Seeding Clinical Appointments...")
        times = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '14:00', '14:30', '15:00', '15:30', '16:00']
        reasons = [
            'Follow-up visit for hypertension blood pressure review.',
            'Severe migraine persisting for 3 days with photophobia.',
            'Knee stiffness and joint swelling after morning exercise.',
            'Routine health checkup and diabetic glycemic evaluation.',
            'Chest palpitations on exertion and shortness of breath.',
            'Follow-up on skin rash and eczema response to topical cream.',
            'Prenatal ultrasound review and routine obstetric consultation.',
            'Acute back pain radiating down left thigh.'
        ]
        apt_objs = []
        for i in range(10):
            apt_code = f"APT-2026-{i+1:04d}"
            pat = patient_objs[i % len(patient_objs)]
            doc = doc_objs[i % len(doc_objs)]
            apt_day = date.today() if i < 4 else (date.today() + timedelta(days=random.randint(1, 10)) if i < 7 else date.today() - timedelta(days=random.randint(1, 15)))
            status = 'Scheduled' if apt_day >= date.today() else 'Completed'
            if i == 8:
                status = 'Confirmed'
            elif i == 9:
                status = 'Cancelled'

            apt = Appointment(
                appointment_id=apt_code,
                patient_id=pat.id,
                doctor_id=doc.id,
                department_id=doc.department_id,
                appointment_date=apt_day,
                appointment_time=times[i % len(times)],
                appointment_type='General Consultation' if i % 2 == 0 else 'Follow-up',
                reason=reasons[i % len(reasons)],
                status=status
            )
            db.session.add(apt)
            apt_objs.append(apt)
        db.session.commit()

        print("Seeding Inpatient Admissions & Bed Occupancy...")
        # 1. Active Inpatient: Jonathan Miller in Room 101, Bed A
        adm1 = Admission(
            admission_id='ADM-2026-0001',
            patient_id=patient_objs[0].id,
            doctor_id=doc_objs[0].id,
            department_id=doc_objs[0].department_id,
            room_id=room_objs[0].id,
            bed_id=bed_objs[0].id,
            admission_date=datetime.utcnow() - timedelta(days=3),
            reason_for_admission='Unstable angina with severe retrosternal chest pain.',
            initial_diagnosis='Acute Coronary Syndrome (Non-ST Elevation Myocardial Infarction)',
            status='Admitted'
        )
        db.session.add(adm1)
        db.session.flush()
        bed_objs[0].status = 'Occupied'
        bed_objs[0].current_admission_id = adm1.id
        patient_objs[0].status = 'Admitted'

        # 2. Active Inpatient: Alexander Pierce in Room ICU-1, Bed A
        icu_room = [r for r in room_objs if r.room_number == 'ICU-1'][0]
        icu_bed = [b for b in bed_objs if b.room_id == icu_room.id][0]
        adm2 = Admission(
            admission_id='ADM-2026-0002',
            patient_id=patient_objs[2].id,
            doctor_id=doc_objs[4].id,
            department_id=doc_objs[4].department_id,
            room_id=icu_room.id,
            bed_id=icu_bed.id,
            admission_date=datetime.utcnow() - timedelta(days=1),
            reason_for_admission='Acute decompensated heart failure with pulmonary edema.',
            initial_diagnosis='Severe Congestive Heart Failure, NYHA Class IV',
            status='Admitted'
        )
        db.session.add(adm2)
        db.session.flush()
        icu_bed.status = 'Occupied'
        icu_bed.current_admission_id = adm2.id
        patient_objs[2].status = 'Admitted'

        # 3. Discharged Inpatient: David Kowalski
        adm3 = Admission(
            admission_id='ADM-2026-0003',
            patient_id=patient_objs[4].id,
            doctor_id=doc_objs[2].id,
            department_id=doc_objs[2].department_id,
            room_id=room_objs[2].id,
            bed_id=room_objs[2].beds[0].id,
            admission_date=datetime.utcnow() - timedelta(days=10),
            discharge_date=datetime.utcnow() - timedelta(days=4),
            reason_for_admission='Severe acute right knee osteoarthritis requiring total joint replacement.',
            initial_diagnosis='Severe Tricompartmental Osteoarthritis Right Knee',
            status='Discharged'
        )
        db.session.add(adm3)
        db.session.flush()

        summary3 = DischargeSummary(
            admission_id=adm3.id,
            discharge_date=datetime.utcnow() - timedelta(days=4),
            condition_at_discharge='Improved',
            final_diagnosis='Post Total Right Knee Arthroplasty, Stable recovery',
            treatment_summary='Underwent uncomplicated total knee replacement under spinal anesthesia. Mobilized on Day 2 with physical therapy. Wound clean, dry, and intact.',
            discharge_medications='Tab Paracetamol 500mg 1-1-1 as needed for pain, Tab Pantoprazole 40mg 1-0-0 before breakfast x 10 days, Tab Enoxaparin 40mg SC daily x 14 days.',
            advice_instructions='Continue daily quadriceps isometric exercises and assisted ambulation with walker. Avoid squatting and high-impact loading. Keep surgical wound dry.',
            follow_up_date=date.today() + timedelta(days=10),
            doctor_signature='Dr. Harrison Wells (MS Ortho)'
        )
        db.session.add(summary3)
        db.session.commit()

        print("Seeding Medical Records & Vitals...")
        for i in range(5):
            pat = patient_objs[i]
            doc = doc_objs[i % len(doc_objs)]
            rec = MedicalRecord(
                record_id=f"MED-2026-{i+1:04d}",
                patient_id=pat.id,
                doctor_id=doc.id,
                visit_date=datetime.utcnow() - timedelta(days=random.randint(2, 30)),
                symptoms=f"Patient presents with {pat.existing_conditions or 'fatigue, fever, and mild headache'}.",
                diagnosis=f"Clinical assessment: {pat.existing_conditions or 'Acute Upper Respiratory Tract Infection'}",
                clinical_notes="General physical examination revealed stable parameters. Chest clear, heart sounds normal.",
                treatment_plan="Advised conservative medical therapy, hydration, symptomatic medications, and review if symptoms worsen.",
                follow_up_date=date.today() + timedelta(days=14)
            )
            db.session.add(rec)
            db.session.flush()

            # Add vitals
            vitals = Vitals(
                patient_id=pat.id,
                medical_record_id=rec.id,
                recorded_by='Nurse Sarah Jenkins',
                recorded_at=rec.visit_date,
                temperature=round(random.uniform(97.8, 99.4), 1),
                bp_systolic=random.randint(115, 145),
                bp_diastolic=random.randint(70, 92),
                heart_rate=random.randint(64, 88),
                respiratory_rate=random.randint(14, 20),
                spo2=round(random.uniform(96.0, 99.5), 1),
                weight_kg=round(random.uniform(55.0, 90.0), 1),
                height_cm=round(random.uniform(155.0, 185.0), 1),
                notes='Patient conscious, alert, and oriented.'
            )
            vitals.calculate_bmi()
            db.session.add(vitals)
        db.session.commit()

        print("Seeding Prescriptions...")
        for i in range(5):
            pat = patient_objs[i]
            doc = doc_objs[i % len(doc_objs)]
            rx = Prescription(
                prescription_id=f"RX-2026-{i+1:04d}",
                patient_id=pat.id,
                doctor_id=doc.id,
                prescription_date=date.today() - timedelta(days=random.randint(1, 10)),
                diagnosis=pat.existing_conditions or 'Bacterial Infection / Hypertension',
                general_advice='Take medications regularly after meals. Maintain adequate fluid intake. Avoid missed doses.',
                status='Dispensed' if i < 3 else 'Active'
            )
            db.session.add(rx)
            db.session.flush()

            item1 = PrescriptionItem(
                prescription_id=rx.id,
                medicine_id=med_objs[i % len(med_objs)].id,
                medicine_name=med_objs[i % len(med_objs)].name,
                dosage='500 mg' if 'Tablet' in med_objs[i % len(med_objs)].category else '1 puff',
                frequency='Twice daily (1-0-1)',
                duration='5 days',
                instructions='After meals with a glass of water'
            )
            item2 = PrescriptionItem(
                prescription_id=rx.id,
                medicine_id=med_objs[(i+1) % len(med_objs)].id,
                medicine_name=med_objs[(i+1) % len(med_objs)].name,
                dosage='40 mg',
                frequency='Once daily in the morning',
                duration='10 days',
                instructions='Before breakfast'
            )
            db.session.add_all([item1, item2])
        db.session.commit()

        print("Seeding Laboratory Investigation Orders & Results...")
        for i in range(5):
            pat = patient_objs[i]
            doc = doc_objs[i % len(doc_objs)]
            test = lab_test_objs[i % len(lab_test_objs)]
            order_st = 'Completed' if i < 3 else ('Processing' if i < 4 else 'Requested')

            order = LabOrder(
                order_id=f"LBO-2026-{i+1:04d}",
                patient_id=pat.id,
                doctor_id=doc.id,
                lab_test_id=test.id,
                order_date=datetime.utcnow() - timedelta(days=random.randint(1, 7)),
                priority='Emergency' if i == 0 else ('Urgent' if i == 1 else 'Normal'),
                clinical_notes='Diagnostic evaluation for clinical symptoms.',
                status=order_st
            )
            db.session.add(order)
            db.session.flush()

            if order_st == 'Completed':
                res = LabResult(
                    lab_order_id=order.id,
                    result_value='13.8' if 'CBC' in test.test_name else ('94' if 'Glucose' in test.test_name else 'Normal findings noted'),
                    reference_range=test.normal_range,
                    unit=test.unit,
                    status_flag='Normal' if i != 2 else 'High',
                    technician_name='Marcus Vance (MLT)',
                    verified_by='Dr. Bruce Banner (MD Pathologist)',
                    remarks='Results cross-verified against internal calibrators.',
                    completed_at=datetime.utcnow() - timedelta(days=1)
                )
                db.session.add(res)
        db.session.commit()

        print("Seeding Billing Invoices & Payments...")
        for i in range(5):
            pat = patient_objs[i]
            inv_code = f"INV-2026-{i+1:04d}"
            inv_date = date.today() - timedelta(days=random.randint(2, 60))
            btype = 'Inpatient' if i < 2 else ('Outpatient' if i < 4 else 'Pharmacy')

            inv = Invoice(
                invoice_number=inv_code,
                patient_id=pat.id,
                invoice_date=inv_date,
                due_date=inv_date + timedelta(days=15),
                billing_type=btype,
                discount_type='Fixed',
                discount_value=10.0 if i % 2 == 0 else 0.0,
                tax_rate=5.0,
                created_by='Robert Thorne (Accounts)'
            )
            db.session.add(inv)
            db.session.flush()

            item1 = InvoiceItem(
                invoice_id=inv.id,
                item_type='Consultation',
                item_name='Specialist Medical Consultation',
                quantity=1,
                unit_price=100.0,
                total_price=100.0
            )
            item2 = InvoiceItem(
                invoice_id=inv.id,
                item_type='Lab Test' if i % 2 == 0 else 'Medicine',
                item_name='Complete Blood Count (CBC)' if i % 2 == 0 else 'Prescribed Pharmaceuticals',
                quantity=1,
                unit_price=35.0,
                total_price=35.0
            )
            db.session.add_all([item1, item2])
            inv.recalculate()

            # Record payments for invoices
            if i < 3:
                # Fully Paid
                pay = Payment(
                    payment_code=f"PAY-2026-{i+1:04d}",
                    invoice_id=inv.id,
                    patient_id=pat.id,
                    payment_date=datetime.combine(inv_date, datetime.min.time()) + timedelta(hours=2),
                    amount=inv.grand_total,
                    payment_method='Card' if i % 2 == 0 else 'Cash',
                    transaction_reference=f"TXN-998{i:03d}",
                    received_by='Robert Thorne (Accountant)',
                    receipt_notes='Paid in full at counter.'
                )
                db.session.add(pay)
                inv.recalculate()
            elif i < 5:
                # Partially Paid
                partial = round(inv.grand_total / 2.0, 2)
                pay = Payment(
                    payment_code=f"PAY-2026-{i+1:04d}",
                    invoice_id=inv.id,
                    patient_id=pat.id,
                    payment_date=datetime.combine(inv_date, datetime.min.time()) + timedelta(hours=1),
                    amount=partial,
                    payment_method='UPI',
                    transaction_reference=f"UPI-2026-{i:04d}",
                    received_by='Robert Thorne (Accountant)',
                    receipt_notes='Initial advance settlement.'
                )
                db.session.add(pay)
                inv.recalculate()

        db.session.commit()

        print("Seeding Audit Trail Logs & Notifications...")
        audit_samples = [
            ('LOGIN', 'Authentication', 'User admin (Super Admin) authenticated from local portal.', '127.0.0.1'),
            ('CREATE_PATIENT', 'Patient', 'Registered new patient Jonathan Miller (PAT-2026-0001).', '127.0.0.1'),
            ('ADMIT_PATIENT', 'Inpatient', 'Admitted patient Jonathan Miller to Room 101, Bed A.', '127.0.0.1'),
            ('CREATE_PRESCRIPTION', 'Prescription', 'Issued prescription RX-2026-0001 for Jonathan Miller.', '127.0.0.1'),
            ('ORDER_LAB_TEST', 'Laboratory', 'Ordered Complete Blood Count for Alexander Pierce.', '127.0.0.1'),
            ('RECORD_PAYMENT', 'Billing', 'Recorded Card settlement of ₹135.00 for Invoice INV-2026-0001.', '127.0.0.1'),
            ('DISPENSE_PRESCRIPTION', 'Pharmacy', 'Dispensed prescription RX-2026-0001 at pharmacy desk.', '127.0.0.1'),
            ('UPDATE_SETTINGS', 'System Settings', 'Updated official hospital tax percentage and currency configuration.', '127.0.0.1')
        ]
        for act, mod, desc, ip in audit_samples:
            log = AuditLog(
                user_id=user_objs['admin'].id,
                action=act,
                module=mod,
                description=desc,
                ip_address=ip,
                created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
            )
            db.session.add(log)

        notifs = [
            ('Low Stock Warning: Cough Syrup', 'Stock for Benadryl Cough Syrup dropped below threshold (14 units remaining).', 'Pharmacist', 'warning', '/pharmacy/?filter=low'),
            ('Patient Admitted: Jonathan Miller', 'Patient admitted to Room 101, Bed A under Dr. Arthur Conan.', 'Nurse', 'info', '/admissions/'),
            ('CRITICAL LAB ALERT: Alexander Pierce', 'Critical diagnostic finding on Cardiac Troponin I for Order LBO-2026-0001.', 'Doctor', 'danger', '/laboratory/'),
            ('Payment Settled: Invoice INV-2026-0001', 'Full payment of ₹135.00 received via POS Card settlement.', 'Accountant', 'success', '/billing/1')
        ]
        for ntitle, nmsg, nrole, ntype, nlink in notifs:
            notif = Notification(
                target_role=nrole,
                title=ntitle,
                message=nmsg,
                notification_type=ntype,
                link=nlink,
                is_read=False,
                created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 24))
            )
            db.session.add(notif)

        db.session.commit()
        print("[SUCCESS] CarePlus Database Seeding completed successfully with rich realistic data!")

if __name__ == '__main__':
    seed_database()
