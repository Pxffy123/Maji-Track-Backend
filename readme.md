# Maji Track 💧

### Nairobi Water Shortage Monitoring & Reporting System

Maji Track is a web-based platform designed to monitor, report, and visualize water shortages across Nairobi County, Kenya.

The platform divides Nairobi into administrative sub-counties, allowing residents to submit reports about water shortages in their areas. Administrators can review, verify, approve, or reject these submissions, helping provide a clearer picture of the city's water shortage situation.

The system also provides dashboards that organize reported shortages by severity, affected location, and submission status.

---

## 1. Project Objectives

- Provide residents with a platform to report water shortages in their areas.
- Organize water shortage reports by Nairobi's sub-counties.
- Allow administrators to review and verify submitted reports.
- Display approved water shortage reports in an organized dashboard.
- Identify areas experiencing the most critical water shortages.
- Improve access to information about water availability across Nairobi.

## 2. Key Features

### Public Landing Page
- Introduces the Maji Track platform.
- Highlights a critical water shortage report.
- Provides navigation to login and registration pages.

### Resident Dashboard
- Displays water shortage information across Nairobi.
- Allows residents to explore different sub-counties.
- Provides access to reports associated with individual areas.
- Allows residents to submit new water shortage reports.

### Report Submission
Residents can submit reports containing information such as:
- Affected location.
- Nairobi sub-county.
- Severity of the shortage.
- Duration without water.
- Additional descriptions of the situation.

Example:

| Field | Example |
|---|---|
| Location | Umoja 1 |
| Sub-county | Embakasi East |
| Severity | Critical |
| Time without water | 3 weeks |
| Description | Residents have experienced an extended water shortage. |

### Administrator Dashboard
- Displays pending submissions.
- Displays approved reports.
- Allows administrators to approve or reject submissions.
- Provides access to the resident dashboard.

### Water Shortage Monitoring
- Organizes reports by location and sub-county.
- Prioritizes critical shortages.
- Provides dashboard summaries and trends.
- Highlights the most affected areas.

### Authentication
- Resident registration.
- Email verification.
- Login and authentication.
- Token-based authentication using JWT.
- Role-based access for residents and administrators.

---

## 3. Nairobi Sub-counties

Maji Track organizes reports across 17 Nairobi sub-counties:

1. Dagoretti North
2. Dagoretti South
3. Embakasi Central
4. Embakasi East
5. Embakasi North
6. Embakasi South
7. Embakasi West
8. Kamukunji
9. Kasarani
10. Kibra
11. Langata
12. Makadara
13. Mathare
14. Roysambu
15. Ruaraka
16. Starehe
17. Westlands

Each sub-county can contain multiple water shortage reports.

---

## 4. Technology Stack

### Backend
- Python
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Bcrypt
- Flask-JWT-Extended
- Flask-RESTful
- Marshmallow

### Frontend
- React
- JavaScript
- CSS

### Database
- SQLite for local development.
- PostgreSQL for production deployment.

### External Services
- Open-Meteo for weather information.
- Railway for backend hosting.
- Neon for managed PostgreSQL database hosting.

---

## 5. Database Structure

The application uses three primary models.

### User
Stores account information and authentication details.

Fields include:
- ID
- Username
- Email
- Password hash
- Role
- Verification status
- Email verification code hash
- Verification expiration

User roles include `resident` and `admin`.

### District
Stores Nairobi sub-county information.

Fields include:
- ID
- Name

### Report
Stores submitted water shortage reports.

Fields include:
- ID
- User ID
- District ID
- Reviewer ID
- Location
- Severity
- Time without water
- Description
- Status
- Creation timestamp

Report statuses:
- Pending
- Approved
- Rejected
- Resolved

---

## 6. Backend API Structure

The Flask backend exposes the following API route groups:

| Route prefix | Purpose |
|---|---|
| `/api/auth` | Registration, verification, login, refresh and user authentication |
| `/api/admin` | Administrative report management |
| `/api/submissions` | Water shortage report submissions |
| `/api/reports` | Retrieving reports |
| `/api/districts` | Retrieving sub-county information |
| `/api/dashboard` | Dashboard statistics and reporting data |

### Authentication Endpoints

- `POST /api/auth/register`
- `POST /api/auth/verify-email`
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `GET /api/auth/me`

### Administrative Endpoints

- `GET /api/admin/reports/pending`
- `GET /api/admin/reports/approved`
- `PATCH /api/admin/reports/<id>/approve`
- `PATCH /api/admin/reports/<id>/reject`

Admins are created by registering normally, then running
`flask --app app make-admin you@example.com` against the production database.

### Submission Endpoints

- `POST /api/submissions`

### Report Endpoints

- `GET /api/reports`

### District Endpoints

- `GET /api/districts`
- `GET /api/districts/<id>`
- `GET /api/districts/<id>/reports`

### Dashboard Endpoints

- `GET /api/dashboard/summary`
- `GET /api/dashboard/recent-reports`
- `GET /api/dashboard/affected-areas`
- `GET /api/dashboard/trends`
- `GET /api/dashboard/top-affected-areas`

---

## 7. Installation and Setup

### Prerequisites

Make sure you have installed:

- Python 3
- Node.js and npm
- Git

### Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd YOUR_PROJECT_DIRECTORY
```

### Backend Setup

Navigate into the backend directory:

```bash
cd backend
```

Create and activate a virtual environment:

```bash
python -m venv venv
```

Windows:

```powershell
venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Configure the necessary environment variables, including your database connection and JWT secret.

Run the Flask application:

```bash
python app.py
```

The backend will start on the local address and port configured by the application.

### Frontend Setup

Open another terminal and navigate into the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the React development server:

```bash
npm run dev
```

Configure the frontend API base URL to point to the running Flask backend.

---

## 8. Deployment

The production deployment uses:

- **Railway:** Hosting the Flask backend.
- **Neon:** Providing the PostgreSQL database.

The production backend connects to PostgreSQL through the `DATABASE_URL` environment variable.

Sensitive configuration values, including database credentials and JWT secrets, should be stored as environment variables rather than committed to GitHub.

---

## 9. Project Workflow

The general Maji Track reporting process:

1. A resident creates an account and verifies their email.
2. The resident logs into the platform.
3. The resident selects their sub-county and submits a water shortage report.
4. The report enters the system with a `Pending` status.
5. An administrator reviews the submission.
6. The administrator approves or rejects the report.
7. Approved reports become available for public monitoring and dashboard statistics.
8. Reports can subsequently be marked as resolved.

---

## 10. Project Purpose

Access to reliable water is essential for communities, yet water shortages can affect different parts of a city in different ways.

Maji Track aims to make these shortages more visible by providing a centralized reporting and monitoring platform.

By connecting residents, administrators, and location-based reporting, the platform helps organize information about water shortages and identify the areas experiencing the greatest challenges.

**Maji Track — Making Nairobi's Water Shortages Visible.**

---

## 11. Contributors

Developed as a collaborative group project at Moringa School.

