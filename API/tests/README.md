# 🧪 Test Case Guidelines

Each question is stored in a folder named with a number, for example: `1`, `2`, `3`.

## 📂 Folder Structure

```
tests/
├── 1/
│   ├── 1.in                # 📝 Input for test case 1
│   ├── 1.out               # ✅ Expected output for test case 1
│   ├── 2.in
│   └── 2.out
├── 2/
│   ├── 1.in
│   ├── 1.out
│   └── config.json         # ⚙️ Optional: timeout, rules, templates
```

---
- **Folder name** = `folder_id` used in the API endpoint.  
- `.in` → Input file.  
- `.out` → Expected output file.  
- Optional **`config.json`** can define:
  - ⏱️ Timeout
  - 🧩 Default code templates
  - 🧮 Validation rules

## 🧾 Example `config.json`

```json
{
  "timeout": 10,
  "templates": {
    "python": "def main():\n    __CODE_GOES_HERE__\n\nif __name__ == '__main__':\n    main()"
  },
  "rules": {
    "python": [
      "\\w+\\s*=\\s*\\[.*\\]",  
      "len\\(\\w+\\)"            
    ]
  }
}
```

## ➕ Adding a New Test Case

1. Create a new folder with the next number.
2. Add `.in` files for inputs.
3. Add `.out` files for expected outputs.
4. Make sure input and output filenames match.
4. Add `config.json` if special rules or timeout are needed.
