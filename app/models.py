from django.db import models

# Patient Model
class Patient(models.Model):
    patient_id = models.CharField(max_length=10, unique=True, blank=True, null=True)
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    age = models.PositiveIntegerField()
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    address = models.TextField()
    assigned_doctor = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.name
    def get_department(self):
        """Returns the specialization of the assigned doctor."""
        return self.assigned_doctor.specialization if self.assigned_doctor else "Not Assigned"    
    def save(self, *args, **kwargs):
        if not self.patient_id:
            last_patient = Patient.objects.order_by('-id').first()
            new_id_number = (last_patient.id + 1) if last_patient else 1
            self.patient_id = f'p{new_id_number}'
        super().save(*args, **kwargs)

#class Medicine(models.Model):
    #name = models.CharField(max_length=100)
    #price = models.DecimalField(max_digits=10, decimal_places=2)
    #quantity = models.IntegerField()
    #discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) 
    #def __str__(self):
        #return self.name
# Doctor Model
class Doctor(models.Model):
    AVAILABILITY_CHOICES = [
        ('Available', 'Available'),
        ('Not Available', 'Not Available'),
    ]
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    specialization = models.CharField(max_length=100)
    experience = models.PositiveIntegerField()  # Years of experience
    age = models.PositiveIntegerField()
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    address = models.TextField()
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='Available')

    def __str__(self):
        return self.name

# Appointment Model
class Appointment(models.Model):
    DEPARTMENTS = [
        ('Neurology', 'Neurology'),
        ('Gynecology', 'Gynecology'),
        ('Cardiology', 'Cardiology'),
        ('Orthopedics', 'Orthopedics'),
        ('Dermatology', 'Dermatology'),
        ('Pediatrics', 'Pediatrics'),

        # Add other departments as needed
    ]
    TIME_SLOTS = [
        ('10AM-11AM', '10AM-11AM'),
        ('10PM-11PM', '10PM-11PM'),
        ('06AM-07AM', '06AM-07AM'),
        # Add other time slots as needed
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    department = models.CharField(max_length=100, choices=DEPARTMENTS)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    time_slot = models.CharField(max_length=20, choices=TIME_SLOTS)
    token_number = models.CharField(max_length=40, unique=True)  # Auto-generated
    problem = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')


    def __str__(self):
        return f"{self.patient.name} - {self.doctor.name} on {self.appointment_date}"

#Services
class Service(models.Model):
    name = models.CharField(max_length=100)
    cost_of_treatment = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
    
    
# Payment Model
class Payment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    admission_date = models.DateField()
    discharge_date = models.DateField()
    services = models.ManyToManyField(Service)
    discount = models.PositiveIntegerField()  # Discount percentage
    paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=50, choices=[('Check', 'Check'), ('Card', 'Card'),('Cash', 'Cash')])
    card_check_number = models.CharField(max_length=50, blank=True, null=True)  # Optional

    def __str__(self):
        return f"Payment for {self.patient.name}"

# Room Allotment Model
class RoomAllotment(models.Model):
    ROOM_TYPES = [
        ('ICU', 'ICU'),
        ('General','General'),
        ('AC Room','AC Room'),
        # Add other room types as needed
    ]
    room_number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=50, choices=ROOM_TYPES)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    allotment_date = models.DateField()
    discharge_date = models.DateField()
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)

    def __str__(self):
        return f"Room {self.room_number} allotted to {self.patient.name}"


class Medicine(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) 
    def __str__(self):
        return self.name

class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    medicines = models.ManyToManyField(Medicine)
    created_at = models.DateTimeField(auto_now_add=True)
    doctor_name = models.CharField(max_length=100, null=True, blank=True)
    doctor_specialization = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return f"Prescription for {self.patient.name}"
class Department(models.Model):
    name = models.CharField(max_length=100)
    # Add any additional fields you need for the department

    def __str__(self):
        return self.name

class Billing(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    icd10_code = models.CharField(max_length=10)
    diagnosis = models.CharField(max_length=255)
    cpt_code = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[("Pending", "Pending"), ("Paid", "Paid")])
    invoice_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.id} - {self.patient.name}"
    def get_department(self):
        """Fetch department based on the patient's assigned doctor."""
        return self.patient.get_department()
    
class Invoice(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
        ('pending', 'Pending'),
    ]
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE,null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='invoices')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    def __str__(self):
        return f"Invoice #{self.id} for {self.patient.name}"