# EMSPro - Enterprise Employee Management System

A modern, production-ready, full-stack **Employee Management System** built with **Django 5**, **PostgreSQL**, **Bootstrap 5**, and strictly **Function-Based Views (FBVs)**.

---

## 🌟 Key Features

- **100% Function-Based Views (FBVs)**: Built cleanly with `@login_required`, `@role_required`, `@require_POST`, `render`, `redirect`, `get_object_or_404`, and standard Post/Redirect/Get patterns.
- **PostgreSQL Database**: Configured for local development with PostgreSQL and cloud deployment via `DATABASE_URL` / `dj-database-url`.
- **Role-Based Access Control (RBAC)**:
  - **Admin**: Complete system management, user role assignments, Django admin integration.
  - **HR Manager**: Manage workforce directories, department assignments, attendance records, and review/approve leave applications.
  - **Employee**: Self-service portal to mark attendance, apply for leave, track remaining leave balances, and update personal profile details.
  - **Ownership Verification**: View-level security ensuring employees can only view or modify their own records.
- **Workforce Management**:
  - Employee directory with multi-field search (name, ID, email, designation), filters (department, status, employment type), and sorting.
  - Auto-generated employee IDs (`EMP-xxxx`).
  - Table and Grid/Card view toggling.
  - Filtered CSV data export.
  - Soft deactivation (`Terminated`) and permanent deletion.
- **Attendance & Time Tracking**:
  - 1-click Check-In and Check-Out.
  - Automatic status evaluation (on-time vs. late after 09:30 AM, half-day for <4 hours).
  - Monthly attendance calendar view with hours calculation.
- **Leave Management**:
  - Leave requests with overlap prevention and server-side date validation.
  - Annual quota engine: Casual (12), Sick (10), Paid (15), Unpaid (flexible).
  - HR review and approval/rejection with remarks.
- **Interactive Dashboards**:
  - Executive Dashboard with KPI stat cards and Chart.js analytics (Department distribution doughnut, Attendance trend line, Employment type bar chart).
  - Employee workspace with attendance widget, quota badges, and personal history.
- **Production-Ready**:
  - WhiteNoise static file compression and caching.
  - Gunicorn WSGI server.
  - Render blueprint (`render.yaml`), `build.sh`, and `Procfile`.
  - Comprehensive unit test suite.

---

## 💻 Tech Stack

- **Backend**: Python 3.11+, Django 5.1+
- **Database**: PostgreSQL (with SQLite local fallback)
- **Database Driver**: `psycopg` (Psycopg 3) and `psycopg2-binary`
- **Frontend**: Bootstrap 5.3, Bootstrap Icons, Chart.js
- **Static Asset Management**: WhiteNoise
- **WSGI Server**: Gunicorn
- **Deployment**: Render (Free Tier: Web Service + Managed PostgreSQL)

---

## 📁 Project Structure

```text
ems_project/
├── build.sh                  # Render deployment build script
├── Procfile                  # Procfile for web process definition
├── render.yaml               # Render Infrastructure-as-Code blueprint
├── manage.py                 # Django management CLI
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git exclusions (.env, SQLite, staticfiles)
├── README.md                 # Project documentation
├── ems_project/              # Project settings & URL routing
│   ├── settings.py           # Database, WhiteNoise, Security & App config
│   ├── urls.py               # Root URL configuration & error handlers
│   ├── wsgi.py               # WSGI entrypoint
│   └── asgi.py               # ASGI entrypoint
├── core/                     # Reusable utilities, decorators & context processors
│   ├── decorators.py         # @role_required & verify_employee_ownership
│   ├── context_processors.py # Global role_context (user_role, is_admin, etc.)
│   ├── views.py              # Custom 403, 404, 500 handlers
│   ├── tests.py              # Tests for decorators, context processors & handlers
│   └── management/commands/  # seed_data command
├── accounts/                 # Authentication, profile & password management
├── departments/              # Department CRUD & leadership assignments
├── employees/                # Employee directory, cards/table & CSV export
├── attendance/               # 1-click check-in/out & monthly summary calendars
├── leaves/                   # Leave requests, quota calculations & review
├── dashboard/                # Analytics charts & role-aware dashboards
├── templates/                # Modular Bootstrap Django templates
└── static/                   # Static CSS, JS, and branding assets
```

---

## 🛠️ Local Setup Guide

### 1. Prerequisites
- **Python 3.11+** installed on your machine.
- **Git** installed.
- **PostgreSQL 14+** installed and running locally.

### 2. Clone the Repository
```bash
git clone https://github.com/IncurseRed-004/EMSPro.git
cd EMSPro
```

