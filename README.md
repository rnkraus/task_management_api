# Task Management API

RESTful API for managing tasks with user assignment.

Built with FastAPI, PostgreSQL, and SQLAlchemy.
Goal: A practical backend project with clean architecture.

---

## Features

- RESTful API design
- Full CRUD for Users and Tasks

### Users
- `POST /users`
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

### Additional Features
- Task ↔ User Relation (Foreign Key)
- Validation with Pydantic
- Error Handling (400 / 404 / 422)
- PostgreSQL as the database
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

#### .env (for Docker):

```env
POSTGRES_DB=taskdb
POSTGRES_USER=taskuser
POSTGRES_PASSWORD=your_password_here
DATABASE_URL=postgresql://taskuser:your_password_here@db:5432/taskdb
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

## Tests

```bash
pytest
```

---

## Architecture

- `api/` → HTTP Layer (FastAPI endpoints)
- `services/` → Business logic
- `models/` → Database models (SQLAlchemy)
- `schemas/` → Request/Response models (Pydantic)
- `core/` → Configuration & DB setup

---

## Database

- PostgreSQL via Docker
- Migrations with Alembic
- Separate test database (taskdb_test)
- Test DB is automatically created during container initialization

---

## Behavior

- Users cannot be deleted if tasks exist
- Duplicate email addresses are prevented
- Tasks require a valid `user_id`
- PATCH requests must include at least one field
- Task titles cannot be empty
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