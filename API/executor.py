import subprocess, os, tempfile
from config import COMPILERS, loadTest

def execute_code(code: str, lang: str, qid: str) -> dict:
    if lang not in COMPILERS:
        return {"status": "error", "message": f"Unsupported language: {lang}"}

    try:
        data = loadTest(qid)
        tests, timeout = data['test_pairs'], data['timeout']
    except Exception as e:
        return {"status": "error", "message": f"Error loading test cases: {e}"}

    if lang in ["c", "cpp"]:
        return _run_c_cpp(code, lang, tests, timeout)
    elif lang == "java":
        return _run_java(code, tests, timeout)
    else:
        return _run_interpreted(code, lang, tests, timeout)


# --- Helpers ---
def _run_c_cpp(code, lang, tests, timeout):
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
        return _run_tests([cfg['interpreter'], "-cp", d, "Main"], tests, timeout)
    finally:
        for f in [src, os.path.join(d, "Main.class")]:
            if os.path.exists(f): os.remove(f)


def _run_interpreted(code, lang, tests, timeout):
    cfg = COMPILERS[lang]
    fd, src = tempfile.mkstemp(suffix=cfg['extension'])
    os.close(fd)
    try:
        open(src, 'w', encoding='utf-8').write(code)
        return _run_tests([cfg['interpreter'], src], tests, timeout)
    finally:
        if os.path.exists(src): os.remove(src)


def _run_tests(cmd_base, tests, timeout):
    results, status, msg = [], "correct", "All test cases passed!"
    for t in tests:
        try:
            r = subprocess.run(cmd_base, input=t['input'], capture_output=True, text=True, timeout=timeout)
            out, err = r.stdout.strip(), r.stderr.strip()
            s, m = "passed", "Test passed."
            if r.returncode or out != t['expected_output'].strip():
                s, m, status, msg = "failed", f"Expected '{t['expected_output'].strip()}', got '{out}'", "incorrect", "Some test cases failed."
            results.append({"test_number": t['test_number'], "status": s, "message": m, "stdout": out, "stderr": err, "return_code": r.returncode})
        except subprocess.TimeoutExpired:
            results.append({"test_number": t['test_number'], "status": "failed", "message": f"Timeout {timeout}s", "stdout": "", "stderr": "Timeout", "return_code": -1})
            status, msg = "incorrect", "Some test cases timed out."
            break
    return {"status": status, "message": msg, "individual_test_results": results}
