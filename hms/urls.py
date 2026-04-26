from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('facilities/', views.facilities, name='facilities'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('patients/', views.patients, name='patients'),
    path('doctors/', views.doctors, name='doctors'),
    path('departments/', views.departments, name='departments'),
    path('room_allotment/', views.room_allotment, name='room_allotment'),
    path('pending_details/', views.pending_details, name='pending_details'),
    path('receipt/<int:patient_id>/', views.receipt, name='patient_slip'),
    path('doctor/edit/<int:id>/', views.edit_doctor, name='edit_doctor'),
    path('doctor/delete/<int:id>/', views.delete_doctor, name='delete_doctor'),
    path('patient/edit/<int:id>/', views.edit_patient, name='edit_patient'),
    path('patient/delete/<int:id>/', views.delete_patient, name='delete_patient'),
    path('department/<int:id>/', views.department_detail, name='department_detail'),
    path('medicines/', views.medicines, name='medicines'),
    path('patient/<int:patient_id>/give-medicine/', views.give_medicine, name='give_medicine'),
    path('patient/<int:patient_id>/prescription/', views.add_prescription, name='add_prescription'),
    path('patient/<int:patient_id>/bill/', views.generate_bill, name='generate_bill'),
    path('patient/<int:patient_id>/discharge/', views.discharge_patient, name='discharge_patient'),
    path('appointments/', views.appointments, name='appointments'),
    path('appointments/book/', views.book_appointment, name='book_appointment'),
    path('appointments/<int:id>/confirm/', views.confirm_appointment, name='confirm_appointment'),
    path('appointments/<int:id>/cancel/', views.cancel_appointment, name='cancel_appointment'),

    # New features
    path('patient/<int:patient_id>/vitals/', views.vital_signs, name='vital_signs'),
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('send-reminders/', views.send_reminders, name='send_reminders'),
    path('test-email/', views.test_email, name='test_email'),
]