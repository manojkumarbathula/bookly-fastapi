# 📚 Bookly — Book Management API

A production-oriented **Book Management REST API** built with **FastAPI**, featuring JWT authentication, PostgreSQL, Redis, Celery-based background tasks, email verification, password reset, rate limiting, database migrations, automated testing, and cloud deployment.

## 🚀 Features

* 🔐 JWT Authentication

  * Access & Refresh Tokens
  * Secure password hashing
  * Role-based authorization
* 👤 User Management

  * User registration
  * Email verification
  * Login / Logout
  * Current user profile
  * Password reset
* 📚 Book Management

  * Create, read, update and delete books
  * Book filtering and management
* ⭐ Reviews & Tags

  * Book reviews
  * Book tagging
* ⚡ Rate Limiting

  * Endpoint-level request limiting
  * Protection against excessive requests
* 📧 Email Services

  * Account verification emails
  * Password reset emails
* 🔄 Background Processing

  * Celery task-based email processing
  * Redis as message broker
* 🗄️ PostgreSQL Database

  * Async database operations
  * SQLModel / SQLAlchemy
* 🔧 Database Migrations

  * Alembic migration management
* 🧪 Testing

  * Pytest-based API testing
* ☁️ Deployment

  * Deployed using Render
  * PostgreSQL and Redis configured for the deployed application

## 🛠️ Tech Stack

| Technology            | Purpose                    |
| --------------------- | -------------------------- |
| Python                | Programming Language       |
| FastAPI               | Backend Web Framework      |
| PostgreSQL            | Relational Database        |
| SQLModel / SQLAlchemy | ORM & Database Operations  |
| Alembic               | Database Migrations        |
| Redis                 | Caching / Message Broker   |
| Celery                | Background Task Processing |
| JWT                   | Authentication             |
| Pydantic              | Data Validation            |
| Pytest                | Testing                    |
| Render                | Cloud Deployment           |

## 🏗️ Project Architecture

```text
Client
   │
   ▼
FastAPI Application
   │
   ├── Authentication & Authorization
   │
   ├── Books
   │
   ├── Reviews
   │
   ├── Tags
   │
   ├── Rate Limiting
   │
   └── Email Services
          │
          ▼
       Celery
          │
          ▼
        Redis
          
FastAPI
   │
   ▼
PostgreSQL
```

## 📁 Project Structure

```text
new_framework/
│
├── src/
│   ├── auth/
│   ├── books/
│   ├── reviews/
│   ├── tags/
│   ├── db/
│   ├── config.py
│   ├── celery_tasks.py
│   ├── mail.py
│   ├── rate_limit.py
│   └── __init__.py
│
├── migrations/
│   └── versions/
│
├── tests/
│
├── requirements.txt
├── alembic.ini
├── .env
└── README.md
```

## 🔐 Authentication Flow

```text
User Signup
     │
     ▼
Create User
     │
     ▼
Generate Verification Token
     │
     ▼
Send Verification Email
     │
     ▼
Verify Account
     │
     ▼
Login
     │
     ├── Access Token
     └── Refresh Token
```

The API uses JWT-based authentication to secure protected endpoints.

## 📧 Email Verification

When a user registers:

1. User account is created.
2. A secure verification token is generated.
3. An email containing the verification link is sent.
4. User opens the verification link.
5. The account is marked as verified.

## 🔑 Password Reset

The application provides a secure password reset flow:

```text
Password Reset Request
        │
        ▼
Generate Token
        │
        ▼
Send Reset Email
        │
        ▼
Open Reset Link
        │
        ▼
Set New Password
```

## ⚡ Rate Limiting

Rate limiting is implemented to protect sensitive endpoints from excessive requests.

Examples include:

* Login
* Signup
* Email sending
* Password reset
* Token verification

This helps reduce abuse such as brute-force login attempts and excessive API requests.

## 🗄️ Database

The application uses **PostgreSQL** as the primary relational database.

Database operations are performed asynchronously using SQLModel / SQLAlchemy.

### Database Migration

Alembic is used to manage schema changes.

```bash
alembic upgrade head
```

## 🔄 Background Tasks

Celery is used for background email processing.

```text
FastAPI
   │
   │ Queue Task
   ▼
Redis
   │
   ▼
Celery Worker
   │
   ▼
Email Service
```

This prevents email processing from unnecessarily blocking API requests.

## 🧪 Testing

The project uses **Pytest** for automated testing.

Run tests using:

```bash
pytest
```

## ▶️ Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/manojkumarbathula/bookly-fastapi
cd new_framework
```

### 2. Create virtual environment

```bash
python -m venv venv
```

### 3. Activate virtual environment

Windows:

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file and configure the required database, JWT, Redis and email settings.

### 6. Run database migrations

```bash
alembic upgrade head
```

### 7. Start the FastAPI server

```bash
uvicorn src:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## 📖 API Documentation

FastAPI automatically provides interactive API documentation.

### Swagger UI

```text
/api/docs
```

### ReDoc

```text
/api/redoc
```

## ☁️ Deployment

The application is deployed on **Render**.

Deployment architecture:

```text
GitHub
   │
   ▼
Render Web Service
   │
   ├── FastAPI
   │
   ├── PostgreSQL
   │
   └── Redis
```

Environment variables are configured through the Render dashboard rather than being committed to the repository.

## 🔒 Environment Variables

Example configuration:

```text
DATABASE_URL=
JWT_SECRET=
JWT_ALGORITHM=

REDIS_URL=

MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_SERVER=
MAIL_FROM=
MAIL_FROM_NAME=
```

> Never commit `.env` files or secret credentials to GitHub.

## 🎯 Learning & Engineering Concepts

This project demonstrates practical experience with:

* REST API development
* Async Python
* FastAPI dependency injection
* JWT authentication
* Role-based authorization
* PostgreSQL database design
* ORM-based database operations
* Database migrations
* Redis
* Celery
* Background task processing
* Rate limiting
* Email workflows
* Automated testing
* API documentation
* Cloud deployment
* Environment-based configuration

## 📌 Future Improvements

Possible future improvements include:

* Docker containerization
* CI/CD pipeline
* Advanced caching strategies
* Structured logging
* Monitoring and observability
* API versioning
* Improved test coverage

## 👨‍💻 Author

**Manoj Kumar Bathula**

Backend Developer | Python | FastAPI | PostgreSQL | Redis

---

⭐ If you find this project useful, consider giving the repository a star.
