# Task Management API

RESTful API for managing tasks with authentication, role-based access control, and advanced querying.

Built with FastAPI, PostgreSQL, and SQLAlchemy.
Goal: A production-like backend project with clean architecture and real-world features.

---

## Features

- RESTful API design
- JWT authentication
- Role-based access control
- Full CRUD for tasks
- User self-service endpoints
- Admin user management endpoints
- Filtering, pagination, sorting, and search
- PostgreSQL + SQLAlchemy + Alembic
- Tests with pytest
- Docker-based setup

### Users

#### Self (Authenticated User)
- `GET /users/me`
- `PUT /users/me`
- `PATCH /users/me`
- `DELETE /users/me`

#### Admin Only
- `GET /users`
- `GET /users/{id}`
- `PUT /users/{id}`
- `PATCH /users/{id}`
- `DELETE /users/{id}`

### Tasks
- `POST /tasks`
- `GET /tasks`
- `GET /tasks/{id}`
- `PUT /tasks/{id}`
- `PATCH /tasks/{id}`
- `DELETE /tasks/{id}`

### Advanced Querying
- Filtering (`completed=true/false`)
- Pagination (`limit`, `offset`)
- Sorting (`sort_by`, `order`)
- Search (`search` in title/description)

### Additional Features
- Task ↔ User Relation (Foreign Key)
- Validation with Pydantic
- Error Handling (400 / 401 / 403 / 404 / 422)
- PostgreSQL database
- SQLAlchemy ORM
- Alembic Migrations
- Tests with pytest
- Docker-based Setup

---

## Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- pytest
- Docker

---

## Setup

### 1. Clone Repository

```bash
git clone https://github.com/rnkraus/task_management_api.git
cd task_management_api
```

### 2. Python Environment (for Tests & Alembic)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
```

### 3. Create Environment Files

Generate a secure key for JWT authentication:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Create the following three `.env` files and replace the placeholder values with your own:

- choose a secure password for the database
- insert your generated `SECRET_KEY`

#### .env (PostgreSQL in Docker + JWT authentication)

```env
POSTGRES_DB=taskdb
POSTGRES_USER=taskuser
POSTGRES_PASSWORD=your_password_here
DATABASE_URL=postgresql://taskuser:your_password_here@db:5432/taskdb

SECRET_KEY=your_secret_key_here
```

#### .env.local (for local tools like Alembic):

```env
DATABASE_URL=postgresql://taskuser:your_password_here@localhost:5432/taskdb
```

#### .env.test (for pytest):

```env
DATABASE_URL=postgresql://taskuser:your_password_here@localhost:5432/taskdb_test
```

### 4. Start Docker (Development Mode)

```bash
docker compose -f compose.yaml -f compose.dev.yaml up --build
```

### 5. Run Migrations

```bash
alembic upgrade head
```

---

## Authentication

### Register

    `POST /auth/register`

### Login

    `POST /auth/login`

### Using the Access Token

After login, include the token in the request header:

    Authorization: Bearer <access_token>

Required for all protected endpoints (e.g. `/tasks`, `/users/me`)

In Swagger UI, you can use the "Authorize" button to log in and automatically include the token.

---

## API Docs (Swagger)

After starting the server, open:

    http://localhost:8000/docs

Swagger UI provides interactive API documentation.

Steps:
1. Register a user (`/auth/register`)
2. Click "Authorize" and log in
3. Use protected endpoints (e.g. `/tasks`)

## Admin

Promote a user to admin:

    python -m scripts.make_admin user@example.com

---

## Tests

```bash
pytest
```

---

## Architecture

```
project/
├── app/
│ ├── api/ # HTTP layer (FastAPI endpoints)
│ ├── services/ # Business logic
│ ├── models/ # Database models (SQLAlchemy)
│ ├── schemas/ # Request/Response models (Pydantic)
│ └── core/ # Config, security, database setup
│
├── scripts/ # Utility scripts (e.g. make_admin)
├── tests/ # Test suite
```
---

## Database

- PostgreSQL via Docker
- Migrations with Alembic
- Separate test database (taskdb_test)
- Test DB is automatically created during container initialization

---

## Behavior

- Users can only access their own tasks
- Admins can manage all users
- Users cannot be deleted if tasks exist
- Duplicate email addresses are prevented
- Task titles cannot be empty
- PATCH requests must include at least one field
- PUT replaces an object completely, PATCH performs a partial update

---

## Docker

### Standard:

```bash
docker compose up --build
```

### Development (Hot Reload)

```bash
docker compose -f compose.yaml -f compose.dev.yaml up --build
```