# 🖥️ CodeExecutor-API

A professional, layered-architecture API for dynamic code execution. This project allows you to run code in multiple languages against database-backed problems and test cases. 🚀🧪

---

## 🛠️ Prerequisites

Before embarking on this journey, ensure your machine is equipped with:

- 🐳 **Docker**: [Install Docker](https://docs.docker.com/get-docker/)
- 🐳 **Docker Compose**: [Install Docker Compose](https://docs.docker.com/compose/install/)

---

## 🚀 Step-by-Step Setup Guide

Follow these steps to get your own instance of **CodeExecutor-API** up and running in minutes!

### 1️⃣ Clone the Repository

Open your terminal and clone this project:

```bash
git clone https://github.com/Saannddy/CodeExecutor-API
cd CodeExecutor-API
```

### 2️⃣ Configure Environment ⚙️

The project uses a `.env` file for configuration. Copy the example to get started:

```bash
cp .env.example .env
```

_(You can tweak the `DATABASE_URL` or ports inside `.env` if needed, but defaults work perfectly!)_

### 3️⃣ Build and Launch 🏗️

Run the entire stack (API + PostgreSQL DB) using Docker Compose:

```bash
## FOR LOCAL DB
docker compose --profile local up -d --build
## FOR PRODUCTION
docker compose --profile remote up -d --build

## FOR REBUILD WHILE DOCKER STILL RUNNING
docker compose --profile local up -d --build --force-recreate
```

- `-d`: Runs containers in the background (**detached mode**).
- `--build`: Ensures all recent code changes are freshly compiled.

### 5️⃣ Automatic Initialization 🪄

On the very first run, the system will automatically:

- Create all database tables (using UUIDs for safety).
- Seed **7+ coding problems** (Two Sum, Palindrome, etc.).
- Link problems with their respective categories and tags.

---

## 🏗️ Database Management

While the system handles initialization automatically, you may need these manual commands for development:

### 🔄 Migrations (Alembic)

If you modify the models in `src/models/`, use these commands to sync the database:

- **Check Status**: `docker compose --profile local exec code-api alembic current`
- **Apply Migrations**: `docker compose --profile local exec code-api alembic upgrade head`
- **Generate New Migration**:
  ```bash
  docker compose --profile local exec code-api alembic revision --autogenerate -m "description_of_change"
  ```

### 🌐 Cloud Database Migration (NeonDB)

If you want to connect to **NeonDB** online and migrate it to the latest version:

1. **Get Connection String**: Copy your connection string from the [Neon Console](https://console.neon.tech/) (ensure `?sslmode=require` is included).
2. **Apply Migrations**:
   Run the following command, replacing `YOUR_NEON_URL` with your actual connection string:
   ```bash
   docker compose --profile local exec -e DATABASE_URL="YOUR_NEON_URL" local-code-api alembic upgrade head
   ```
3. **(Optional) Seed Data**:
   If your Neon database is empty, you can seed it with the default problems:
   ```bash
   docker compose --profile local exec -e DATABASE_URL="YOUR_NEON_URL" local-code-api python3 -m scripts.seed
   ```

_(Alternatively, you can simply update the `DATABASE_URL` in your `.env` file and run the standard migration commands.)_

### 🌱 Data Seeding

If you need to re-seed or reset the initial data:

- **Run Seeder**: `docker compose --profile local exec local-code-api python3 -m scripts.seed`
  _(The seeder is idempotent and will skip problems that already exist!)_

---

## ️ Recommended Tooling

For the most professional development experience, we recommend the following tools:

- ⚡ **[OrbStack](https://orbstack.dev/)**: A fast, light, and easy way to run Docker containers on macOS.
- 🐝 **[Beekeeper Studio](https://www.beekeeperstudio.io/)**: A smooth and easy-to-use SQL editor and database manager for PostgreSQL.
- 🐶 **[Bruno](https://www.usebruno.com/)**: A fast and git-friendly API client for testing the CodeExecutor endpoints.

---

## �📖 Complete API Documentation

Since you're up and running, you'll want to know how to talk to the API!

- **Detailed Endpoints**: See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for full request/response examples.
- **Interactive Swagger/Scalar Docs**: Visit [http://localhost:3000/docs](http://localhost:3000/docs) while the app is running.
- **OpenAPI Spec**: Available at `http://localhost:3000/openapi.yaml`.

---

## � Testing with Bruno

For the best developer experience, we've included a **Bruno Collection**:

1. Open **Bruno**.
2. Import the folder located at `./bruno`.
3. Start firing requests!

---

## 🧪 Supported Languages

- 🐍 **Python** (`python`)
- 🟨 **JavaScript** (`javascript`)
- ☕ **Java** (`java`)
- 🟦 **C** (`c`)
- 🟥 **C++** (`cpp`)

---

## 🧪 Testing

Tests are organized by feature group in the `tests/` directory:

```
tests/
├── conftest.py           # Shared fixtures (Flask client, DB mocks)
├── problem/              # Problem endpoint tests
│   └── test_problem_handler.py
├── question/             # Question endpoint tests
├── riddle/               # Riddle endpoint tests
├── execution/            # Code execution tests
└── docs/                 # Documentation endpoint tests
```

### Run All Tests

```bash
python3 -m pytest
```

### Coverage Report

After running tests, open the interactive HTML coverage report:

```bash
open coverage_html/index.html
```

The report highlights **exactly which lines** were hit or missed during testing — click any file to see line-by-line coverage.

### Run a Specific Test Group

```bash
python3 -m pytest tests/problem/       # Problem tests only
python3 -m pytest tests/riddle/        # Riddle tests only
```

> **Note**: Tests mock the database layer so they run locally without Postgres. Install test dependencies first: `pip install pytest pytest-cov`

---

## 📝 Usage Best Practices

- 💡 **4 Spaces**: Always use spaces instead of tabs in your JSON `code` strings.
- ⏱️ **Timeouts**: Most problems are capped at 5 seconds for safety.
- 🔒 **Sandboxing**: Code runs in a dedicated non-root container environment.

---

Build with focus on **Modular, Scalable, and Professional** architecture. ✨
