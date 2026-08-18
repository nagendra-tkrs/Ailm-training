# Employee Leave Management System - Backend

A secure REST API built with FastAPI for managing employee leave requests, approvals, and balances.

## Features

- JWT authentication with role-based authorization (Employee / Admin)
- Leave request CRUD (apply, edit, delete, approve, reject)
- Leave balance tracking (Casual, Sick, Earned)
- Employee profile management
- Admin dashboard with statistics
- Global exception handling and structured error responses
- Comprehensive input validation
- MySQL database with SQLAlchemy ORM

## Tech Stack

- **Framework:** FastAPI
- **Database:** MySQL (via SQLAlchemy + PyMySQL)
- **Auth:** JWT (python-jose) + Argon2 password hashing
- **Validation:** Pydantic v2

## Setup Instructions

### Prerequisites

- Python 3.10+
- MySQL 8.0+
- pip

### 1. Clone the repository

```bash
git clone https://github.com/nagendra-tkrs/Ailm-training.git
cd Ailm-training/backend
```

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the `backend/` directory:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=leave_management

JWT_SECRET_KEY=your_random_256_bit_secret_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Generate a secure JWT secret:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Setup MySQL database

```sql
CREATE DATABASE leave_management;
```

Tables are created automatically on server startup. Seed data (admin + demo employee) is inserted on first run.

### 6. Start the server

```bash
python -m uvicorn app.main:app --reload --port 5000
```

## Seed Users

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@gmail.com | Admin@123 |
| Employee | employee@gmail.com | Employee@123 |

## API Documentation

Swagger UI: http://localhost:5000/docs
ReDoc: http://localhost:5000/redoc

## API Endpoints

### Public (No Auth)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new employee |
| POST | `/api/auth/login` | Login and get JWT token |
| GET | `/` | Backend status |
| GET | `/health` | Health check |
| GET | `/db-test` | Database connectivity check |

### Employee (Bearer Token Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/me` | Get current user info |
| GET | `/api/employee/dashboard` | Dashboard with leave balance |
| POST | `/api/leave` | Apply for leave |
| GET | `/api/leave/my` | List own leaves |
| DELETE | `/api/leave/{id}` | Delete pending leave |
| POST | `/api/leaves` | Create leave (CRUD) |
| GET | `/api/leaves` | List own leaves (CRUD) |
| PUT | `/api/leaves/{id}` | Update leave |
| DELETE | `/api/leaves/{id}` | Delete leave |
| GET | `/api/profile` | Get profile |
| PUT | `/api/profile` | Update profile |
| PUT | `/api/profile/password` | Change password |
| GET | `/api/users/profile` | Get user profile with balances |

### Admin (Bearer Token + Admin Role Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/dashboard` | Admin dashboard stats |
| GET | `/api/leave/all` | List all leaves (with status filter) |
| PUT | `/api/leave/{id}/approve` | Approve leave |
| PUT | `/api/leave/{id}/reject` | Reject leave |
| GET | `/api/users` | List all users |
| GET | `/api/users/{id}` | Get user detail |

## Authentication

1. Login via `POST /api/auth/login` with email and password
2. Receive `access_token` in response
3. Include in all subsequent requests: `Authorization: Bearer <token>`

Token expires after 60 minutes (configurable via `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`).

## Error Responses

All errors return structured JSON:

```json
{
  "detail": "Error message"
}
```

Validation errors include field-level details:

```json
{
  "detail": "Validation error",
  "errors": [
    {"field": "body -> email", "message": "Only @gmail.com email addresses are allowed"}
  ]
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (validation/business rule) |
| 401 | Unauthorized (missing/invalid/expired token) |
| 403 | Forbidden (insufficient role) |
| 404 | Not found |
| 409 | Conflict (duplicate email) |
| 422 | Validation error (schema) |
| 500 | Internal server error |
| 503 | Service unavailable (DB down) |

## Security Features

- JWT with expiration, issued-at, and unique token ID claims
- Argon2 password hashing (OWASP-recommended)
- Role-based access control (Employee / Admin)
- User existence verification on every authenticated request
- Input validation on all endpoints
- Global exception handlers (no stack traces in production)
- SQL injection protection via SQLAlchemy ORM
- CORS restricted to localhost origins
- Environment variable-based configuration (no hardcoded secrets)

## Database Schema

- **users** - id, employee_id, name, email, password, role, created_date
- **leaves** - id, user_id, employee_id, leave_type, start_date, end_date, days, reason, status, created_date, updated_at
- **leave_balances** - id, user_id, leave_type, total_days, used_days
- **employee_profiles** - id, user_id, name, email, role, address, phone_number

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_HOST` | No | localhost | MySQL host |
| `DB_PORT` | No | 3306 | MySQL port |
| `DB_USER` | No | root | MySQL username |
| `DB_PASSWORD` | Yes | - | MySQL password |
| `DB_NAME` | No | leave_management | Database name |
| `JWT_SECRET_KEY` | Yes | - | Secret key for JWT signing |
| `JWT_ALGORITHM` | No | HS256 | JWT signing algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | No | 60 | Token expiration in minutes |
| `LOG_LEVEL` | No | INFO | Logging level |
