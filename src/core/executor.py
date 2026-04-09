import subprocess
import os
import re
import tempfile
import resource
from .config import COMPILERS, validate_code
from .security.sanitizer import sanitize_code

MAX_MEMORY_MB = int(os.getenv("MAX_MEMORY_MB", 128))
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 1))
MAX_OPEN_FILES = int(os.getenv("MAX_OPEN_FILES", 64))
MAX_RUN_TIME = int(os.getenv("MAX_RUN_TIME", 5))

def _java_env():
    """Build a clean environment for Java subprocesses, removing JAVA_TOOL_OPTIONS to prevent noise."""
    env = os.environ.copy()
    env.pop("JAVA_TOOL_OPTIONS", None)
    env.pop("_JAVA_OPTIONS", None)
    return env

def _clean_java_stderr(stderr):
    """Strip JVM noise lines (Picked up JAVA_TOOL_OPTIONS, etc.) from stderr."""
    if not stderr:
        return stderr
    lines = stderr.splitlines(True)
    cleaned = [l for l in lines if not l.startswith("Picked up ")]
    return "".join(cleaned)

def _sandbox_preexec(timeout, skip_memory=False):
    """Set resource limits for child processes."""
    def _set_limits():
        # Limits for CPU time and file size
        resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_FILE_SIZE_MB * 1024 * 1024, MAX_FILE_SIZE_MB * 1024 * 1024))
        resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout))
        resource.setrlimit(resource.RLIMIT_NOFILE, (MAX_OPEN_FILES, MAX_OPEN_FILES))
        
        # Memory limit - skipped for Java as JVM manage its own heap/memory
        if not skip_memory:
            mem = MAX_MEMORY_MB * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
            
    return _set_limits

def execute_custom_code(code: str, lang: str) -> dict:
    """Execute raw code without test cases."""
    if lang not in COMPILERS:
        return {"status": "error", "stdout": "", "stderr": f"Unsupported language: {lang}"}

    scan = sanitize_code(lang, code)
    if not scan["safe"]:
        return {"status": "error", "stdout": "", "stderr": f"Code reject for execute due to {' and '.join(scan['violations'])}"}

    if lang in ["c", "cpp"]:
        return _run_c_cpp(code, lang)
    elif lang == "java":
        return _run_java(code)
    else:
        return _run_interpreted(code, lang)

def execute_code(code: str, lang: str, tests: list, timeout: int = None, templates: dict = None, rules: dict = None) -> dict:
    """Execute code against test cases with validation and templating."""
    if timeout is None:
        timeout = MAX_RUN_TIME
    if lang not in COMPILERS:
        return {"status": "error", "msg": f"Unsupported language: {lang}"}

    scan = sanitize_code(lang, code)
    if not scan["safe"]:
        return {"status": "error", "msg": f"Code reject for execute due to {' and '.join(scan['violations'])}"}

    if not validate_code(lang, code, rules or {}):
        return {"status": "error", "msg": "Code failed additional rules."}
    
    code_final = code
    template = (templates or {}).get(lang)
    if template and "__CODE_GOES_HERE__" in template:
        code_final = template.replace("__CODE_GOES_HERE__", code)

    if lang in ["c", "cpp"]:
        return _run_c_cpp(code_final, lang, tests, timeout)
    elif lang == "java":
        return _run_java(code_final, tests, timeout)
    else:
        return _run_interpreted(code_final, lang, tests, timeout)

def _run_c_cpp(code, lang, tests=None, timeout=None):
    """Compile and run C/C++ code."""
    if timeout is None:
        timeout = MAX_RUN_TIME
    cfg = COMPILERS[lang]
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, f"main{cfg['extension']}")
        exe = os.path.join(d, "main")
        
        with open(src, 'w') as f:
            f.write(code)
            
        try:
            comp = subprocess.run(
                [cfg['compiler'], src, "-o", exe], 
                capture_output=True, text=True, timeout=max(timeout, 10), cwd=d
            )
            if comp.returncode:
                return {"status": "incorrect", "msg": comp.stderr}
        except subprocess.TimeoutExpired:
            return {"status": "error", "msg": "Compilation timed out"}

        if tests is None:
            try:
                res = subprocess.run(
                    [exe], capture_output=True, text=True, 
                    timeout=timeout, cwd=d, preexec_fn=_sandbox_preexec(timeout)
                )
                return {"status": "success", "stdout": res.stdout, "stderr": res.stderr}
            except subprocess.TimeoutExpired:
                return {"status": "error", "msg": "Execution timed out"}
            
        return _run_tests([exe], tests, timeout, cwd=d)

