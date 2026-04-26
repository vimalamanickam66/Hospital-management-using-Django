
from django.contrib import admin
from .models import Department, Doctor, Patient, RoomAllotment

admin.site.register(Department)
admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(RoomAllotment)