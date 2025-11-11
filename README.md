
# 🖥️ CodeExecutor-API

---

This project provides a Flask API to run user-submitted code against predefined test cases. 🧪

## 🛠️ Requirements
- 🐳 Docker & Docker Compose

## 🚀 Running the API
Build and start the container:

```bash
docker compose up --build
```
---
The API will be available at:

```
http://127.0.0.1:3000
```
Change port as needed if port conflict

## 🔗 API Endpoint

**POST** `/<folder_id>`

Request JSON:

```json
{
  "code": "<your code here>",
  "language": "python"  
}
```

Response JSON:

```json
{
  "status": "correct|incorrect|error",
  "msg": "Summary message",
  "tests": [
    {
      "case": 1,
      "status": "passed|failed",
      "msg": "...",
      "stdout": "...",
      "stderr": "..."
    }
  ]
}
```

### 📝 Notes

* ⏱️ Default port is `3000`.
* 📁 Folder IDs correspond to folders under `tests/`.

