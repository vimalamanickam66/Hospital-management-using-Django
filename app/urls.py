from django.urls import path,include
from . import views
from .views import home_page, user_login,about_us
from .views import MedicineListCreate
from .views import invoice_print,generate_invoice

urlpatterns = [
    path('', views.home_page, name='home'),
    path('departments/', views.departments, name='departments'),
    path('medicine/', views.medicine_list, name='medicine'),
    path('medicine/add/', views.add_medicine, name='add_medicine'),
    path('medicine/edit/<int:id>/', views.edit_medicine, name='edit_medicine'),
    path('prescription/', views.prescription_and_bill, name='prescription'),
    path('delete_medicine/<int:medicine_id>/', views.delete_medicine, name='delete_medicine'),
    path("billing_dashboard/", views.billing_dashboard, name="billing_dashboard"),
    path("generate_invoice/", views.generate_invoice, name="generate_invoice"),
    path('invoice/search/', views.invoice_by_patient, name='invoice_by_patient'),
    path('details/<int:invoice_id>/', views.invoice_details, name='invoice_details'),
    path('invoice_print/<int:invoice_id>/', invoice_print, name='invoice_print'),
     path('get-patient-name/<int:patient_id>/', views.get_patient_name, name='get_patient_name'),
    # urls.py
    path('get_patient_details/', views.get_patient_details, name='get_patient_details'),
    #path('save_prescription/', views.save_prescription, name='save_prescription'), # You need to define this view
    #path('add_medicine/', views.add_medicine, name='add_medicine'),
    #path('edit_medicine/<int:id>/', views.edit_medicine, name='edit_medicine'),
    path('departments/cardiology.html', views.cardiology_view, name='cardiology'),
    path('departments/neurology.html', views.neurology, name='neurology'),
    path('departments/dermatology.html', views.dermatology, name='dermatology'),
    path('departments/orthopedics.html', views.orthopedics, name='orthopedics'),
    path('departments/gynecology.html', views.gynecology, name='gynecology'),
    path('departments/pediatrics.html', views.pediatrics, name='pediatrics'),
    path('about_us/', views.about_us, name='about_us'),
    path('index/', views.index, name='index'),
    path('calculate-bill/', views.calculate_bill, name='calculate_bill'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('add-patient/',views.add_patient,name='add-patient'),
    path('all-patients/',views.all_patients,name='all-patients'),
    path('add-doctor/',views.add_doctor,name='add-doctor'),
    path('all-doctors/',views.all_doctors,name='all-doctors'),
    path('patient-autocomplete/', views.patient_autocomplete, name='patient_autocomplete'),
    path('add-appointment/', views.add_appointment, name='add-appointment'),
    path('all-appointments/', views.all_appointments, name='all-appointments'),
    path('add-payment/', views.add_payment, name='add-payment'),
    path('all-payments/', views.all_payments, name='all-payments'),
    path('add-room/', views.add_room, name='add-room'),
    path('all-rooms/', views.all_rooms, name='all-rooms'),
] 
# analytics/urls.py
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, DoctorViewSet, AppointmentViewSet, PaymentViewSet, RoomAllotmentViewSet

router = DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'doctors', DoctorViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'room-allotments', RoomAllotmentViewSet)

urlpatterns += [
    path('api/', include(router.urls)),
]
