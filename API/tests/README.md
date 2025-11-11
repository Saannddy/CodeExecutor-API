# 🧪 Test Case Guidelines

Each question is stored in a folder named with a number, for example: 1, 2, 3

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
│   └── config.json         # ⏱️ specific timeout
```

- The **folder name** is the `folder_id` used in the API endpoint.
- **Test files** are numbered sequentially as `.in` for input and `.out` for expected output.
- Optionally, you can add a `config.json` file to specify a timeout ⏱️, default code and rules:

Example `config.json`:

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

1. Create a new folder with the next number (n+1) 🔢.
2. Add `.in` files for inputs 📝 and `.out` files for expected outputs ✅.
3. Make sure the numbers match across `.in` and `.out` files 🔗.
4. Add `config.json` if you want to override the default timeout (default is 5 seconds) ⏱️.
