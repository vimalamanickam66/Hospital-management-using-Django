from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.models import User
from .models import (Department, Doctor, Patient, RoomAllotment,
                     Prescription, Medicine, PatientMedicine,
                     Appointment, Bill, VitalSign)
from .forms import (DepartmentForm, DoctorForm, PatientForm,
                    RoomAllotmentForm, PrescriptionForm, MedicineForm,
                    PatientMedicineForm, AppointmentForm, BillForm,
                    VitalSignForm, PasswordResetForm)


# ─────────────────────────────────────────────
# NOTIFICATION HELPERS
# ─────────────────────────────────────────────

def send_sms(to_phone, message_body):
    """
    Send SMS using Vonage SDK v3+
    """
    try:
        from vonage import Auth, Vonage
        from vonage_sms import SmsMessage, SmsResponse
        from django.conf import settings

        # Clean phone number
        clean_phone = str(to_phone).strip().replace(' ', '')
        if clean_phone.startswith('+91'):
            clean_phone = clean_phone[3:]
        elif clean_phone.startswith('91') and len(clean_phone) == 12:
            clean_phone = clean_phone[2:]

        full_phone = f'91{clean_phone}'
        print(f"[SMS] Sending to {full_phone}...")

        client = Vonage(Auth(
            api_key=settings.VONAGE_API_KEY,
            api_secret=settings.VONAGE_API_SECRET
        ))

        message = SmsMessage(
            to=full_phone,
            from_=settings.VONAGE_FROM,
            text=message_body,
        )

        response: SmsResponse = client.sms.send(message)

        print(f"[SMS] Vonage response: {response}")

        if response.messages[0].status == '0':
            print(f"[SMS] ✅ Sent to {full_phone}")
            return True
        else:
            print(f"[SMS] ❌ Failed: {response.messages[0].error_text}")
            return False

    except Exception as e:
        print(f"[SMS] ❌ Error: {e}")
        return False


