import subprocess, os, tempfile
from config import COMPILERS, loadTest, validate_code

def execute_code(code: str, lang: str, qid: str) -> dict:
    """Execute the given code in the specified language against test cases for the question ID."""
    if lang not in COMPILERS:
        return {"status": "error", "message": f"Unsupported language: {lang}"}

    try:
        data = loadTest(qid)
        tests, timeout = data['test_pairs'], data['timeout']
        templates = data.get('templates', {})
        rules = data.get('rules', {})
    except Exception as e:
        return {"status": "error", "message": f"Error loading test cases: {e}"}

    if not validate_code(lang, code, rules):
        return {"status": "error", "message": "Code does not meet the required rules."}

    template = templates.get(lang)
    if template and "__CODE_GOES_HERE__" in template:
        code = template.replace("__CODE_GOES_HERE__", code)

    if lang in ["c", "cpp"]:
        return _run_c_cpp(code, lang, tests, timeout)
    elif lang == "java":
        return _run_java(code, tests, timeout)
    else:
        return _run_interpreted(code, lang, tests, timeout)


def _run_c_cpp(code, lang, tests, timeout):
    """Compile and run C/C++ code."""
    cfg = COMPILERS[lang]
    fd, src = tempfile.mkstemp(suffix=cfg['extension'])
    os.close(fd)
    exe = src.replace(cfg['extension'], "")
    try:
        open(src, 'w', encoding='utf-8').write(code)
        comp = subprocess.run([cfg['compiler'], src, "-o", exe], capture_output=True, text=True, timeout=timeout)
        if comp.returncode:
            return {"status": "incorrect", "message": "Compilation failed", "compiler_output": comp.stderr}
        return _run_tests([exe], tests, timeout)
    finally:
        for f in [src, exe]:
            if os.path.exists(f): os.remove(f)


def _run_java(code, tests, timeout):
    """Compile and run Java code."""
    cfg = COMPILERS["java"]
    fd, src = tempfile.mkstemp(suffix=".java")
    os.close(fd)
    d = os.path.dirname(src)
    try:
        open(src, 'w', encoding='utf-8').write(code)
        if not code.strip().startswith("public class Main"):
            return {"status": "error", "message": "Java code must use 'public class Main'."}
        comp = subprocess.run([cfg['compiler'], src, "-d", d], capture_output=True, text=True, timeout=timeout)
        if comp.returncode:
            return {"status": "incorrect", "message": "Compilation failed", "compiler_output": comp.stderr}
        return _run_tests(["java", "-cp", d, "Main"], tests, timeout)
    finally:
        for f in [src, os.path.join(d, "Main.class")]:
            if os.path.exists(f): os.remove(f)


def _run_interpreted(code, lang, tests, timeout):
    """Run interpreted languages like Python and JavaScript."""
    cfg = COMPILERS[lang]
    fd, src = tempfile.mkstemp(suffix=cfg['extension'])
    os.close(fd)
    try:
        open(src, 'w', encoding='utf-8').write(code)
        return _run_tests([cfg['interpreter'], src], tests, timeout)
    finally:
        if os.path.exists(src): os.remove(src)


def _run_tests(cmd_base, tests, timeout):
    """Run the compiled/interpreted code against test cases."""
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
