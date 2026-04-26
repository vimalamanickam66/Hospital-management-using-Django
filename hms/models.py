from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Doctor(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    specialization = models.CharField(max_length=50, blank=True)
    available = models.BooleanField(default=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name


class Patient(models.Model):
    STATUS_CHOICES = (
        ('Waiting', 'Waiting'),
        ('Checked', 'Checked'),
        ('Admitted', 'Admitted'),
        ('Discharged', 'Discharged'),
    )
    patient_id = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    disease = models.CharField(max_length=100)
    assigned_doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    appointment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Waiting')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.patient_id:
            last_patient = Patient.objects.order_by('-id').first()
            if last_patient and last_patient.patient_id:
                try:
                    last_number = int(last_patient.patient_id.replace('PAT', ''))
                    new_number = last_number + 1
                except:
                    new_number = 1
            else:
                new_number = 1
            self.patient_id = f"PAT{new_number:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class RoomAllotment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=10)
    bed_number = models.CharField(max_length=5)
    room_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    allotted_date = models.DateField(auto_now_add=True)
    discharge_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.patient.name} - {self.room_number}"


class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.patient.name}"


class Medicine(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class PatientMedicine(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    given_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.medicine.name} for {self.patient.name}"

    @property
    def total_price(self):
        return self.quantity * self.medicine.price


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    )
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    appointment_date = models.DateField()
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.appointment_date}"


class Bill(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    room_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    doctor_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    medicine_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Bill for {self.patient.name}"


class VitalSign(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    blood_pressure = models.CharField(max_length=20, blank=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    pulse = models.IntegerField(null=True, blank=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    oxygen_level = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Vitals for {self.patient.name} at {self.recorded_at}"