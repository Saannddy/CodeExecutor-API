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
*(You can tweak the `DATABASE_URL` or ports inside `.env` if needed, but defaults work perfectly!)*

### 3️⃣ Build and Launch 🏗️
Run the entire stack (API + PostgreSQL DB) using Docker Compose:
```bash
docker compose up -d --build
```
- `-d`: Runs containers in the background (**detached mode**).
- `--build`: Ensures all recent code changes are freshly compiled.

### 4️⃣ Verify System Health ✅
Once started, you can check if everything is breathing:
- **Container Status**: `docker compose ps` (Look for `Up (healthy)`)
- **API Logs**: `docker compose logs -f code-api`
- **Database Logs**: `docker compose logs -f db`

### 5️⃣ Automatic initialization 🪄
On the very first run, the system will automatically:
- Create all database tables (using UUIDs for safety).
- Seed **7+ coding problems** (Two Sum, Palindrome, etc.).
- Link problems with their respective categories and tags.

---

## 📖 Complete API Documentation
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

## 📝 Usage Best Practices
- 💡 **4 Spaces**: Always use spaces instead of tabs in your JSON `code` strings.
- ⏱️ **Timeouts**: Most problems are capped at 5 seconds for safety.
- 🔒 **Sandboxing**: Code runs in a dedicated non-root container environment.

---

Build with focus on **Modular, Scalable, and Professional** architecture. ✨
