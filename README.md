<div align="center">
  <h1>🛡️ ICMS Backend (Insurance Claim Management System)</h1>
  <p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
    <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  </p>
  <p>The core REST API and database interactions for the ICMS Platform.</p>
</div>

---

> [!NOTE]
> This is the backend API for the ICMS application. It serves as the bridge between the frontend application and the PostgreSQL database, handling authentication, business logic, and data persistence.

## 🚀 Quick Start

<details>
<summary><b>Click to expand Setup Instructions</b></summary>
<br/>

### 1. Prerequisites
- Python 3.8+
- PostgreSQL database

### 2. Installation
Navigate to the backend directory and set up a virtual environment:

```bash
cd icms_backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root of the backend folder:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
```

### 4. Run the Server
```bash
python app.py
```
> [!TIP]
> The server will start in debug mode on `http://localhost:5000` by default.
</details>

## 📂 Directory Structure

<details>
<summary><b>View Backend Architecture</b></summary>
<br/>

```text
icms_backend/
├── app.py                # Main application entry point & route registration
├── controllers/          # Route handlers (User, Policy, Claim)
├── models/               # Database schemas and data models
├── services/             # Core business logic
├── middleware/           # Request interceptors & authentication
├── commons/              # Utility functions and shared helpers
├── uploads/              # Storage for uploaded claim documents
├── requirements.txt      # Python dependencies
└── .env                  # Environment configuration
```
</details>

## 🔌 API Endpoints Reference

<details>
<summary><b>View Key API Routes</b></summary>
<br/>

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/users/login` | `POST` | Authenticate user & get token |
| `/api/users/google-login` | `POST` | OAuth login via Google |
| `/api/policies/` | `GET` | Fetch all available policies |
| `/api/policies/<id>/purchase` | `POST` | Purchase a policy |
| `/api/claims/` | `POST` | Submit a new insurance claim |
| `/api/claims/<id>/documents` | `POST` | Upload damage photos/files |
| `/api/claims/<id>/approve` | `POST` | Officer approval of claim |

> [!IMPORTANT]
> All API routes are protected by CORS. Ensure your frontend is running on `http://localhost:5173`.
</details>

## 🗄️ Database

> [!TIP]
> Ensure you import the `db_backup.sql` provided in the root repository before running the server to set up tables and initial mock data.
