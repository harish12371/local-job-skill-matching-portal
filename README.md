<<<<<<< HEAD
# Local Job & Skill Matching Portal

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.3-green.svg)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org/)
[![MySQL](https://img.shields.io/badge/Database-MySQL-orange.svg)](https://www.mysql.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

An intelligent, commission-free web platform designed to connect daily wage workers with nearby job opportunities and empower local employers to hire reliable workers directly.

> **Core Formula:** `SKILL + LOCATION = BETTER JOB MATCHING`

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Key Objectives](#key-objectives)
3. [Features](#features)
4. [Technology Stack](#technology-stack)
5. [System Architecture](#system-architecture)
6. [Database Schema & Relationships](#database-schema--relationships)
7. [Smart Matching Algorithm](#smart-matching-algorithm)
8. [Installation & Local Execution](#installation--local-execution)
9. [Pre-Seeded Demonstration Accounts](#pre-seeded-demonstration-accounts)
10. [REST API Documentation](#rest-api-documentation)
11. [Vercel Cloud Deployment Guide](#vercel-cloud-deployment-guide)
12. [Automated Test Suite (20 Test Cases)](#automated-test-suite-20-test-cases)

---

## 1. Project Overview

In traditional informal labor markets, millions of daily wage workers assemble at road intersections (*labor chowks*) every morning under harsh weather conditions, facing uncertainty of employment, high travel costs, and exploitation by commission-taking contractors. At the same time, local homeowners and contractors struggle to find skilled technicians (plumbers, electricians, masons, painters) on short notice.

The **Local Job & Skill Matching Portal** resolves this friction by providing a digital, localized marketplace where workers and employers connect directly with 100% transparency, zero middleman cuts, and proximity-based job matching.

---

## 2. Key Objectives

- **Dignified Digital Identity:** Equip informal sector workers with verified online profiles highlighting their vocational skills and wage expectations.
- **Hyper-Local Matching:** Prioritize job openings in the same neighborhood or town (e.g., Bantwal, Mangalore), cutting commute times and transit costs.
- **Direct Employer-to-Worker Contact:** Enable direct phone communication upon job application acceptance.
- **Zero Commission:** Every rupee earned goes directly into the worker's hands.

---

## 3. Features

### For Workers / Job Seekers
- **Quick Registration:** Sign up with name, mobile number, location, trade skills, and expected daily wage.
- **Worker Dashboard:** View profile completion score, personalized job recommendations, and application status.
- **Smart Job Recommendations:** Automatic ranking of active jobs matching worker trade skills, location, and wage fit.
- **One-Click Application:** Apply for jobs with an optional cover note; duplicate applications are prevented.
- **Direct Contact:** Access employer phone number immediately once an application is accepted.

### For Employers / Work Providers
- **Dedicated Employer Dashboard:** View real-time hiring metrics (Total Jobs, Active Openings, Total Applicants, Pending Review).
- **Job Posting & Management:** Post, edit, pause, and delete daily wage openings with custom wages, duration, working hours, and worker counts.
- **Applicant Review:** Inspect applicant trade skills, experience years, and wage expectations.
- **Accept / Reject Workflow:** Instantly accept or decline applicants with live feedback.
- **Direct Calling:** Click-to-call accepted applicants on their mobile numbers.

---

## 4. Technology Stack

- **Frontend:** HTML5, CSS3, JavaScript (Vanilla ES6+), Bootstrap 5.3, Bootstrap Icons
- **Backend:** Python 3.12, Flask 3.1.3, Flask REST API
- **Database ORM:** SQLAlchemy, Flask-SQLAlchemy 3.1, PyMySQL driver
- **Authentication & Security:** Flask-Login, Werkzeug password hashing (PBKDF2/Scrypt), CSRF Protection (Flask-WTF), Role-Based Access Control (RBAC)
- **Deployment:** Vercel (Python Serverless Runtime WSGI), External Cloud MySQL (TiDB / AWS RDS / Aiven / Railway)

---

## 5. System Architecture

```
local-job-skill-matching-portal/
├── api/
│   └── index.py                # Vercel Serverless entrypoint
├── models/
│   ├── __init__.py             # SQLAlchemy db & LoginManager initialization
│   ├── user.py                 # User authentication & role management
│   ├── worker.py               # Worker profile, skills, experience, expected wage
│   ├── employer.py             # Employer company info, contact person, site location
│   ├── job.py                  # Job listings, required skills, wages, duration
│   └── application.py          # Application status (Pending/Accepted/Rejected)
├── routes/
│   ├── __init__.py
│   ├── auth.py                 # Registration & login for workers and employers
│   ├── decorators.py           # Role-based access decorators (@worker_required, @employer_required)
│   ├── main.py                 # Public pages (Home, About, How It Works)
│   ├── worker.py               # Worker dashboard & profile editing
│   ├── employer.py             # Employer dashboard & job applicant management
│   ├── jobs.py                 # Job search, filtering, posting, editing, deletion
│   ├── applications.py         # Job application submission & status updates
│   └── api.py                  # JSON REST API endpoints
├── services/
│   ├── __init__.py
│   └── matching_service.py     # Rule-based skill, location, and wage scoring engine
├── static/
│   ├── css/
│   │   └── style.css           # Custom design system (Professional Blue & Clean Light)
│   └── js/
│       └── main.js             # Form validation, role switching, alert dismissals
├── templates/
│   ├── base.html               # Master layout with responsive navbar & footer
│   ├── index.html              # Homepage with hero, categories, and featured jobs
│   ├── about.html              # Problem statement, solution, and objectives
│   ├── how_it_works.html       # Worker & Employer separate workflow guides
│   ├── login.html              # Authentication sign-in page
│   ├── register.html           # Dual-role registration page
│   ├── worker_dashboard.html   # Worker dashboard with recommendations
│   ├── employer_dashboard.html # Employer dashboard with applicant tracker
│   ├── find_jobs.html          # Search, category, and skill filter interface
│   ├── job_details.html        # Job specification & one-click apply
│   ├── post_job.html           # Job publishing and editing form
│   ├── applications.html       # Full application log view
│   └── errors/                 # 403, 404, 500 error pages
├── scripts/
│   ├── seed_data.py            # Pristine demonstration data seeder
│   └── test_db_connection.py   # Database connectivity diagnostic utility
├── tests/
│   ├── test_portal.py          # Functional test suite
│   └── test_all_20_cases.py    # 20 required project verification test cases
├── app.py                      # Flask Application Factory & WSGI instance
├── config.py                   # Environment configuration & MySQL connection pool
├── vercel.json                 # Vercel deployment configuration
├── .env.example                # Environment variable template
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## 6. Database Schema & Relationships

```
+-----------------------------------------------------------------------------------+
|                                  DATABASE SCHEMA                                  |
+-----------------------------------------------------------------------------------+

       [ users ]
       ├── id (PK, Integer)
       ├── email (Unique, String)
       ├── password_hash (String)
       ├── role ('worker' | 'employer')
       ├── full_name (String)
       ├── phone (String)
       ├── location (String)
       └── address (String)
             │
             ├── (1 : 1) ──> [ worker_profiles ]
             │               ├── id (PK, Integer)
             │               ├── user_id (FK -> users.id)
             │               ├── skills (String, comma-separated)
             │               ├── experience_years (Float)
             │               ├── expected_wage (Float)
             │               ├── availability ('Available' | 'Busy' | 'Unavailable')
             │               └── short_description (Text)
             │                     │
             │                     └── (1 : N) ──┐
             │                                   │
             └── (1 : 1) ──> [ employer_profiles ]│
                             ├── id (PK, Integer) │
                             ├── user_id (FK)    │
                             ├── company_name    │
                             ├── contact_person  │
                             └── work_location   │
                                   │             │
                                   ▼ (1 : N)     ▼ (1 : N)
                               [ jobs ] <─── [ applications ]
                               ├── id (PK)   ├── id (PK)
                               ├── employer_id├── job_id (FK -> jobs.id)
                               ├── title     ├── worker_id (FK -> worker_profiles.id)
                               ├── category  ├── status ('Pending' | 'Accepted' | 'Rejected')
                               ├── wage      ├── cover_note (Text)
                               ├── location  └── applied_at (DateTime)
                               └── skills    * UNIQUE(job_id, worker_id)
```

---

## 7. Smart Matching Algorithm

The matching engine in `services/matching_service.py` evaluates active jobs for any registered worker using a transparent, rule-based formula:

$$\text{Total Score (100%)} = \text{Skill Overlap (50 pts)} + \text{Location Proximity (40 pts)} + \text{Wage Alignment (10 pts)}$$

1. **Skill Overlap (Max 50 points):** Compares worker trade skills against job requirements.
2. **Location Proximity (Max 40 points):** Full 40 points for matching town/city (e.g. Bantwal), 30 points for partial or district-level overlap.
3. **Wage Fit (Max 10 points):** Full 10 points when offered wage meets or exceeds the worker's expected rate.

---

## 8. Installation & Local Execution

### Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- Git

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd Local-Job-Skill-Matching-Portal
```

### Step 2: Create and Activate Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux / macOS:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```
*(If no `DATABASE_URL` is set, the portal automatically initializes a local development SQLite database so you can test immediately.)*

### Step 5: Seed Demonstration Data
```bash
python scripts/seed_data.py
```

### Step 6: Start Local Development Server
```bash
python app.py
```
Open your browser at: `http://localhost:5000`

---

## 9. Pre-Seeded Demonstration Accounts

For instant evaluation, the database comes pre-seeded with realistic demonstration accounts:

| User Type | Name | Email | Password | Location | Trade Skills |
|:---|:---|:---|:---|:---|:---|
| **Worker** | Ramesh Poojary | `worker1@portal.com` | `password123` | Bantwal | Painting, Masonry, Helper |
| **Worker** | Suresh Kumar | `worker2@portal.com` | `password123` | Mangalore | Electrician, Plumber |
| **Worker** | Ravi Naik | `worker3@portal.com` | `password123` | Bantwal | Delivery Worker, Helper |
| **Employer** | Rajesh Shenoy (Coastal Infra) | `employer1@portal.com` | `password123` | Mangalore | Civil & Building Construction |
| **Employer** | Vinay Bhat (Green Valley) | `employer2@portal.com` | `password123` | Bantwal | Agricultural Estates & Masonry |

---

## 10. REST API Documentation

The portal exposes JSON REST API endpoints under `/api`:

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/api/status` | Service health status and current session info |
| `GET` | `/api/jobs` | Retrieve all active jobs (supports `?keyword=`, `?location=`, `?category=`, `?skill=`) |
| `GET` | `/api/jobs/<id>` | Retrieve detailed information for a specific job |
| `GET` | `/api/recommendations` | Ranked job recommendations for authenticated worker |

---

## 11. Vercel Cloud Deployment Guide

The application is pre-configured for Vercel deployment with Python WSGI serverless runtime.

### Step 1: Push Code to GitHub
```bash
git init
git add .
git commit -m "Initial release of Local Job & Skill Matching Portal"
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

### Step 2: Import Project into Vercel
1. Log into your [Vercel Dashboard](https://vercel.com/).
2. Click **Add New** > **Project** and select your GitHub repository.
3. Framework Preset: Leave as **Other**.
4. Root Directory: `./` (leave default).

### Step 3: Configure Environment Variables in Vercel
Under the **Environment Variables** section, add:
- `SECRET_KEY`: A secure random secret string.
- `DATABASE_URL`: Connection URI to your external managed cloud MySQL database (e.g. from TiDB Cloud, Aiven MySQL, AWS RDS, or PlanetScale):
  ```
  mysql+pymysql://<username>:<password>@<cloud-host>:3306/<database-name>?ssl_ca=/etc/ssl/certs/ca-certificates.crt
  ```

### Step 4: Deploy
Click **Deploy**. Vercel will build the application using `vercel.json` and serve it globally with full static asset caching and serverless execution.

---

## 12. Automated Test Suite (20 Test Cases)

To verify all 20 required specifications, run:
```bash
pytest tests/test_all_20_cases.py -v
```

### Verified Test Cases:
1. `test_case_01_worker_registration` - Worker account creation & profile initialization.
2. `test_case_02_employer_registration` - Employer account creation & profile setup.
3. `test_case_03_login_and_logout` - Secure session management.
4. `test_case_04_invalid_login_handling` - Rejection of invalid credentials with user-friendly alerts.
5. `test_case_05_worker_profile_update` - Updating skills, experience, expected wage, and availability.
6. `test_case_06_employer_profile_update` - Updating company info, contact phone, and location.
7. `test_case_07_job_posting` - Publishing new job opening with category, wages, and duration.
8. `test_case_08_job_editing` - Modifying existing job details and scope of work.
9. `test_case_09_job_deletion` - Deleting job postings and dependent records.
10. `test_case_10_job_search` - Keyword matching on title and description.
11. `test_case_11_skill_filtering` - Trade skill filtering.
12. `test_case_12_location_filtering` - Location proximity search.
13. `test_case_13_job_application_flow` - Submitting worker application with cover note.
14. `test_case_14_duplicate_application_prevention` - Database and route-level uniqueness check.
15. `test_case_15_application_acceptance` - Employer marking application as Accepted.
16. `test_case_16_application_rejection` - Employer marking application as Rejected.
17. `test_case_17_role_based_access_restrictions` - Restricting worker pages from employers and vice versa.
18. `test_case_18_mysql_connectivity` - Validating PyMySQL engine dialect registration.
19. `test_case_19_mobile_responsiveness` - Checking responsive viewport and Bootstrap grid constructs.
20. `test_case_20_vercel_production_compatibility` - Validating `vercel.json`, `api/index.py`, and `requirements.txt`.

---

## License
MIT License. Created for the **Local Job & Skill Matching Portal** project.
=======
# local-job-skill-matching-portal
>>>>>>> f19d4f00a297e3535cc561c72125e59812047c08
