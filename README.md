# README.md

"""
# Speak Booking Engine

A full-stack booking engine built using Django, designed to handle user registrations,
authentication, and booking management with a clean and scalable architecture.

---

## 🚀 Features

- User Registration & Authentication
- Booking Management System
- Admin Dashboard (Django Admin)
- Static & Media File Handling
- Scalable Django Project Structure
- Ready for Deployment

---

## 🏗️ Project Structure

Speak-main/
│
├── manage.py
├── db.sqlite3
├── Speak/                # Main Django project
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── booking/              # Booking app
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│
├── static/               # Static files
├── staticfiles/          # Collected static files
└── templates/            # Global templates

---

## ⚙️ Setup Instructions

### 1. Clone Repository

git clone https://github.com/sagnik10/speak-booking-engine.git

### 2. Navigate to Project Folder

cd Speak-main

### 3. Create Virtual Environment

python -m venv venv

### 4. Activate Virtual Environment

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate

### 5. Install Dependencies

pip install -r requirements.txt

### 6. Apply Migrations

python manage.py migrate

### 7. Create Superuser

python manage.py createsuperuser

### 8. Run Server

python manage.py runserver

---

## 🌐 Access Application

- Main App: http://127.0.0.1:8000/
- Admin Panel: http://127.0.0.1:8000/admin/

---

## 🧠 Tech Stack

- Backend: Django (Python)
- Database: SQLite (default)
- Frontend: HTML, CSS, JavaScript
- Server: Django Development Server

---

## 📦 Deployment Notes

- Configure ALLOWED_HOSTS in settings.py
- Use PostgreSQL for production
- Run collectstatic before deployment
- Use Gunicorn + Nginx for production server

---

## ⚠️ Important Notes

- Do not commit venv/ or sensitive files
- Always keep SECRET_KEY secure
- Use environment variables in production

---

## 👨‍💻 Author

Developed by Sagnik

---

## 📄 License

This project is open-source and available under the MIT License.

---

## 🔥 Force Push Command (For Reference)

cd C:\Users\nwp\Downloads\Speak-main-1.0.0\Speak-main && git init && git remote remove origin 2>nul & git remote add origin https://github.com/sagnik10/speak-booking-engine.git && git add . && git commit -m "force update" && git branch -M main && git push -u origin main --force

"""
