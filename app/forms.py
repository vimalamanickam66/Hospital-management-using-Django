# forms.py
from django import forms
from .models import Medicine

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name', 'price','quantity','discount']
from django import forms
from .models import Billing, Patient

class InvoiceForm(forms.ModelForm):
    patient = forms.ModelChoiceField(queryset=Patient.objects.all(), required=True)
    diagnosis = forms.CharField(max_length=255, required=True)
    amount = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
    symptoms = forms.CharField(widget=forms.Textarea, required=False)
    class Meta:
        model = Billing
        fields = ['patient', 'diagnosis', 'amount']
