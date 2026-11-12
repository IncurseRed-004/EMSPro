# Enterprise Employee Management System (EMS)

A modern, production-ready, full-stack **Employee Management System** built with **Django**, **Bootstrap 5**, and strictly **Function-Based Views (FBVs)**.

---

## 🌟 Key Highlights & Architecture

- **100% Function-Based Views (FBVs)**: All views implemented cleanly with `@login_required`, `@role_required`, `@require_POST`, `render`, `redirect`, `get_object_or_404`, and Post/Redirect/Get patterns.
- **Role-Based Access Control (RBAC)**:
  - **Admin**: Complete system control and configuration.
  - **HR Manager**: Manage workforce directories, department assignments, attendance records, and review/approve leave applications.
  - **Employee**: Self-service portal to mark attendance, apply for leave, track remaining leave balances, and update personal profile details.
  - **Ownership Verification**: Enforced at the view layer. Employees can only access and modify their own records.
- **Enterprise UI/UX**:
  - Bootstrap 5 + Bootstrap Icons + Chart.js.
  - Custom color palette with CSS variables and **Dark Mode** toggle stored in `localStorage`.
  - Directory view toggle: Switch smoothly between **Table View** and **Card/Grid View**.
  - Dynamic Bootstrap confirmation modals for safe deletions and deactivations.
  - Toast alerts via Django's Messages framework.
  - Fully mobile-responsive layouts (optimized for 360px, 768px, and 1280px+).

---

## 🚀 Module Overview

### 1. Accounts & Authentication (`accounts`)
- Custom FBVs for login, logout, profile editing, and password change.
- Multi-role redirection: Admin and HR are routed to the Executive Dashboard; Employees land directly on their personal workspace.
- User profile editing with avatar image upload powered by Pillow.

### 2. Department Management (`departments`)
- Department CRUD with search, sorting, and pagination.
- Aggregated metrics (`annotate(Count('employees'))`).
- Department head assignment linked to active employee records.

### 3. Employee Directory (`employees`)
- Full employee CRUD with auto-generated unique IDs (e.g., `EMP-0001`).
- Multi-field search (name, ID, email, designation) and multi-select filtering (department, status, employment type).
- Sorting by creation date, name, salary, and joining date.
- Dual view: **Table View** with avatar thumbnails and status badges, and **Grid/Card View**.
- **Soft Deactivation** (sets status to `Terminated` and deactivates linked user account) and permanent deletion options.
- Filtered CSV data export (`employees:export_csv`).

### 4. Attendance System (`attendance`)
- One-click daily **Check-In** and **Check-Out** directly from the dashboard.
- Automatic status evaluation (on-time vs. late after 09:30 AM, half-day for <4 hours).
- HR management interface with date, employee, department, and status filters.
- **Monthly Summary Calendar**: Detailed day-by-day logs, total hours worked, and monthly attendance rates.

### 5. Leave Management (`leaves`)
- Leave application form with client and server-side date validation (start date $\le$ end date, overlap detection).
- Annual quota balance engine (`Casual`: 12 days, `Sick`: 10 days, `Paid`: 15 days, `Unpaid`: Flexible).
- HR review interface to approve or reject with manager remarks.
- Employee cancellation of pending requests.

### 6. Interactive Dashboards (`dashboard`)
- **Executive Dashboard** (Admin & HR):
  - 5 key KPI metric cards (Total staff, Active roster, Departments, Pending leaves, Present today).
  - 3 Chart.js data visualizations:
    1. *Department Split* (Doughnut chart)
    2. *Workforce Attendance Trend* (14-day interactive line chart)
    3. *Employment Type Split* (Bar chart)
  - Recent joiners list and pending leave approval widget with quick actions.
- **Employee Workspace**:
  - One-click attendance clock-in widget.
  - Quota balance badges and quick actions.
  - Recent attendance logs and leave application history.

---

## 🛠️ Quickstart Guide

### 1. Prerequisites
- Python 3.11+
- Git

### 2. Setup Virtual Environment
```bash
# Clone or navigate to the project directory
cd ems_project

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(By default, SQLite is pre-configured. To switch to PostgreSQL, set `DB_ENGINE=postgresql` and specify your credentials in `.env`.)*

### 5. Apply Migrations
```bash
python manage.py migrate
```

### 6. Seed Demo Data
Populate the database with roles, sample departments, 25 realistic employees, 30 days of attendance history, and sample leave requests:
```bash
python manage.py seed_data
```

### 7. Run Unit Tests
```bash
python manage.py test
```

### 8. Start the Development Server
```bash
python manage.py runserver
```
Visit **http://127.0.0.1:8000** in your browser.

---

## 🔑 Demo Login Credentials

| Role | Username | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | Full system access, Django admin, all modules |
| **HR Manager** | `hr_user` | `hr123` | Manage employees, departments, attendance, review leaves |
| **Employee** | `emp_user` | `emp123` | Self-service attendance, leave applications, own profile |

---

## 📁 Project Structure

```text
ems_project/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── ems_project/              # Project settings & URL routing
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/                     # Reusable utilities, decorators & handlers
│   ├── decorators.py         # @role_required & ownership verification
│   ├── context_processors.py # Global role & profile template context
│   ├── views.py              # Custom 403, 404, 500 error views
│   └── management/commands/  # seed_data command
├── accounts/                 # Auth, login, profile, password change
├── departments/              # Department CRUD & head assignments
├── employees/                # Employee directory, CSV export, cards/table
├── attendance/               # 1-click check-in/out & monthly summaries
├── leaves/                   # Leave requests, balance tracking & review
├── dashboard/                # Analytics charts & role-based dashboards
├── templates/                # Modular Django templates
│   ├── base.html
│   ├── partials/             # Navbar, sidebar, pagination, messages
│   ├── accounts/
│   ├── departments/
│   ├── employees/
│   ├── attendance/
│   ├── leaves/
│   ├── dashboard/
│   └── errors/               # Custom styled 403, 404, 500 pages
└── static/                   # Static CSS, JS, and branding assets
    ├── css/style.css         # Theme styles & dark mode variables
    ├── js/main.js            # Theme toggle, modals & sidebar scripts
    └── img/                  # SVG logos and avatar fallbacks
```

