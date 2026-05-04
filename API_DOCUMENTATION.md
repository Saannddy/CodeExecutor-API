# CodeExecutor-API Documentation

Dynamic code execution API supporting multiple languages and database-backed problem management.

## Base URL

`http://localhost:3000`

## Interactive Documentation

Interactive docs are available at: [http://localhost:3000/docs](http://localhost:3000/docs)

---

## Endpoints

### 1. List Problems

Retrieve a summary of all problems in the database. Supports filtering by category or tag.

- **URL**: `/problems`
- **Method**: `GET`
- **Query Parameters**:
  - `category`: Filter by category name (e.g., `/problems?category=Math`)
  - `tag`: Filter by tag name (e.g., `/problems?tag=String`)
- **Response**: `200 OK`

```json
{
  "status": "success",
  "data": [
    { "id": "uuid", "title": "Two Sum", "difficulty": "easy" }
  ]
}
```

### 2. Get Problem Details

Retrieve specific problem metadata, configuration, and public test cases.

- **URL**: `/problem/<problem_id>`
- **Method**: `GET`
- **Response**: `200 OK`

### 3. Execute Code (Problem-based)

Run code against test cases associated with a specific problem.

- **URL**: `/code/<problem_id>`
- **Method**: `POST`
- **Body**:

```json
{
  "language": "python",
  "code": "print('hello')"
}
```

### 4. Custom Execution

Run arbitrary code without a pre-defined problem.

- **URL**: `/run?lang=python`
- **Method**: `POST`
- **Body**:

```json
{
  "code": "print('hello world')"
}
```

### 5. Cheat Flip

Toggle cheat mode on/off. When enabled, all code execution will return "passed" for all test cases.

- **URL**: `/cheat-flip`
- **Method**: `POST`
- **Body**:

```json
{
  "cheat-code": "your-raw-secret-passphrase"
}
```

- **Notes**:
  - The secret is validated using a constant-time SHA-256 comparison.
  - The state is held in-memory and resets on server restart.

---

## Supported Languages

- **Python**: `python`
- **JavaScript**: `javascript`
- **Java**: `java`
- **C**: `c`
- **C++**: `cpp`
