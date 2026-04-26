from django import forms
from django.contrib.auth.models import User
from .models import (Department, Doctor, Patient, RoomAllotment,
                     Prescription, Medicine, PatientMedicine,
                     Appointment, Bill, VitalSign)


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = '__all__'


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = '__all__'


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = '__all__'


class RoomAllotmentForm(forms.ModelForm):
    class Meta:
        model = RoomAllotment
        fields = '__all__'


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = '__all__'


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = '__all__'


class PatientMedicineForm(forms.ModelForm):
    class Meta:
        model = PatientMedicine
        fields = '__all__'


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['name', 'phone', 'email', 'department', 'doctor',
                  'appointment_date', 'message']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'message': forms.Textarea(attrs={'rows': 3}),
        }


class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['other_charges', 'is_paid']


class VitalSignForm(forms.ModelForm):
    class Meta:
        model = VitalSign
        fields = ['patient', 'blood_pressure', 'temperature',
                  'pulse', 'weight', 'oxygen_level', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }


class PasswordResetForm(forms.Form):
    username = forms.CharField(max_length=150)
    new_password = forms.CharField(widget=forms.PasswordInput, min_length=6)
    confirm_password = forms.CharField(widget=forms.PasswordInput, min_length=6)

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data