### 3. Create and Activate a Virtual Environment
```bash
# Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS:
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Create PostgreSQL Database Locally
Open your PostgreSQL shell (`psql`) or pgAdmin:
```sql
CREATE DATABASE "EMSproject";
```

Verify that your PostgreSQL service is running on `localhost:5432`.

### 6. Configure Environment Variables
Copy `.env.example` to create your local `.env` file:
```bash
# Windows:
copy .env.example .env

# Linux / macOS:
cp .env.example .env
```

Edit `.env` to match your local PostgreSQL credentials:
```env
SECRET_KEY=your-secret-key-for-local-development
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# PostgreSQL Configuration
DB_ENGINE=postgresql
DB_NAME=EMSproject
DB_USER=postgres
DB_PASSWORD=1234
DB_HOST=localhost
DB_PORT=5432
```

### 7. Run Migrations
Generate and apply all database migrations to PostgreSQL:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 8. Seed Demo Data (Optional)
Populate the database with roles, sample departments, 25 realistic employees, 30 days of attendance history, and sample leave requests:
```bash
python manage.py seed_data
```

**Default Demo Credentials:**
| Role | Username | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | Full system access, all modules |
| **HR Manager** | `hr_user` | `hr123` | Manage employees, departments, attendance, review leaves |
| **Employee** | `emp_user` | `emp123` | Self-service attendance, leave applications, own profile |

To create a new superuser manually:
```bash
python manage.py createsuperuser
```

### 9. Run the Development Server
```bash
python manage.py runserver
```
Visit **http://127.0.0.1:8000** in your browser.

---

## 🧪 Running Automated Tests

Run the full Django test suite against your configured database:
```bash
python manage.py test
```

Run tests for specific applications:
```bash
python manage.py test accounts dashboard employees departments attendance leaves core
```

Run system and deployment checks:
```bash
python manage.py check
python manage.py check --deploy
```

---

## 🚀 Free Deployment Guide (Render)

EMSPro is configured for 1-click blueprint deployment on **[Render](https://render.com/)** using the included `render.yaml`.

### Step 1: Push Repository to GitHub
Ensure all your latest changes are pushed to your GitHub repository:
```bash
git push origin main
```

### Step 2: Create a Blueprint on Render
1. Sign in to your **[Render Dashboard](https://dashboard.render.com/)** (you can sign in with your GitHub account).
2. Click **New +** in the top navigation bar and select **Blueprint**.
3. Connect your GitHub repository: `IncurseRed-004/EMSPro`.
4. Render will detect the `render.yaml` file automatically and define:
   - A free **PostgreSQL Database** (`emspro-db`).
   - A free **Web Service** (`emspro-web`) using Python and Gunicorn.
5. Click **Apply**. Render will:
   - Provision the PostgreSQL database.
   - Run `build.sh` (installs dependencies, runs `collectstatic`, and applies `migrate`).
   - Start the application with Gunicorn.

### Step 3: Populate Initial Data on Production (Optional)
Once deployed, open the **Shell** tab for the web service in your Render dashboard and run:
```bash
python manage.py seed_data
```
Or create an admin superuser:
```bash
python manage.py createsuperuser
```

### Step 4: Verify Deployment URL
Your application will be live at:
`https://<your-service-name>.onrender.com`

---

## ⚠️ Free-Tier Hosting Limitations & Notes

When deploying on Render's free tier, keep in mind:
1. **Web Service Inactivity Sleep**: Free web services spin down after 15 minutes of inactivity. When a new request arrives, it takes approximately 30-50 seconds to spin up ("cold start").
2. **Database Expiration**: Render's free managed PostgreSQL instances expire after **30 days** of creation. For permanent free databases, you can alternatively connect an external free PostgreSQL instance from providers such as **[Neon.tech](https://neon.tech)** or **[Supabase](https://supabase.com)** by setting the `DATABASE_URL` environment variable in the Render Web Service settings.
3. **Ephemeral Media Storage**: Media files uploaded to `/media/` (e.g. avatars) are stored on the local container filesystem and are wiped when the free service restarts. For persistent file uploads in production, configure an S3-compatible cloud storage bucket (e.g., AWS S3 or Cloudflare R2).

---

## 🔒 Security Best Practices

- Never commit the `.env` file or hardcoded credentials to Git.
- Always set `DEBUG=False` in production environments.
- Maintain strong, randomly generated `SECRET_KEY` values in production.
- Use HTTPS and verify that `CSRF_TRUSTED_ORIGINS` matches your public domain.