def send_styled_email(subject, to_email, html_content):
    """Send styled HTML email via Gmail SMTP"""
    try:
        from django.core.mail import EmailMultiAlternatives
        from django.conf import settings
        print(f"[Email] Sending '{subject}' to {to_email}...")
        msg = EmailMultiAlternatives(
            subject=subject,
            body='Please view this in an HTML-capable email client.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        print(f"[Email] ✅ Sent to {to_email}")
        return True
    except Exception as e:
        print(f"[Email] ❌ Failed: {type(e).__name__}: {e}")
        return False


# ─────────────────────────────────────────────
# EMAIL HTML TEMPLATES
# ─────────────────────────────────────────────

def appointment_confirmed_email(appointment):
    return f"""
    <!DOCTYPE html><html><head>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f4f7fa; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #003580, #0077cc); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .body {{ padding: 30px; }}
        .detail-row {{ display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #f0f0f0; font-size: 15px; }}
        .detail-row span:first-child {{ color: #888; }}
        .detail-row span:last-child {{ font-weight: 600; color: #1a2740; }}
        .badge {{ background: #d4edda; color: #155724; padding: 10px 24px; border-radius: 20px; display: inline-block; font-weight: 700; margin: 20px 0; font-size: 16px; }}
        .footer {{ background: #f8fafc; padding: 20px; text-align: center; color: #888; font-size: 13px; }}
        .note {{ background: #dbeafe; border-left: 4px solid #3b82f6; padding: 14px 18px; border-radius: 8px; margin-top: 18px; font-size: 14px; color: #1e40af; }}
    </style></head><body>
        <div class="container">
            <div class="header">
                <h1>🏥 City Care Hospital</h1>
                <p style="margin:5px 0 0;opacity:0.85;">Appointment Confirmed</p>
            </div>
            <div class="body">
                <p style="font-size:16px;">Dear <strong>{appointment.name}</strong>,</p>
                <p style="color:#555;margin:10px 0 20px;">Your appointment has been <strong>confirmed</strong> by our team.</p>
                <div class="detail-row"><span>📅 Appointment Date</span><span>{appointment.appointment_date}</span></div>
                <div class="detail-row"><span>🏥 Department</span><span>{appointment.department}</span></div>
                <div class="detail-row"><span>👨‍⚕️ Doctor</span><span>{appointment.doctor if appointment.doctor else 'Will be assigned'}</span></div>
                <div class="detail-row"><span>📞 Contact</span><span>{appointment.phone}</span></div>
                <div style="text-align:center;margin-top:20px;">
                    <span class="badge">✅ Appointment Confirmed</span>
                </div>
                <div class="note">
                    ⏰ Please arrive <strong>15 minutes early</strong>.
                    Bring any previous medical reports.
                    For queries, call <strong>+91 98765 43210</strong>.
                </div>
            </div>
            <div class="footer">
                © 2026 City Care Hospital | 123 Health Street, Chennai, Tamil Nadu
            </div>
        </div>
    </body></html>"""


def appointment_cancelled_email(appointment):
    return f"""
    <!DOCTYPE html><html><head>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f4f7fa; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #b91c1c, #ef4444); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .body {{ padding: 30px; }}
        .detail-row {{ display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #f0f0f0; font-size: 15px; }}
        .detail-row span:first-child {{ color: #888; }}
        .detail-row span:last-child {{ font-weight: 600; color: #1a2740; }}
        .badge {{ background: #fee2e2; color: #991b1b; padding: 10px 24px; border-radius: 20px; display: inline-block; font-weight: 700; margin: 20px 0; font-size: 16px; }}
        .footer {{ background: #f8fafc; padding: 20px; text-align: center; color: #888; font-size: 13px; }}
        .note {{ background: #fef9ec; border-left: 4px solid #f59e0b; padding: 14px 18px; border-radius: 8px; margin-top: 18px; font-size: 14px; color: #92400e; }}
    </style></head><body>
        <div class="container">
            <div class="header">
                <h1>🏥 City Care Hospital</h1>
                <p style="margin:5px 0 0;opacity:0.85;">Appointment Cancelled</p>
            </div>
            <div class="body">
                <p style="font-size:16px;">Dear <strong>{appointment.name}</strong>,</p>
                <p style="color:#555;margin:10px 0 20px;">Your appointment has been <strong>cancelled</strong>.</p>
                <div class="detail-row"><span>📅 Appointment Date</span><span>{appointment.appointment_date}</span></div>
                <div class="detail-row"><span>🏥 Department</span><span>{appointment.department}</span></div>
                <div class="detail-row"><span>👨‍⚕️ Doctor</span><span>{appointment.doctor if appointment.doctor else 'Was not assigned'}</span></div>
                <div class="detail-row"><span>📞 Contact</span><span>{appointment.phone}</span></div>
                <div style="text-align:center;margin-top:20px;">
                    <span class="badge">❌ Appointment Cancelled</span>
                </div>
                <div class="note">
                    📞 To rebook, call <strong>+91 98765 43210</strong>
                    or visit our website. We apologize for any inconvenience.
                </div>
            </div>
            <div class="footer">
                © 2026 City Care Hospital | 123 Health Street, Chennai, Tamil Nadu
            </div>
        </div>
    </body></html>"""


def discharge_summary_email(patient, bill):
    return f"""
    <!DOCTYPE html><html><head>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f4f7fa; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #1b5e20, #2e7d32); color: white; padding: 30px; text-align: center; }}
        .body {{ padding: 30px; }}
        .detail-row {{ display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #f0f0f0; font-size: 15px; }}
        .detail-row span:first-child {{ color: #888; }}
        .detail-row span:last-child {{ font-weight: 600; color: #1a2740; }}
        .total-box {{ background: linear-gradient(135deg, #003580, #0077cc); color: white; padding: 18px; border-radius: 10px; display: flex; justify-content: space-between; margin: 20px 0; }}
        .footer {{ background: #f8fafc; padding: 20px; text-align: center; color: #888; font-size: 13px; }}
    </style></head><body>
        <div class="container">
            <div class="header">
                <h1>🏥 City Care Hospital</h1>
                <p style="margin:5px 0 0;opacity:0.85;">Discharge Summary</p>
            </div>
            <div class="body">
                <p style="font-size:16px;">Dear <strong>{patient.name}</strong>,</p>
                <p style="color:#555;margin:10px 0 20px;">You have been successfully discharged.</p>
                <div class="detail-row"><span>🧑 Patient</span><span>{patient.name}</span></div>
                <div class="detail-row"><span>🆔 Patient ID</span><span>{patient.patient_id}</span></div>
                <div class="detail-row"><span>🩺 Disease</span><span>{patient.disease}</span></div>
                <div class="detail-row"><span>👨‍⚕️ Doctor</span><span>{patient.assigned_doctor}</span></div>
                <div class="detail-row"><span>🛏️ Room Charge</span><span>₹{bill.room_charge}</span></div>
                <div class="detail-row"><span>👨‍⚕️ Doctor Fee</span><span>₹{bill.doctor_fee}</span></div>
                <div class="detail-row"><span>💊 Medicine</span><span>₹{bill.medicine_charge}</span></div>
                <div class="detail-row"><span>📋 Other</span><span>₹{bill.other_charges}</span></div>
                <div class="total-box">
                    <span style="font-size:16px;font-weight:600;">Total Amount</span>
                    <span style="font-size:22px;font-weight:700;">₹{bill.total_amount}</span>
                </div>
                <p style="color:#555;font-size:14px;">Wishing you a speedy recovery! Call <strong>+91 98765 43210</strong>.</p>
            </div>
            <div class="footer">© 2026 City Care Hospital</div>
        </div>
    </body></html>"""


def reminder_email_html(appointment):
    return f"""
    <!DOCTYPE html><html><head>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f4f7fa; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #e65100, #f57c00); color: white; padding: 30px; text-align: center; }}
        .body {{ padding: 30px; }}
        .reminder-box {{ background: #fff3e0; border-left: 5px solid #f57c00; padding: 18px; border-radius: 8px; margin: 20px 0; }}
        .detail-row {{ display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #f0f0f0; font-size: 15px; }}
        .detail-row span:first-child {{ color: #888; }}
        .detail-row span:last-child {{ font-weight: 600; color: #1a2740; }}
        .footer {{ background: #f8fafc; padding: 20px; text-align: center; color: #888; font-size: 13px; }}
    </style></head><body>
        <div class="container">
            <div class="header">
                <h1>🔔 Appointment Reminder</h1>
                <p style="opacity:0.9;">City Care Hospital</p>
            </div>
            <div class="body">
                <p style="font-size:16px;">Dear <strong>{appointment.name}</strong>,</p>
                <div class="reminder-box">
                    <strong>⏰ Your appointment is TOMORROW!</strong><br>
                    Please make sure you are prepared and arrive on time.
                </div>
                <div class="detail-row"><span>📅 Date</span><span>{appointment.appointment_date}</span></div>
                <div class="detail-row"><span>🏥 Department</span><span>{appointment.department}</span></div>
                <div class="detail-row"><span>👨‍⚕️ Doctor</span><span>{appointment.doctor if appointment.doctor else 'Will be assigned'}</span></div>
                <p style="color:#555;font-size:14px;margin-top:20px;">
                    Please arrive <strong>15 minutes early</strong>.
                    Call <strong>+91 98765 43210</strong>.
                </p>
            </div>
            <div class="footer">© 2026 City Care Hospital</div>
        </div>
    </body></html>"""


# ─────────────────────────────────────────────
# TEST EMAIL VIEW
# ─────────────────────────────────────────────

@login_required(login_url='login')
def test_email(request):
    to_email = request.GET.get('to', '')
    status = None
    error_msg = None

    if to_email:
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            print(f"[TEST] Host:{settings.EMAIL_HOST} Port:{settings.EMAIL_PORT} User:{settings.EMAIL_HOST_USER}")
            result = send_mail(
                subject='✅ Test Email - City Care Hospital',
                message='This is a test email from City Care Hospital Django app.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                fail_silently=False,
            )
            status = 'success' if result == 1 else 'failed'
        except Exception as e:
            status = 'error'
            error_msg = str(e)
            print(f"[TEST EMAIL] ❌ {type(e).__name__}: {e}")

    from django.http import HttpResponse
    html = f"""
    <!DOCTYPE html><html><head>
    <style>
        body{{font-family:Arial,sans-serif;background:#f4f7fa;padding:40px;}}
        .box{{max-width:600px;margin:0 auto;background:white;padding:30px;border-radius:12px;}}
        h2{{color:#004d99;}}
        .success{{background:#d4edda;color:#155724;padding:15px;border-radius:8px;margin:15px 0;border-left:5px solid #28a745;}}
        .error{{background:#f8d7da;color:#721c24;padding:15px;border-radius:8px;margin:15px 0;border-left:5px solid #dc3545;}}
        input{{width:100%;padding:10px;border:1.5px solid #dde3ec;border-radius:8px;font-size:14px;margin:10px 0;box-sizing:border-box;}}
        button{{background:linear-gradient(135deg,#004d99,#0077cc);color:white;padding:12px;border:none;border-radius:8px;font-size:14px;cursor:pointer;width:100%;}}
    </style></head><body>
    <div class="box">
        <h2>📧 Email Test</h2>
        {"<div class='success'>✅ Email sent to " + to_email + "!</div>" if status=='success' else ""}
        {"<div class='error'>❌ Failed: " + (error_msg or '') + "</div>" if status=='error' else ""}
        <form method="GET">
            <input type="email" name="to" value="{to_email}" placeholder="yourmail@gmail.com" required>
            <button type="submit">📤 Send Test Email</button>
        </form>
        <a href="/dashboard/" style="display:inline-block;margin-top:15px;color:#004d99;">← Dashboard</a>
    </div></body></html>"""
    return HttpResponse(html)


# ─────────────────────────────────────────────
# PUBLIC VIEWS
# ─────────────────────────────────────────────

def home(request):
    departments = Department.objects.all()
    doctors = Doctor.objects.filter(available=True)[:6]
    return render(request, 'hms/home.html', {
        'departments': departments,
        'doctors': doctors,
    })


def facilities(request):
    return render(request, 'hms/facilities.html')


def department_detail(request, id):
    department = get_object_or_404(Department, id=id)
    doctors = Doctor.objects.filter(department=department)
    available_count = doctors.filter(available=True).count()
    return render(request, 'hms/department_detail.html', {
        'department': department,
        'doctors': doctors,
        'available_count': available_count,
    })


def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                '✅ Appointment booked successfully! '
                'Our team will review and confirm shortly. '
                'You will receive an email once confirmed.'
            )
            return redirect('book_appointment')
    else:
        form = AppointmentForm()

    return render(request, 'hms/book_appointment.html', {
        'form': form,
        'departments': Department.objects.all(),
        'doctors': Doctor.objects.filter(available=True),
    })


# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────

def login_view(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        user = authenticate(request, username=username, password=password)
        if user and user.is_superuser:
            login(request, user)
            return redirect('dashboard')
        else:
            error = "Invalid admin username or password"
    return render(request, 'hms/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────

@login_required(login_url='login')
def dashboard(request):
    total_patients       = Patient.objects.count()
    total_doctors        = Doctor.objects.count()
    total_departments    = Department.objects.count()
    total_rooms          = RoomAllotment.objects.count()
    pending_patients     = Patient.objects.filter(status='Waiting')
    available_doctors    = Doctor.objects.filter(available=True)
    waiting_count        = Patient.objects.filter(status='Waiting').count()
    checked_count        = Patient.objects.filter(status='Checked').count()
    admitted_count       = Patient.objects.filter(status='Admitted').count()
    discharged_count     = Patient.objects.filter(status='Discharged').count()
    pending_appointments = Appointment.objects.filter(status='Pending').count()

    from django.db.models import Count
    from django.utils import timezone
    current_year = timezone.now().year
    monthly_data = (
        Patient.objects
        .filter(appointment_date__year=current_year)
        .values('appointment_date__month')
        .annotate(count=Count('id'))
        .order_by('appointment_date__month')
    )
    monthly_counts = [0] * 12
    for entry in monthly_data:
        monthly_counts[entry['appointment_date__month'] - 1] = entry['count']

    return render(request, 'hms/dashboard.html', {
        'total_patients':       total_patients,
        'total_doctors':        total_doctors,
        'total_departments':    total_departments,
        'total_rooms':          total_rooms,
        'pending_patients':     pending_patients,
        'available_doctors':    available_doctors,
        'waiting_count':        waiting_count,
        'checked_count':        checked_count,
        'admitted_count':       admitted_count,
        'discharged_count':     discharged_count,
        'monthly_counts':       monthly_counts,
        'pending_appointments': pending_appointments,
    })


# ─────────────────────────────────────────────
# GENERIC CRUD
# ─────────────────────────────────────────────

def handle_crud(request, model, form_class, template_name):
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect(request.path)
    else:
        form = form_class()

    objects_list = model.objects.all().order_by('-id')
    paginator    = Paginator(objects_list, 10)
    page_obj     = paginator.get_page(request.GET.get('page'))

    return render(request, template_name, {
        'form': form,
        f'{model.__name__.lower()}_list': page_obj
    })


# ─────────────────────────────────────────────
# PATIENT VIEWS
# ─────────────────────────────────────────────

@login_required(login_url='login')
def patients(request):
    search_query = request.GET.get('patient_id', '').strip()
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('patients')
    else:
        form = PatientForm()

    if search_query:
        try:
            numeric_id = int(search_query)
            patient_list = (
                Patient.objects.filter(id=numeric_id) |
                Patient.objects.filter(patient_id=str(numeric_id))
            )
        except ValueError:
            patient_list = Patient.objects.none()
    else:
        patient_list = Patient.objects.all().order_by('-id')

    return render(request, 'hms/patients.html', {
        'form':         form,
        'patient_list': patient_list,
        'search_query': search_query,
    })


@login_required(login_url='login')
def edit_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    form = PatientForm(request.POST or None, instance=patient)
    if form.is_valid():
        form.save()
        return redirect('patients')
    return render(request, 'hms/edit_patient.html', {'form': form, 'patient': patient})


@login_required(login_url='login')
def delete_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    if request.method == "POST":
        patient.delete()
        return redirect('patients')
    return render(request, 'hms/delete_patient.html', {'patient': patient})


@login_required(login_url='login')
def receipt(request, patient_id):
    patient       = get_object_or_404(Patient, id=patient_id)
    prescriptions = Prescription.objects.filter(patient=patient)
    room          = RoomAllotment.objects.filter(patient=patient).first()
    room_charge   = room.room_charge if room else 0
    doctor_fee    = patient.assigned_doctor.fee if patient.assigned_doctor else 0
    other_charges = 100
    total_amount  = room_charge + doctor_fee + other_charges
    return render(request, 'hms/receipt.html', {
        'patient':       patient,
        'prescriptions': prescriptions,
        'room':          room,
        'room_charge':   room_charge,
        'doctor_fee':    doctor_fee,
        'other_charges': other_charges,
        'total_amount':  total_amount,
    })


@login_required(login_url='login')
def discharge_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == 'POST':
        patient.status = 'Discharged'
        patient.save()

        room = RoomAllotment.objects.filter(patient=patient).first()
        if room:
            from django.utils import timezone
            room.discharge_date = timezone.now().date()
            room.save()

        # Send discharge SMS
        send_sms(
            patient.phone,
            f"Dear {patient.name}, you have been discharged from City Care Hospital. "
            f"Wishing you a speedy recovery! Call: +91 98765 43210"
        )

        # Send discharge email
        bill = Bill.objects.filter(patient=patient).first()
        if bill:
            appt = Appointment.objects.filter(
                name=patient.name, phone=patient.phone
            ).first()
            if appt and appt.email:
                send_styled_email(
                    subject='Discharge Summary - City Care Hospital',
                    to_email=appt.email,
                    html_content=discharge_summary_email(patient, bill)
                )

        messages.success(
            request,
            f'{patient.name} discharged successfully.'
        )
        return redirect('patients')

    return render(request, 'hms/discharge_patient.html', {'patient': patient})


# ─────────────────────────────────────────────
# DOCTOR VIEWS
# ─────────────────────────────────────────────

@login_required(login_url='login')
def doctors(request):
    return handle_crud(request, Doctor, DoctorForm, 'hms/doctors.html')


@login_required(login_url='login')
def edit_doctor(request, id):
    doctor = get_object_or_404(Doctor, id=id)
    form = DoctorForm(request.POST or None, instance=doctor)
    if form.is_valid():
        form.save()
        return redirect('doctors')
    return render(request, 'hms/edit_doctor.html', {'form': form, 'doctor': doctor})


@login_required(login_url='login')
def delete_doctor(request, id):
    doctor = get_object_or_404(Doctor, id=id)
    if request.method == "POST":
        doctor.delete()
        return redirect('doctors')
    return render(request, 'hms/delete_doctor.html', {'doctor': doctor})


# ─────────────────────────────────────────────
# OTHER CRUD
# ─────────────────────────────────────────────

@login_required(login_url='login')
def departments(request):
    return handle_crud(request, Department, DepartmentForm, 'hms/departments.html')


@login_required(login_url='login')
def room_allotment(request):
    return handle_crud(request, RoomAllotment, RoomAllotmentForm, 'hms/room_allotment.html')


@login_required(login_url='login')
def pending_details(request):
    pending_patients = Patient.objects.filter(status='Waiting')
    paginator = Paginator(pending_patients, 10)
    page_obj  = paginator.get_page(request.GET.get('page'))
    return render(request, 'hms/pending_details.html', {'pending_patients': page_obj})


@login_required(login_url='login')
def medicines(request):
    return handle_crud(request, Medicine, MedicineForm, 'hms/medicines.html')


# ─────────────────────────────────────────────
# MEDICINE & PRESCRIPTION
# ─────────────────────────────────────────────

@login_required(login_url='login')
def give_medicine(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == 'POST':
        form = PatientMedicineForm(request.POST)
        if form.is_valid():
            pm = form.save(commit=False)
            pm.medicine.quantity -= pm.quantity
            pm.medicine.save()
            pm.save()
            return redirect('give_medicine', patient_id=patient_id)
    else:
        form = PatientMedicineForm(initial={'patient': patient})

    given_medicines = PatientMedicine.objects.filter(patient=patient).order_by('-given_date')
    return render(request, 'hms/give_medicine.html', {
        'form':            form,
        'patient':         patient,
        'given_medicines': given_medicines,
    })


@login_required(login_url='login')
def add_prescription(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_prescription', patient_id=patient_id)
    else:
        form = PrescriptionForm(initial={'patient': patient})

    prescriptions = Prescription.objects.filter(patient=patient).order_by('-created_at')
    return render(request, 'hms/add_prescription.html', {
        'form':          form,
        'patient':       patient,
        'prescriptions': prescriptions,
    })


# ─────────────────────────────────────────────
# BILLING
# ─────────────────────────────────────────────

@login_required(login_url='login')
def generate_bill(request, patient_id):
    patient         = get_object_or_404(Patient, id=patient_id)
    room            = RoomAllotment.objects.filter(patient=patient).first()
    given_medicines = PatientMedicine.objects.filter(patient=patient)
    room_charge     = room.room_charge if room else 0
    doctor_fee      = patient.assigned_doctor.fee if patient.assigned_doctor else 0
    medicine_charge = sum(pm.total_price for pm in given_medicines)
    existing_bill   = Bill.objects.filter(patient=patient).first()

    if request.method == 'POST':
        other_charges = float(request.POST.get('other_charges', 0))
        is_paid       = request.POST.get('is_paid') == 'on'
        total = (float(room_charge) + float(doctor_fee) +
                 float(medicine_charge) + other_charges)

        if existing_bill:
            existing_bill.room_charge     = room_charge
            existing_bill.doctor_fee      = doctor_fee
            existing_bill.medicine_charge = medicine_charge
            existing_bill.other_charges   = other_charges
            existing_bill.total_amount    = total
            existing_bill.is_paid         = is_paid
            existing_bill.save()
            bill = existing_bill
        else:
            bill = Bill.objects.create(
                patient=patient,
                room_charge=room_charge,
                doctor_fee=doctor_fee,
                medicine_charge=medicine_charge,
                other_charges=other_charges,
                total_amount=total,
                is_paid=is_paid,
            )

        return render(request, 'hms/bill.html', {
            'patient':         patient,
            'bill':            bill,
            'room':            room,
            'given_medicines': given_medicines,
        })

    other_charges = existing_bill.other_charges if existing_bill else 0
    total = (float(room_charge) + float(doctor_fee) +
             float(medicine_charge) + float(other_charges))

    return render(request, 'hms/generate_bill.html', {
        'patient':         patient,
        'room':            room,
        'room_charge':     room_charge,
        'doctor_fee':      doctor_fee,
        'medicine_charge': medicine_charge,
        'other_charges':   other_charges,
        'total':           total,
        'given_medicines': given_medicines,
        'existing_bill':   existing_bill,
    })


# ─────────────────────────────────────────────
# APPOINTMENTS
# ─────────────────────────────────────────────

@login_required(login_url='login')
def appointments(request):
    all_appointments = Appointment.objects.all().order_by('-created_at')
    paginator = Paginator(all_appointments, 10)
    page_obj  = paginator.get_page(request.GET.get('page'))
    return render(request, 'hms/appointments.html', {'appointments': page_obj})


@login_required(login_url='login')
def confirm_appointment(request, id):
    appointment = get_object_or_404(Appointment, id=id)
    appointment.status = 'Confirmed'
    appointment.save()

    # ── SMS ──
    sms_sent = send_sms(
        appointment.phone,
        f"Dear {appointment.name}, your appointment at City Care Hospital "
        f"on {appointment.appointment_date} is CONFIRMED! "
        f"Dept: {appointment.department}. "
        f"Please arrive 15 min early. Call: +91 98765 43210"
    )

    # ── Email ──
    email_sent = False
    if appointment.email:
        email_sent = send_styled_email(
            subject='✅ Appointment Confirmed - City Care Hospital',
            to_email=appointment.email,
            html_content=appointment_confirmed_email(appointment)
        )

    # ── Build success message ──
    notif_parts = []
    if sms_sent:   notif_parts.append(f'SMS sent to {appointment.phone}')
    if email_sent: notif_parts.append(f'Email sent to {appointment.email}')
    if not notif_parts:
        notif_parts.append('Email/SMS failed — check terminal')

    messages.success(
        request,
        f'✅ Confirmed for {appointment.name}. ' + ' & '.join(notif_parts) + '.'
    )
    return redirect('appointments')

@login_required(login_url='login')
def cancel_appointment(request, id):
    appointment = get_object_or_404(Appointment, id=id)
    appointment.status = 'Cancelled'
    appointment.save()

    # ── SMS ──
    sms_sent = send_sms(
        appointment.phone,
        f"Dear {appointment.name}, your appointment on "
        f"{appointment.appointment_date} at City Care Hospital "
        f"has been CANCELLED. "
        f"To rebook call: +91 98765 43210"
    )

    # ── Email ──
    email_sent = False
    if appointment.email:
        email_sent = send_styled_email(
            subject='❌ Appointment Cancelled - City Care Hospital',
            to_email=appointment.email,
            html_content=appointment_cancelled_email(appointment)
        )

    # ── Build message ──
    notif_parts = []
    if sms_sent:   notif_parts.append(f'SMS sent to {appointment.phone}')
    if email_sent: notif_parts.append(f'Email sent to {appointment.email}')
    if not notif_parts:
        notif_parts.append('Email/SMS failed — check terminal')

    messages.success(
        request,
        f'❌ Cancelled for {appointment.name}. ' + ' & '.join(notif_parts) + '.'
    )
    return redirect('appointments')

# ─────────────────────────────────────────────
# NEW FEATURES
# ─────────────────────────────────────────────

@login_required(login_url='login')
def vital_signs(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == 'POST':
        form = VitalSignForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vital signs recorded successfully.')
            return redirect('vital_signs', patient_id=patient_id)
    else:
        form = VitalSignForm(initial={'patient': patient})

    vitals_history = VitalSign.objects.filter(patient=patient).order_by('-recorded_at')
    return render(request, 'hms/vital_signs.html', {
        'form':           form,
        'patient':        patient,
        'vitals_history': vitals_history,
    })


@login_required(login_url='login')
def password_reset_view(request):
    form = PasswordResetForm()
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            username     = form.cleaned_data['username']
            new_password = form.cleaned_data['new_password']
            try:
                user = User.objects.get(username=username)
                user.set_password(new_password)
                user.save()
                messages.success(
                    request,
                    f'Password for "{username}" reset successfully.'
                )
                return redirect('password_reset')
            except User.DoesNotExist:
                messages.error(request, f'User "{username}" not found.')

    users = User.objects.all().order_by('username')
    return render(request, 'hms/password_reset.html', {
        'form':  form,
        'users': users,
    })


@login_required(login_url='login')
def send_reminders(request):
    from django.utils import timezone
    import datetime

    tomorrow = timezone.now().date() + datetime.timedelta(days=1)
    tomorrow_appointments = Appointment.objects.filter(
        appointment_date=tomorrow,
        status='Confirmed'
    )

    sent_count = 0
    for appt in tomorrow_appointments:
        send_sms(
            appt.phone,
            f"Reminder: Dear {appt.name}, your appointment at City Care Hospital "
            f"is TOMORROW ({appt.appointment_date}). "
            f"Please arrive 15 min early. Call: +91 98765 43210"
        )
        if appt.email:
            send_styled_email(
                subject='Appointment Reminder - City Care Hospital',
                to_email=appt.email,
                html_content=reminder_email_html(appt)
            )
        sent_count += 1

    messages.success(
        request,
        f'Reminders sent to {sent_count} patient(s) with appointments tomorrow.'
    )
    return redirect('appointments')