def _run_java(code, tests=None, timeout=None):
    """Compile and run Java code."""
    if timeout is None:
        timeout = MAX_RUN_TIME
    # Strip comments to safely detect class name
    code_clean = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)
    
    match = re.search(r'(?:public\s+)?(?:(?:abstract|final|static|strictfp)\s+)*class\s+(\w+)', code_clean)
    if not match:
        return {"status": "error", "msg": "Java class not found."}
        
    class_name = match.group(1)
    
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, f"{class_name}.java")
        with open(src, 'w') as f:
            f.write(code)
            
        java_env = _java_env()
        try:
            # Compile with --release 11 for broad compatibility and fast startup
            comp = subprocess.run([
                "javac",
                "-J-XX:+TieredCompilation",
                "-J-XX:TieredStopAtLevel=1",
                "--release", "11",
                src, "-d", d
            ], capture_output=True, text=True, timeout=max(timeout, 10), cwd=d,
               env=java_env)
            if comp.returncode:
                return {"status": "incorrect", "msg": _clean_java_stderr(comp.stderr)}
        except subprocess.TimeoutExpired:
            return {"status": "error", "msg": "Compilation timed out"}

        # Optimized JVM startup arguments (removed deprecated -noverify)
        cmd = [
            "java",
            "-cp", d,
            f"-Xmx{MAX_MEMORY_MB}m",
            f"-Xms32m",
            "-XX:+TieredCompilation",
            "-XX:TieredStopAtLevel=1",
            class_name
        ]
        if tests is None:
            try:
                res = subprocess.run(
                    cmd, capture_output=True, text=True, 
                    timeout=timeout, cwd=d, env=java_env,
                    preexec_fn=_sandbox_preexec(timeout, skip_memory=True)
                )
                return {"status": "success", "stdout": res.stdout, "stderr": _clean_java_stderr(res.stderr)}
            except subprocess.TimeoutExpired:
                return {"status": "error", "msg": "Execution timed out"}
            
        return _run_tests(cmd, tests, timeout, cwd=d, skip_memory=True, env=java_env)

def _run_interpreted(code, lang, tests=None, timeout=None):
    """Run interpreted languages like Python/JS."""
    if timeout is None:
        timeout = MAX_RUN_TIME
    cfg = COMPILERS[lang]
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, f"main{cfg['extension']}")
        with open(src, 'w') as f:
            f.write(code)
            
        cmd = [cfg['interpreter'], src]
        if tests is None:
            try:
                res = subprocess.run(
                    cmd, capture_output=True, text=True, 
                    timeout=timeout, cwd=d, preexec_fn=_sandbox_preexec(timeout)
                )
                return {"status": "success", "stdout": res.stdout, "stderr": res.stderr}
            except subprocess.TimeoutExpired:
                return {"status": "error", "msg": "Execution timed out"}
            
        return _run_tests(cmd, tests, timeout, cwd=d)

def _run_tests(cmd_base, tests, timeout, cwd=None, skip_memory=False, env=None):
    """Run code against multiple test cases."""
    results, status, msg = [], "correct", "All tests passed!"
    for t in tests:
        try:
            run_kwargs = dict(
                input=t['input'], capture_output=True,
                text=True, timeout=timeout, cwd=cwd,
                preexec_fn=_sandbox_preexec(timeout, skip_memory)
            )
            if env:
                run_kwargs['env'] = env
            r = subprocess.run(cmd_base, **run_kwargs)
            out, err = r.stdout.strip(), r.stderr.strip()
            
            # Simple correctness check
            is_correct = not r.returncode and out == t['expected_output'].strip()
            s = "passed" if is_correct else "failed"
            m = "Test passed." if is_correct else f"Expected '{t['expected_output'].strip()}', got '{out}'"
            
            if s == "failed":
                status, msg = "incorrect", "Some tests failed."
                
            results.append({"case": int(t['test_number']), "status": s, "msg": m, "stdout": out, "stderr": err})
            
        except subprocess.TimeoutExpired:
            results.append({"case": int(t['test_number']), "status": "failed", "msg": "Timeout", "stdout": "", "stderr": "Timeout"})
            status, msg = "timeout", "Time Limit Exceeded"
            break
            
    return {"status": status, "msg": msg, "tests": results}
