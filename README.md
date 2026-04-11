# Training Management System (Flask)

A full-stack training and compliance management platform built with Flask, designed to manage student onboarding, training agreements, progress tracking, and reporting.

---

## 🚀 Features

- Student registration with access codes
- Training agreement creation and lifecycle tracking
- Student dashboard with:
  - Timesheets
  - Learning records
  - Exam tracking
  - Periodic reviews
- Profile management (contact details, department, job title, cohort)
- Live UI updates and validation
- Demo postcode lookup system
- Role-based access (Student, Employer, Admin)

---

## 🧱 Tech Stack

- Python (Flask)
- SQLite
- HTML / CSS / JavaScript
- Jinja2 Templates

---

## 🧠 Key Concepts

- Relational database design with foreign key constraints
- Modular architecture using Flask Blueprints
- Full audit-ready data structure (training, reviews, exams)
- Form validation (client + server side)
- Dynamic UI updates (live summaries, validation feedback)
- Role-based system design

---

## ⚙️ Setup

```bash
git clone https://github.com/yourusername/training-management-system.git
cd training-management-system

python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

pip install -r requirements.txt

python init_db.py
python app.py
```

---

### 6. 🔑 Demo Accounts
```md
## 🔑 Demo Accounts

- Admin: admin@example.com / Admin123!
- Employer: employer@example.com / Employer123!
- Student: student@example.com / Student123!
```
## 📍 Project Status

🚧 In active development

Completed:
- Student registration
- Dashboard
- Profile management
- Training agreements

Next:
- Employer portal
- Admin tools
- Reporting dashboard

 ## 💡 Future Improvements

- Reporting dashboard (Power BI style)
- Notifications system
- File uploads
- API layer
- Production deployment

## 👤 Author

Built by Andy Caladine

- Business Systems Manager
- Web Developer
- Building real-world applications with Flask





