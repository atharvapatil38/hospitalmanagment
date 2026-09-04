# 🏥 CarePlus Hospital Management System (HMS)

> **A Production-Grade, Full-Stack Hospital Information & Clinical Operations Management System**

[![Flask](https://img.shields.io/badge/Flask-3.0+-blue.svg)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)](https://www.sqlalchemy.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![Pytest](https://img.shields.io/badge/Pytest-100%25%20Passed-brightgreen.svg)](https://pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🌟 Overview & Architecture

**CarePlus HMS** is an enterprise-grade hospital management and clinical informatics application designed for modern multi-speciality medical centers. Built with a modular Flask application factory architecture, strict Role-Based Access Control (RBAC), ACID-compliant relational data modeling, dynamic UI interactions, and automated audit trails, CarePlus handles everything from patient intake to discharge summaries, pharmacy inventory control, diagnostic laboratory reporting, and multi-tier billing.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CarePlus Web Application Layer                     │
│    (Jinja2 Templates + Bootstrap 5.3 UI + Chart.js + Dynamic Modals & Forms) │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP / WSGI
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                            Flask Blueprint Routes                           │
│  ├── Auth & Profile         ├── Admissions & Wards     ├── Diagnostic Lab   │
│  ├── Executive Dashboard    ├── Rooms & Bed Matrix     ├── Billing Invoices │
│  ├── Patients Directory     ├── Medical Records        ├── Supplies / Assets│
│  ├── Doctors & Consultants  ├── Vitals Recording       ├── Analytics Reports│
│  ├── Clinical Appointments  ├── Multi-Item Rx Builder  ├── System Audit Log │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Session / Auth & Decorators
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                   Business Logic & Service Utility Layer                    │
│  ├── RBAC @roles_required   ├── Auto ID Generator      ├── CSV Exporters    │
│  ├── Audit Trail Logger     ├── Notification Dispatcher ├── Jinja Filters    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ SQLAlchemy ORM
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                             Database Layer                                  │
│   (17 Relational Tables: SQLite for dev / PostgreSQL for production deploy) │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 👥 Role-Based Access Control (RBAC) Matrix

CarePlus HMS provides **8 distinct user roles** with granular permissions and specialized dashboards:

| Role | Access Scope & Key Capabilities |
| :--- | :--- |
| **👑 Super Admin** | Full root administrative access across all clinical, financial, audit, staff, and system configuration modules. |
| **🏥 Hospital Admin** | Hospital operations management, doctor & staff onboarding, room/bed matrix configuration, department oversight, and executive reports. |
| **👨‍⚕️ Doctor** | Personal consultation agenda, assigned inpatients, clinical diagnosis recording, vitals review, prescription generator, lab orders, and discharge summaries. |
| **👩‍⚕️ Nurse** | Inpatient care, bedside vitals recording, patient admissions/transfers, appointment check-ins, and ward tracking. |
| **📋 Receptionist** | Patient intake/registration, master directory search, doctor appointment scheduling with real-time conflict checking, and outpatient triage. |
| **💊 Pharmacist** | Pharmaceutical catalog, batch & expiry management, restock adjustments, prescription dispensing, and low-stock alerts. |
| **🔬 Lab Technician**| Diagnostic catalog, investigation order queue, specimen collection tracking, test result entry with reference ranges, and critical finding alerts. |
| **💳 Accountant** | Patient invoices (outpatient & inpatient), dynamic line-item builder, partial/full payment settlement, tax/discount calculation, and thermal receipt printing. |

---

## 🔑 Demo Login Accounts

All accounts come pre-seeded with realistic healthcare data:

| Role | Email Address | Password |
| :--- | :--- | :--- |
| **Super Admin** | `admin@careplus.com` | `Admin@123` |
| **Hospital Admin**| `hospital.admin@careplus.com` | `Admin@123` |
| **Doctor** | `doctor@careplus.com` | `Doctor@123` |
| **Doctor (Cardiology)** | `marcus.vance@careplus.com` | `Doctor@123` |
| **Nurse** | `nurse@careplus.com` | `Nurse@123` |
| **Receptionist** | `reception@careplus.com` | `Reception@123` |
| **Pharmacist** | `pharmacy@careplus.com` | `Pharmacy@123` |
| **Lab Technician**| `lab@careplus.com` | `Lab@123` |
| **Accountant** | `accountant@careplus.com` | `Account@123` |

---

## 🚀 Key Functional Modules

### 1. 📊 Executive & Role-Aware Dashboard
* **Dynamic KPIs**: Total patients, today's appointments, inpatient bed occupancy percentage, today's collections, pending lab tests, and low-stock alerts.
* **Interactive Visualizations**: 7-day revenue trendline charts and department patient distribution pie charts powered by Chart.js.
* **Quick Action Hub**: 1-click booking, new patient intake, invoice generation, and prescription builder.
* **Doctor Personalized View**: Automatically shows attending doctor's morning visits, assigned ward inpatients, and today's schedule.

### 2. 🗂️ Patient Management & 360° Electronic Health Record (EHR)
* **Demographic & Clinical Intake**: Unique formatted identifiers (`PAT-2026-XXXX`), blood groups, emergency contacts, medical history, allergies, and chronic conditions.
* **Patient 360° Profile**: Tabbed clinical dossier consolidating Appointments, Consultation Records, Bedside Vitals charts, Prescriptions, Diagnostic Lab Orders, Inpatient Admissions, and Billing History.
* **Filter & Export**: Real-time multi-field search, status filtering, and one-click CSV export.

### 3. 📅 Appointment Scheduling & Conflict Prevention
* **Automated Conflict Detection**: Prevents double-booking doctors at the exact same date and time slot.
* **Status Lifecycle**: Transition visits seamlessly from `Scheduled` ➔ `Confirmed` ➔ `Completed` ➔ `Cancelled` ➔ `No-Show`.
* **Doctor Consultation Fee Integration**: Automatic fee calculation linked to billing.

### 4. 🛏️ Inpatient Admissions & Interactive Bed Matrix
* **Visual Room & Bed Matrix**: Real-time room-by-room grid showing status badges (`Available`, `Occupied`, `Reserved`, `Maintenance`).
* **Admission Intake**: Ward assignment, attending physician allocation, bed locking, and initial diagnosis.
* **In-Hospital Bed Transfers**: Department-to-department and room-to-room transfers with audit tracking.
* **Clinical Discharge Summary**: Automated length of stay (LOS) computation, condition at discharge, discharge medications, follow-up advice, and printable summary sheet.

### 5. 🩺 Clinical Consultation & Bedside Vitals
* **Consultation Encounters**: Subjective complaints, physical examination findings, differential diagnosis, treatment plan, and ICD codes.
* **Vitals Tracking**: Blood pressure (Systolic/Diastolic), heart rate (BPM), temperature (°F), respiratory rate, SpO2 (%), blood glucose (mg/dL), weight (kg), and BMI calculation.

### 6. 💊 Electronic Prescriptions & Pharmacy Dispensing
* **Dynamic Multi-Item Rx Builder**: Prescribe multiple medications with individualized dosages, frequencies (e.g. `Twice daily`, `TID`), durations, and food instructions.
* **Printable Rx Slip**: Formatted hospital prescription document with doctor signature block, hospital seal, and disclaimer.
* **Inventory Control**: Batch tracking, manufacture/expiry dates, low-stock threshold alerts, and Stock In / Stock Out adjustment logging.

### 7. 🔬 Diagnostic Laboratory Management
* **Investigation Catalog**: Test panels, standard specimen requirements (Blood, Urine, Sputum, etc.), turnaround times, and prices.
* **Diagnostic Order Workflow**: `Requested` ➔ `Sample Collected` ➔ `Processing` ➔ `Completed`.
* **Findings & Result Reporting**: Reference ranges, units, technician details, pathologist verification, and automatic **Critical Result Alerts** sent to attending doctors.
* **Printable Lab Report**: Clean laboratory report ready for patient delivery.

### 8. 💳 Multi-Tier Invoicing & Financial Settlement
* **Dynamic Invoice Builder**: Multi-row bill generator supporting Consultations, Inpatient Room charges, Lab Tests, Pharmacy, Nursing, and Surgical fees.
* **Automated Financial Calculations**: Live calculation of Subtotal, Percentage/Fixed Discounts, Hospital Tax / VAT rates, Grand Total, and Balance Due.
* **Payments & Receipts**: Multi-mode payment recording (Cash, Credit/Debit Card, Insurance, UPI, Bank Transfer) with partial settlement tracking and printable thermal receipt slips.

### 9. 📈 Operational Reports & Security Audit Trail
* **Filterable Reports**: Date-range operational report generation for Revenue, Patients, Appointments, Admissions, Pharmacy Sales, and Laboratory Orders.
* **System Audit Trail**: Complete immutable logging of logins, patient updates, stock modifications, clinical changes, and invoice generation with IP address and timestamps.

---

## 🛠️ Technology Stack

* **Backend Framework**: Python 3.12, Flask 3.0+
* **Database & ORM**: SQLAlchemy 2.0+, Flask-SQLAlchemy, SQLite (Dev) / PostgreSQL (Prod ready)
* **Authentication & Security**: Flask-Login, Werkzeug Security (scrypt password hashing), CSRF protection via Flask-WTF
* **Frontend Architecture**: HTML5, Jinja2 template inheritance, Bootstrap 5.3, Bootstrap Icons, Chart.js 4.4
* **Testing Suite**: Pytest 9+, Flask-Testing Client

---

## ⚡ Quick Start & Installation

### 1. Clone the Repository & Setup Virtual Environment
```bash
git clone https://github.com/your-username/careplus-hms.git
cd careplus-hms

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize & Seed Database
```bash
python seed.py
```
*(This automatically creates all database tables, creates default roles, registers system settings, and populates realistic demo records across all modules.)*

### 4. Run the Development Server
```bash
python run.py
```
Open your browser and navigate to **`http://127.0.0.1:5000`**!

---

## 🧪 Automated Testing

CarePlus HMS includes a comprehensive test suite covering all critical workflows:

```bash
# Run full test suite with verbose output
pytest -v
```

### Test Coverage Highlights
* `tests/test_auth.py`: Authentication, session persistence, role restrictions, password security.
* `tests/test_patients.py`: Patient registration, duplicate validation, search filters, 360 profile.
* `tests/test_appointments.py`: Appointment booking, doctor schedule conflict checks, status transitions.
* `tests/test_admissions.py`: Inpatient intake, bed status synchronization (`Available` ➔ `Occupied`), discharge summary generation, and bed release.
* `tests/test_prescriptions.py`: Multi-item medication builder and printable prescription slips.
* `tests/test_pharmacy.py`: Medicine catalog, batch tracking, inventory restock, and stock-out adjustments.
* `tests/test_laboratory.py`: Lab test catalog, investigation orders, specimen processing, and diagnostic result verification.
* `tests/test_billing.py`: Dynamic invoice calculations (subtotal, discounts, tax), partial payment records, and account settlements.

---

## 📂 Project Directory Structure

```
hospital managment/
├── app/
│   ├── __init__.py                # Application Factory & Filter Registrations
│   ├── extensions.py              # db, login_manager, csrf instances
│   ├── forms/                     # Flask-WTF Forms with field validators
│   │   ├── admin_forms.py
│   │   ├── auth_forms.py
│   │   ├── billing_forms.py
│   │   ├── clinical_forms.py
│   │   └── pharmacy_forms.py
│   ├── models/                    # 17 SQLAlchemy Relational Data Models
│   │   ├── user.py, patient.py, doctor.py, department.py
│   │   ├── appointment.py, admission.py, medical_record.py
│   │   ├── prescription.py, pharmacy.py, laboratory.py
│   │   ├── billing.py, inventory.py, audit.py
│   ├── routes/                    # 16 Modular Route Blueprints
│   │   ├── auth.py, dashboard.py, patients.py, doctors.py
│   │   ├── appointments.py, admissions.py, rooms_beds.py
│   │   ├── medical_records.py, prescriptions.py, pharmacy.py
│   │   ├── laboratory.py, billing.py, inventory.py
│   │   ├── staff.py, reports.py, settings.py
│   ├── static/                    # CSS, JavaScript & Assets
│   │   ├── css/style.css          # Healthcare UI Theme
│   │   └── js/main.js, dashboard-charts.js
│   ├── templates/                 # 31 Jinja2 HTML Templates
│   │   ├── base.html, auth/, dashboard/, patients/, doctors/
│   │   ├── appointments/, admissions/, rooms_beds/, medical_records/
│   │   ├── prescriptions/, pharmacy/, laboratory/, billing/
│   │   ├── inventory/, staff/, reports/, settings/
│   │   └── errors/                # 400, 403, 404, 500 error pages
│   └── utils/                     # Helpers, Decorators, ID Generator, Audit
├── api/
│   └── index.py                   # Vercel Serverless WSGI Entrypoint
├── instance/                      # Local SQLite database storage
├── tests/                         # Pytest test suite (19 test cases)
├── config.py                      # Development & Production Configuration
├── seed.py                        # Realistic Mock Data Seeder
├── run.py                         # Application CLI Runner
├── vercel.json                    # Vercel Serverless & Static Asset Routing
├── .vercelignore                  # Vercel Build Optimization Excludes
├── requirements.txt               # Python Dependencies
├── VERCEL_DEPLOYMENT.md           # Step-by-Step Vercel Deployment Guide
└── README.md                      # Project Portfolio Documentation
```

---

## 🚀 Deploying to Vercel

CarePlus HMS is pre-configured and ready for 1-click deployment on **Vercel**:

1. Push your repository to GitHub.
2. Import the repository in [Vercel](https://vercel.com/new).
3. *(Optional)* Add your cloud PostgreSQL connection string in the `DATABASE_URL` environment variable (e.g. from **Neon**, **Supabase**, or **Vercel Postgres**).
4. Click **Deploy**!

For detailed step-by-step instructions, see [`VERCEL_DEPLOYMENT.md`](file:///e:/hospital%20managment/VERCEL_DEPLOYMENT.md).


---

## 🛡️ Security Features
* **Password Security**: Werkzeug `generate_password_hash` with secure salting.
* **Session Management**: Secure cookie-based sessions with role re-validation.
* **SQL Injection Protection**: Fully parameterized queries via SQLAlchemy ORM.
* **CSRF Protection**: Universal CSRF tokens on all POST/PUT/DELETE forms.
* **Access Control**: Route-level `@roles_required` decorators preventing privilege escalation.
* **Audit Trail**: Every critical action (create, edit, delete, dispense, discharge) is immutably logged with actor, timestamp, and IP address.

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
