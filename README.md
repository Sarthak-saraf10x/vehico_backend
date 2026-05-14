<div align="center">
  <h1>VEHICO Backend (Vehicle Insurance Management System)</h1>
  <p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
    <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  </p>
  <p>The core REST API and database interactions for the VEHICO Platform.</p>
</div>

---

> [!NOTE]
> This is the backend API for the VEHICO application. It serves as the bridge between the frontend application and the PostgreSQL database, handling authentication, business logic, and data persistence for vehicle insurance and claims.

## Project Working

<details>
<summary><b>View Backend Workflow</b></summary>
<br/>

The VEHICO backend uses a Flask-based REST architecture to handle all insurance operations. Here is how the system works:

1. **Authentication:** Users (Customers, Claim Officers, Inspection Guides) log in via standard credentials or Google OAuth. The backend issues tokens/sessions to maintain secure states.
2. **Policy Management:** The system handles creation, retrieval, and purchasing of vehicle insurance policies. When a customer purchases a policy, it is recorded in the database and linked to their profile.
3. **Claim Processing:** When a vehicle accident or incident occurs, customers submit claims. The backend processes these claims, stores uploaded damage evidence (images/documents) in the `uploads/` directory, and schedules an inspection.
4. **Inspection and Approval:** Inspection Guides retrieve claim data, perform checks, and submit reports. Claim Officers then hit the approval/rejection endpoints based on these reports, updating the final status of the claim.
</details>

## How to Start

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

### 4. Database Setup
Ensure you have created the database specified in your `.env` file. You should import any provided database backup SQL file to set up the tables and initial mock data.

### 5. Run the Server
```bash
python app.py
```
> [!TIP]
> The server will start in debug mode on `http://localhost:5000` by default.
</details>

## Directory Structure

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

## API Endpoints Reference

<details>
<summary><b>View Key API Routes</b></summary>
<br/>

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/users/login` | `POST` | Authenticate user |
| `/api/users/google-login` | `POST` | OAuth login via Google |
| `/api/policies/` | `GET` | Fetch all available vehicle policies |
| `/api/policies/<id>/purchase` | `POST` | Purchase a vehicle policy |
| `/api/claims/` | `POST` | Submit a new vehicle accident claim |
| `/api/claims/<id>/documents` | `POST` | Upload vehicle damage photos |
| `/api/claims/<id>/approve` | `POST` | Officer approval of the claim |

> [!IMPORTANT]
> All API routes are protected by CORS. Ensure your frontend is running on `http://localhost:5173`.
</details>
