# 🏥 CarePlus Hospital Management System (HMS)
## Comprehensive Major Project Summary & Technical Report

---

## 1. Executive Summary

**CarePlus Hospital Management System (HMS)** is an enterprise-grade, full-stack web application designed for comprehensive hospital administration, clinical workflow automation, inpatient and outpatient care tracking, diagnostic laboratory management, pharmacy inventory control, and financial operations.

Built using **Python Flask**, **SQLAlchemy ORM**, **Bootstrap 5.3**, and modern JavaScript, the platform adheres to modern software engineering principles including **Role-Based Access Control (RBAC)** across 8 specialized hospital roles, immutable system auditing, real-time schedule conflict prevention, automated vital metric analytics (BMI, pulse pressure), dynamic multi-item invoice billing in **Indian Rupees (₹)**, and seamless **Vercel Serverless** cloud deployment.

---

## 2. Project Metadata

| Attribute | Details |
| :--- | :--- |
| **Project Name** | CarePlus Multispeciality Hospital Management System |
| **Version** | 1.0.0 (Production-Ready) |
| **Primary Architecture** | Modular WSGI MVC Architecture (16 Blueprints, 17 Relational Models) |
| **Frontend Technologies** | HTML5, CSS3, Bootstrap 5.3.3, Bootstrap Icons, Chart.js |
| **Backend Framework** | Python 3.12+, Flask 3.0+, Jinja2 Template Engine |
| **Database System** | SQLite (Local/Serverless Fallback) / PostgreSQL (Neon, Supabase) via SQLAlchemy |
| **Security & Auth** | Flask-Login, Werkzeug Password Hashing (PBKDF2-HMAC-SHA256), Flask-WTF CSRF |
| **System Currency** | Indian Rupee (₹ / INR) |
| **Deployment Platform** | Vercel Serverless Functions (`@vercel/python`) & Edge CDN |
| **GitHub Repository** | [github.com/atharvapatil38/hospitalmanagment](https://github.com/atharvapatil38/hospitalmanagment) |
| **Test Coverage** | 19 Pytest Automated Integration & Unit Tests (100% Pass Rate) |

---

## 3. High-Level System Architecture

```
                                  ┌───────────────────────────────┐
                                  │      Client Web Browser       │
                                  │   (Desktop / Tablet / Mobile) │
                                  └───────────────┬───────────────┘
                                                  │ HTTPS / Edge CDN
                                  ┌───────────────▼───────────────┐
                                  │       Vercel Serverless       │
                                  │       WSGI Entrypoint         │
                                  │        (api/index.py)         │
                                  └───────────────┬───────────────┘
                                                  │
                ┌─────────────────────────────────┼─────────────────────────────────┐
                │                                 │                                 │
  ┌─────────────▼─────────────┐     ┌─────────────▼─────────────┐     ┌─────────────▼─────────────┐
  │     Security & Auth       │     │     Core Clinical Core    │     │   Financials & Logistics  │
  │ • Flask-Login RBAC (8)    │     │ • Patients & EHR Profiles │     │ • Multi-Item Billing (₹)  │
  │ • CSRF Protection         │     │ • Doctor Schedules & Ops  │     │ • Pharmacy & Batch Expiry │
  │ • Password Salting        │     │ • Admissions & Bed Matrix │     │ • Lab Diagnostic Orders   │
  │ • Immutable Audit Logs    │     │ • E-Prescriptions & Vitals│     │ • Asset & Supply Depot    │
  └─────────────┬─────────────┘     └─────────────┬─────────────┘     └─────────────┬─────────────┘
                │                                 │                                 │
                └─────────────────────────────────┼─────────────────────────────────┘
                                                  │ SQLAlchemy ORM
                                  ┌───────────────▼───────────────┐
                                  │  Database Storage Subsystem   │
                                  │ • Neon / Supabase (PostgreSQL)│
                                  │ • Serverless SQLite (/tmp)    │
                                  └───────────────────────────────┘
```

---

## 4. Key Functional Modules & Features

### 👤 1. Patient Lifecycle & Electronic Health Records (EHR)
* **Formatted Patient Identifiers**: Auto-generated sequential IDs (`PAT-YYYY-XXXX`).
* **Demographic & Clinical Profiles**: Contact information, blood group, emergency contact, known drug/environmental allergies, and chronic medical history.
* **Unified Patient 360° Timeline**: Consolidated view of all past appointments, inpatient hospitalizations, clinical vitals, prescription orders, lab investigations, and billing history.
* **Smart Search**: Real-time filtering by Patient ID, Name, Phone Number, or Blood Group.

### 👨‍⚕️ 2. Doctor Management & OPD Schedule Management
* **Department Assignment**: Cardiology, Neurology, Orthopedics, Pediatrics, General Medicine, Dermatology, Radiology, and ENT.
* **Availability Schedules**: Shift start/end times, active consultation days, and assigned consultation rooms.
* **Consultation Fees**: Standard consultation fee tracking in Indian Rupees (₹).

### 📅 3. Real-Time Appointment Scheduling & Conflict Prevention
* **Automated Collision Detection**: Prevents double-booking doctors on overlapping timeslots.
* **Lifecycle State Machine**: Transitions through `Scheduled` $\rightarrow$ `Completed` $\rightarrow$ `Cancelled` $\rightarrow$ `No Show`.
* **Patient & Doctor Integration**: Direct linkage to patient profile and doctor's daily agenda.

### 🛏️ 4. Inpatient Admissions & Interactive Bed Matrix
* **Visual Room Matrix**: Real-time tracking of beds across Private Wards, Semi-Private Rooms, Intensive Care Units (ICU), Emergency Wards, and General Wards.
* **Automated Occupancy Toggling**: Beds automatically transition to `Occupied` on admission and `Available` upon patient discharge.
* **Discharge Summary Generator**: Tracks admission duration, Length of Stay (LOS), discharge condition, treatment summary, post-discharge instructions, and printable discharge certificates.

### 🩺 5. Clinical Encounters, Vitals & Electronic Prescriptions
* **Vital Signs Tracking**: Blood pressure (Systolic/Diastolic), Heart Rate (BPM), Temperature (°F), Respiratory Rate, Oxygen Saturation ($\text{SpO}_2$), Weight (kg), Height (cm).
* **Automated Clinical Calculators**: Real-time Body Mass Index (BMI) calculation and classification (Underweight, Normal, Overweight, Obese).
* **Multi-Item Prescription Builder**: Dosage strength, frequency (e.g. 1-0-1), duration, and food intake instructions.
* **Thermal / Letterhead Print**: Formal doctor prescription slips with hospital branding.

### 💊 6. Pharmacy Inventory, Batch Tracking & Dispensing
* **Medicine Catalog**: Brand name, generic composition, dosage form (Tablet, Syrup, Injection, IV Fluid), and manufacturer details.
* **Batch & Expiry Monitoring**: Automated alerts for expired medications and near-expiry batches.
* **Stock Transactions**: Procurement Stock-In, Ward Adjustments, and Damaged stock scrapping.
* **Point-of-Sale Dispensing**: Prescription fulfillment with real-time inventory deduction and pricing in ₹.

### 🔬 7. Laboratory & Diagnostic Investigation Workflows
* **Investigation Catalog**: Reference ranges, units ($\text{mg/dL}$, $\text{g/dL}$), turnaround times, and specimen requirements (Blood, Urine, Sputum, Biopsy, X-Ray).
* **Diagnostic Order Pipeline**: Priority triage (`Routine`, `Urgent`, `STAT Emergency`).
* **Critical Finding Alerts**: Immediate high-priority warning badges for abnormal diagnostic parameters.
* **Printable Pathology Reports**: Formatted laboratory test reports with technician sign-off.

### 💳 8. Billing, Invoicing & Financial Accounting
* **Dynamic Multi-Item Invoice Builder**: Support for doctor consultation, room charges, surgery/procedures, pharmacy items, laboratory tests, and nursing fees.
* **Tax & Discount Engine**: Flat discount (₹) or percentage discount (%) with dynamic hospital VAT/Tax computation.
* **Partial & Full Payment Settlement**: Support for Cash, POS Debit/Credit Card, UPI / QR Code, Bank Wire (NEFT/RTGS), and Third-Party Insurance (TPA).
* **Thermal Payment Receipts & Tax Invoices**: Official printed financial vouchers.

---

## 5. Role-Based Access Control (RBAC) Matrix

CarePlus HMS implements strict permission tiers with role verification decorators preventing unauthorized horizontal or vertical privilege escalation:

| Feature / Module | Super Admin | Hospital Admin | Doctor | Nurse | Receptionist | Pharmacist | Lab Tech | Accountant |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **System Dashboard & KPI Stats** | ✅ Full | ✅ Full | ✅ Clinical | ✅ Ward | ✅ Front Desk | ✅ Inventory | ✅ Diagnostic | ✅ Financial |
| **Patient Registration & Search** | ✅ | ✅ | ✅ | ✅ | ✅ | 👁️ Read | 👁️ Read | 👁️ Read |
| **Doctor & Staff Onboarding** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Appointment Scheduling** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Inpatient Admissions & Beds** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Clinical Vitals & Medical Notes** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Prescription Generation** | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Pharmacy Stock & Dispensing** | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **Laboratory Orders & Results** | ✅ | ✅ | ✅ (Order) | ❌ | ❌ | ❌ | ✅ (Verify) | ❌ |
| **Invoicing & Payment Receipts** | ✅ | ✅ | ❌ | ❌ | ✅ (Create) | ❌ | ❌ | ✅ (Settle) |
| **Audit Logs & System Settings** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 6. Database Schema & Relational Models (17 Entities)

```
[User] 1──* [AuditLog]
[User] 1──* [Notification]
[Role] 1──* [User]
[Department] 1──* [Doctor]
[Department] 1──* [Staff]
[Doctor] 1──* [Appointment]
[Patient] 1──* [Appointment]
[Patient] 1──* [Admission] 1──1 [DischargeSummary]
[Room] 1──* [Bed] 1──* [Admission]
[Patient] 1──* [MedicalRecord]
[Patient] 1──* [Vitals]
[Patient] 1──* [Prescription] 1──* [PrescriptionItem]
[Medicine] 1──* [MedicineBatch]
[Medicine] 1──* [PharmacySaleItem] 1──* [PharmacySale]
[LabTest] 1──* [LabOrder] 1──1 [LabResult]
[Patient] 1──* [Invoice] 1──* [InvoiceItem]
[Invoice] 1──* [Payment]
[InventoryItem] 1──* [InventoryTransaction]
[HospitalSetting] (Dynamic Key-Value Store)
```

---

## 7. Pre-Configured Demonstration Accounts

| User Role | Login Email | Password | Primary Purpose |
| :--- | :--- | :--- | :--- |
| **👑 Super Admin** | `admin@careplus.com` | `Admin@123` | Complete root system administration, audit logs, settings |
| **🏥 Hospital Admin** | `hospital.admin@careplus.com` | `Admin@123` | Facility operations, doctor rosters, staff management |
| **👨‍⚕️ Doctor** | `doctor@careplus.com` | `Doctor@123` | Patient encounters, prescriptions, lab orders |
| **👩‍⚕️ Nurse** | `nurse@careplus.com` | `Nurse@123` | Inpatient bed management, patient vital recordings |
| **📋 Receptionist** | `reception@careplus.com` | `Reception@123` | Front-desk triage, OPD appointment booking |
| **💊 Pharmacist** | `pharmacy@careplus.com` | `Pharmacy@123` | Drug stock inventory, prescription dispensing |
| **🔬 Lab Technician** | `lab@careplus.com` | `Lab@123` | Diagnostic queue, pathology results entry |
| **💳 Accountant** | `accountant@careplus.com` | `Account@123` | Patient invoicing, settlement receipt generation |

---

## 8. Quality Assurance & Test Verification

The application includes an automated test suite with **19 comprehensive integration and unit tests**:

* **Authentication Tests**: Login validation, bad password rejection, session logout, and RBAC privilege checks.
* **Patient Management Tests**: Registration validation, uniqueness checks, search filters, and full profile rendering.
* **Appointment Tests**: Slot booking, status state machine transitions, and doctor collision detection.
* **Admission Tests**: Bed occupancy state toggling upon inpatient admission and release on discharge.
* **Clinical Tests**: Multi-item prescription creation and print view formatting.
* **Laboratory Tests**: Diagnostic order creation, sample tracking, and result entry.
* **Pharmacy Tests**: Medicine batch creation, expiry checking, and stock adjustments.
* **Billing Tests**: Invoice subtotal/tax/discount auto-calculation, partial payment, and full balance settlement.

```
============================== 19 passed in 100.81s ==============================
```

---

## 9. Conclusion & Technical Merits

The **CarePlus Hospital Management System** stands as an end-to-end, production-ready solution that bridges healthcare administrative needs with reliable modern web technologies. Its serverless-ready architecture, clean code structure, granular security policies, and intuitive UI make it a standout software engineering project suitable for college submissions, professional portfolios, and enterprise prototyping.
