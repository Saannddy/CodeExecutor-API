
# 🖥️ CodeExecutor-API

This project provides a API to run submitted code against predefined test cases. 🧪

## 🛠️ Requirements: 
  `🐳 Docker` `🐳 Docker compose`

## 🚀 Running the API
Build and start the container:

```bash
docker compose up -d --build
```
---
## 🔗 API Endpoint

**POST** `http://127.0.0.1:3000/code/<folder_id>`

Request JSON Format: 

```json
{
  "code": "<your code here>",
  "language": "python"  
}
```
  `📝 Notes: For \t (tab) please sent 4 spacebar instead`

Response JSON Format:

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

**POST** `http://127.0.0.1:3000/run`

Request JSON Format: 

```json
{
  "code": "<your code here>",
  "language": "python"  
}
```
  `📝 Notes: For \t (tab) please sent 4 spacebar instead`

### 📝 Notes

* ⏱️ Default port is `3000` change port as needed in  `docker-compose.yml`.
* ⏱️ The API will be available at `http://127.0.0.1:<port>`
* 📁 Folder IDs correspond to folders under `tests/`.

The test will be further update as database
