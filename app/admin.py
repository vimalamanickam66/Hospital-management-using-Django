from django.contrib import admin
from .models import Patient, Doctor, Appointment, Payment, RoomAllotment,Service,Invoice,Billing,Prescription,Medicine,Department

# Register your models here.
admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(Appointment)
admin.site.register(Payment)
admin.site.register(RoomAllotment)
admin.site.register(Service)
admin.site.register(Invoice)
admin.site.register(Billing)
admin.site.register(Prescription)
admin.site.register(Medicine)
admin.site.register(Department)