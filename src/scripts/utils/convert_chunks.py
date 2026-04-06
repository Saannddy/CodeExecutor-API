import csv
import json
import re

def convert_chunks_csv_to_json(csv_path, json_path):
    # Descriptive titles for each chunk
    titles = [
        "Internal Subnet Check",
        "Backdoor Account Detection", 
        "URL Protocol Upgrade",
        "Storage Capacity Check",
        "Password Validation"
    ]
    
    # Expectations for each chunk
    expectations = [
        {"input": "192.168.1.1", "output": "true"},
        {"input": "admin", "output": "true"},
        {"input": "http://example.com", "output": "https://example.com"},
        {"input": "1024\n2048", "output": "true"},
        {"input": "password\nusername", "output": "false"}
    ]
    
    chunks = []
    with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            template = row['Template']
            expected = row['Expected Snippet']
            
            # Find the placeholder key
            match = re.search(r'\{\{\{(.+?)\}\}\}', template)
            if not match:
                print(f"Warning: No placeholder found in row {i+1}")
                continue
            key = match.group(1)
            
            chunk = {
                'title': f'LCK-CHUNK-{i+1:03d}: {titles[i]}',
                'difficulty': 'Medium',
                'category': 'Java Basics',
                'templates': [
                    {
                        'lang': 'java',
                        'name': 'Java Implementation',
                        'code': template,
                        'snippets': [
                            [key, expected]
                        ]
                    }
                ],
                'expectation': expectations[i]
            }
            chunks.append(chunk)
    
    with open(json_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(chunks, jsonfile, indent=4, ensure_ascii=False)
    
    print(f"Converted {len(chunks)} chunks to {json_path}")

if __name__ == "__main__":
    csv_path = ""
    json_path = ""
    convert_chunks_csv_to_json(csv_path, json_path)