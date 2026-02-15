import subprocess
import os
import tempfile
from .config import COMPILERS, validate_code

def execute_custom_code(code: str, lang: str) -> dict:
    """Execute raw code without test cases (custom run)."""
    if lang not in COMPILERS:
        return {"status": "error", "stdout": "", "stderr": f"Unsupported language: {lang}"}

    if lang in ["c", "cpp"]:
        return _run_c_cpp(code, lang)
    elif lang == "java":
        return _run_java(code)
    else:
        return _run_interpreted(code, lang)

def execute_code(code: str, lang: str, tests: list, timeout: int = 5, templates: dict = None, rules: dict = None) -> dict:
    """Execute code against a list of test cases with validation and templating."""
    if lang not in COMPILERS:
        return {"status": "error", "message": f"Unsupported language: {lang}"}

    templates = templates or {}
    rules = rules or {}

    if not validate_code(lang, code, rules):
        return {"status": "error", "message": "Code does not meet the prescribed rules."}

    template = templates.get(lang)
    if template and "__CODE_GOES_HERE__" in template:
        code = template.replace("__CODE_GOES_HERE__", code)

    if lang in ["c", "cpp"]:
        return _run_c_cpp(code, lang, tests, timeout)
    elif lang == "java":
        return _run_java(code, tests, timeout)
    else:
        return _run_interpreted(code, lang, tests, timeout)

def _run_c_cpp(code, lang, tests=None, timeout=5):
    """Compile and execute C/C++ code."""
    cfg = COMPILERS[lang]
    fd, src = tempfile.mkstemp(suffix=cfg['extension'])
    os.close(fd)
    exe = src.replace(cfg['extension'], "")
    try:
        with open(src, 'w', encoding='utf-8') as f:
            f.write(code)
        
        comp = subprocess.run([cfg['compiler'], src, "-o", exe], capture_output=True, text=True, timeout=timeout)
        if comp.returncode:
            return {"status": "incorrect", "message": "Compilation failed", "compiler_output": comp.stderr}
        
        if tests is None:
            res = subprocess.run([exe], capture_output=True, text=True, timeout=timeout)
            return {"status": "success", "stdout": res.stdout, "stderr": res.stderr}
            
        return _run_tests([exe], tests, timeout)
    finally:
        for f in [src, exe]:
            if os.path.exists(f): os.remove(f)

def _run_java(code, tests=None, timeout=5):
    """Compile and execute Java code (requires 'public class Main')."""
    cfg = COMPILERS["java"]
    fd, src = tempfile.mkstemp(suffix=".java")
    os.close(fd)
    d = os.path.dirname(src)
    try:
        with open(src, 'w', encoding='utf-8') as f:
            f.write(code)
            
        if not code.strip().startswith("public class Main"):
            return {"status": "error", "message": "Java code must utilize 'public class Main'."}
            
        comp = subprocess.run([cfg['compiler'], src, "-d", d], capture_output=True, text=True, timeout=timeout)
        if comp.returncode:
            return {"status": "incorrect", "message": "Compilation failed", "compiler_output": comp.stderr}
        
        cmd = ["java", "-cp", d, "Main"]
        if tests is None:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return {"status": "success", "stdout": res.stdout, "stderr": res.stderr}
            
        return _run_tests(cmd, tests, timeout)
    finally:
        for f in [src, os.path.join(d, "Main.class")]:
            if os.path.exists(f): os.remove(f)

def _run_interpreted(code, lang, tests=None, timeout=5):
    """Execute interpreted languages (e.g., Python, JavaScript)."""
    cfg = COMPILERS[lang]
    fd, src = tempfile.mkstemp(suffix=cfg['extension'])
    os.close(fd)
    try:
        with open(src, 'w', encoding='utf-8') as f:
            f.write(code)
            
        cmd = [cfg['interpreter'], src]
        if tests is None:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return {"status": "success", "stdout": res.stdout, "stderr": res.stderr}
            
        return _run_tests(cmd, tests, timeout)
    finally:
        if os.path.exists(src): os.remove(src)

def _run_tests(cmd_base, tests, timeout):
    """Batch execute test cases against the generated command."""
    results, status, msg = [], "correct", "All test cases passed!"
    for t in tests:
        try:
            r = subprocess.run(cmd_base, input=t['input'], capture_output=True, text=True, timeout=timeout)
            out, err = r.stdout.strip(), r.stderr.strip()
            s, m = "passed", "Test passed."
            
            if r.returncode or out != t['expected_output'].strip():
                s, m, status, msg = "failed", f"Expected '{t['expected_output'].strip()}', got '{out}'", "incorrect", "Some test cases failed."
                
            results.append({
                "case": int(t['test_number']),
                "status": s,
                "msg": m,
                "stdout": out,
                "stderr": err
            })
        except subprocess.TimeoutExpired:
            results.append({
                "case": int(t['test_number']),
                "status": "failed",
                "msg": f"Timeout {timeout}s",
                "stdout": "",
                "stderr": "Timeout"
            })
            status, msg = "timeout", "Time Limit Exceeded"
            break
            
    return {"status": status, "msg": msg, "tests": results}
