from app.forms.auth_forms import LoginForm, ChangePasswordForm, UserProfileForm, UserAdminForm
from app.forms.patient_forms import PatientForm
from app.forms.doctor_forms import DoctorForm
from app.forms.appointment_forms import AppointmentForm, AppointmentStatusForm
from app.forms.admission_forms import AdmissionForm, DischargeForm, BedTransferForm
from app.forms.clinical_forms import MedicalRecordForm, VitalsForm, PrescriptionForm
from app.forms.pharmacy_forms import MedicineForm, StockAdjustmentForm
from app.forms.lab_forms import LabTestForm, LabOrderForm, LabResultForm
from app.forms.billing_forms import InvoiceForm, PaymentForm
from app.forms.inventory_forms import InventoryItemForm, InventoryTransactionForm
from app.forms.staff_forms import StaffForm
from app.forms.settings_forms import HospitalSettingForm

__all__ = [
    'LoginForm',
    'ChangePasswordForm',
    'UserProfileForm',
    'UserAdminForm',
    'PatientForm',
    'DoctorForm',
    'AppointmentForm',
    'AppointmentStatusForm',
    'AdmissionForm',
    'DischargeForm',
    'BedTransferForm',
    'MedicalRecordForm',
    'VitalsForm',
    'PrescriptionForm',
    'MedicineForm',
    'StockAdjustmentForm',
    'LabTestForm',
    'LabOrderForm',
    'LabResultForm',
    'InvoiceForm',
    'PaymentForm',
    'InventoryItemForm',
    'InventoryTransactionForm',
    'StaffForm',
    'HospitalSettingForm',
]
