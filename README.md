# 🏥 Hospital Management System (HMS)

A complete **web-based Hospital Management System** developed using **Django REST Framework** for backend services, **Bootstrap** for frontend UI, and **Morris.js** for data visualization. This system enables efficient management of hospital operations, patient records, appointments, billing, and administrative tasks.

---

## ⚙️ Key Features

- 🧑‍⚕️ Patient registration & medical records
- 📅 Appointment scheduling
- 💊 Doctor & department management
- 💵 Billing and invoice generation
- 📊 Dashboard with Morris.js charts
- 🏥 Role-based access control (admin, doctor, receptionist, etc.)
- 🗂️ Inventory and staff management
- 🔐 Secure authentication system

---

## 🛠️ Tech Stack

| Layer         | Technology                    |
|---------------|-------------------------------|
| **Backend**   | Django REST Framework         |
| **Frontend**  | HTML, CSS,JavaScript,Bootstrap|
| **Database**  | SQLite (default),             |
| **Charts**    | Morris.js, jQuery             |
| Authentication| Django Auth                   |

---

### 1. Clone the repository


git clone https://github.com/vimalamanickam66/Hospital-management-using-Django.git
cd Hospital-management-using-Django
2. Create virtual environment and install dependencies
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
3. Apply migrations and run the server
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
Visit: http://127.0.0.1:8000/

📊 Dashboard Example
Patient Count
Revenue Overview
Daily Appointments
Pie/Bar Charts using Morris.js


🔐 Admin Access
To create a superuser:
python manage.py createsuperuser




