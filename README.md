Here’s your README with some tasteful emojis added to make it more visual and friendly:

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

or

```bash
cd API
pip install -r requirements.txt
python app.py
```
---
The API will be available at:

```
http://localhost:3000/<folder_id>
```

## 🔗 API Endpoint

**POST** `/<folder_id>`

Request JSON:

```json
{
  "code": "<your code here>",
  "language": "python"  // or c, cpp, java, javascript
}
```

Response JSON:

```json
{
  "status": "correct|incorrect|error",
  "message": "Summary message",
  "individual_test_results": [
    {
      "test_number": "1",
      "status": "passed|failed",
      "message": "...",
      "stdout": "...",
      "stderr": "...",
      "return_code": 0
    }
  ]
}
```

### 📝 Notes

* ⏱️ Default port is `3000`.
* 📁 Folder IDs correspond to folders under `tests/`.

