import pandas as pd
import json
import os
import re

def process_excel():
    xl = pd.ExcelFile('Level 4 Puzzles.xlsx')
    chunks = []
    problems = []

    for name in xl.sheet_names:
        df = xl.parse(name)
        # Extract Px from L4_Px
        match_p = re.search(r'L4_(P\d+)', name)
        category_id = f"ELV-{match_p.group(1)}" if match_p else "Elevator Hall"

        if '(Chunk)' in name:
            for i, row in df.iterrows():
                template_code = str(row.get('Problem', row.get('Template', '')))
                snippet_block = str(row.get('Expected Input', row.get('Expected Snippet', '')))
                
                placeholders = re.findall(r'\{TASK\s*(\d+):[^\}]+\}', template_code)
                s_dict = {}
                
                new_template = template_code
                for p_num in placeholders:
                    placeholder_search = re.search(rf'\{{TASK\s*{p_num}:[^\}}]+\}}', new_template)
                    if placeholder_search:
                        placeholder_str = placeholder_search.group(0)
                        new_template = new_template.replace(placeholder_str, f'{{{{{{snippet_{p_num}}}}}}}')
                    
                    pattern = rf'TASK\s*{p_num}\s*\([^\)]+\):\s*(.*?)(?=TASK\s*\d+\s*\(|$)'
                    match = re.search(pattern, snippet_block, re.DOTALL)
                    if match:
                        s_dict[f"snippet_{p_num}"] = match.group(1).strip()
                    else:
                        s_dict[f"snippet_{p_num}"] = f"// Missing snippet for Task {p_num}"

                chunk_data = {
                    "title": f"{category_id}-CHUNK-{i+1:03d}",
                    "difficulty": str(row.get('Difficulty', "Medium")),
                    "category": category_id,
                    "templates": {
                        "java": {
                            "name": "Java Implementation",
                            "template_code": new_template,
                            "snippets": s_dict
                        }
                    },
                    "expectation": {
                        "input": str(row.get('Input', '')),
                        "output": str(row.get('Expected Output', ''))
                    }
                }
                chunks.append(chunk_data)
        elif '(Problem)' in name:
            for i, row in df.iterrows():
                template_code = str(row.get('Problem', row.get('Template', '')))
                expected_output = str(row.get('Expected Output', ''))
                
                outputs = [o.strip() for o in expected_output.split('\n') if o.strip()]
                
                method_match = re.search(r'public\s+static\s+(?:\w+(?:\[\])?)\s+(\w+)\(', template_code)
                method_name = method_match.group(1) if method_match else ""
                
                inputs = []
                if method_name:
                    # Look only inside the main method
                    main_match = re.search(r'public\s+static\s+void\s+main\s*\(.*?\)\s*\{(.*?)\}', template_code, re.DOTALL)
                    if main_match:
                        main_content = main_match.group(1)
                        # Look for calls: method_name(...)
                        # We want the arguments between the first "(" and last ")" for this call
                        matches = re.finditer(rf'{method_name}\((.*?)\)', main_content)
                        for m in matches:
                            inputs.append(m.group(1))
                
                test_cases = []
                # Use whichever count is larger, but match them up
                count = max(len(inputs), len(outputs))
                for j in range(count):
                    inp = inputs[j] if j < len(inputs) else ""
                    out = outputs[j] if j < len(outputs) else ""
                    test_cases.append({
                        "input": inp,
                        "output": out,
                        "is_hidden": j > 0
                    })

                problem_data = {
                    "title": f"{category_id}-PROB-{i+1:03d}",
                    "description": template_code,
                    "difficulty": str(row.get('Difficulty', "Hard")),
                    "category": category_id,
                    "templates": {
                        "java": template_code
                    },
                    "test_cases": test_cases
                }
                problems.append(problem_data)

    out_dir = 'src/scripts/data/java/elevatorhall'
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, 'chunks.json'), 'w') as f:
        json.dump(chunks, f, indent=4)
    
    with open(os.path.join(out_dir, 'problems.json'), 'w') as f:
        json.dump(problems, f, indent=4)

    print(f"Processed {len(chunks)} chunks and {len(problems)} problems with category mapping.")

if __name__ == "__main__":
    process_excel()
