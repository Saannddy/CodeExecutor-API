import csv
import json

def convert_riddles_csv_to_json(csv_path, json_path):
    riddles = []
    with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            riddle = {
                'text': row['Riddle Text'],
                'char': row['Character (refer_character)'],
                'index': int(row['Index (refer_index)']),
                'difficulty': row['Difficulty']
            }
            riddles.append(riddle)
    
    with open(json_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(riddles, jsonfile, indent=4, ensure_ascii=False)
    
    print(f"Converted {len(riddles)} riddles to {json_path}")

if __name__ == "__main__":
    csv_path = ""
    json_path = ""
    convert_riddles_csv_to_json(csv_path, json_path)